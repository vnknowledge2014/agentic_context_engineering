"""
ACE Framework - Agentic Context Engineering
Functional implementation following ICLR 2026 paper
"""
from typing import List, Tuple
from ace_types import (
    Result, Success, Failure, ContextState, Trajectory, Insight, 
    DeltaUpdate, ContextBullet, OllamaConfig
)
from functional_core import (
    get_relevant_bullets, parse_trajectory_response, parse_insights_response,
    insights_to_delta, merge_delta, prune_low_quality_bullets, 
    limit_context_size, build_context_prompt, update_bullet_feedback
)
from imperative_shell import OllamaClient, bind, map_result, log_success, log_error

class ACEGenerator:
    """Generator: Produces reasoning trajectories (pure + I/O)"""
    
    def __init__(self, client: OllamaClient):
        self.client = client
    
    async def generate_trajectory(
        self,
        query: str,
        context: ContextState
    ) -> Result[Trajectory, str]:
        """Generate reasoning trajectory"""
        bullets = get_relevant_bullets(context, query)
        context_text = build_context_prompt(bullets)
        
        prompt = f"""{query}

Provide a brief answer in this format:
STEPS: [step1; step2; step3]
OUTCOME: your answer here
SUCCESS: true
USED_BULLETS: []"""
        
        result = await self.client.generate(prompt)
        return map_result(result, lambda r: parse_trajectory_response(query, r))

class ACEReflector:
    """Reflector: Distills insights from trajectories"""
    
    def __init__(self, client: OllamaClient):
        self.client = client
    
    async def reflect(
        self,
        trajectory: Trajectory
    ) -> Result[List[Insight], str]:
        """Reflect on trajectory and extract insights"""
        steps_text = '; '.join(s.description for s in trajectory.steps[:3])
        prompt = f"""Based on this task: {trajectory.query}
Result: {trajectory.outcome}

Provide one key insight:
[Content: key learning from this task; Type: strategy; Confidence: 0.8]"""
        
        result = await self.client.generate(prompt)
        return map_result(
            result,
            lambda r: parse_insights_response(r, trajectory.query)
        )

class ACECurator:
    """Curator: Integrates insights into context"""
    
    def __init__(self):
        self.context = ContextState(bullets={})
    
    def create_delta(self, insights: List[Insight]) -> DeltaUpdate:
        """Create delta update from insights"""
        return insights_to_delta(insights)
    
    def apply_delta(self, delta: DeltaUpdate) -> ContextState:
        """Apply delta to context"""
        self.context = merge_delta(self.context, delta)
        return self.context
    
    def update_feedback(self, bullet_ids: List[str], success: bool) -> None:
        """Update bullet feedback"""
        new_bullets = dict(self.context.bullets)
        for bullet_id in bullet_ids:
            if bullet_id in new_bullets:
                new_bullets[bullet_id] = update_bullet_feedback(
                    new_bullets[bullet_id],
                    success
                )
        self.context = ContextState(
            bullets=new_bullets,
            version=self.context.version + 1
        )
    
    def grow_and_refine(self, max_size: int = 1000) -> ContextState:
        """Apply grow-and-refine mechanism"""
        self.context = prune_low_quality_bullets(self.context)
        self.context = limit_context_size(self.context, max_size)
        return self.context
    
    def get_context(self) -> ContextState:
        """Get current context"""
        return self.context

class ACEFramework:
    """Main ACE Framework coordinating all components"""
    
    def __init__(self, config: OllamaConfig = OllamaConfig()):
        self.config = config
        self.client = OllamaClient(config)
        self.generator = ACEGenerator(self.client)
        self.reflector = ACEReflector(self.client)
        self.curator = ACECurator()
    
    async def initialize(self) -> Result[bool, str]:
        """Initialize framework"""
        result = await self.client.initialize()
        match result:
            case Success(_):
                log_success("ACE Framework initialized")
                return Success(True)
            case Failure(error):
                log_error(f"Initialization failed: {error}")
                return Failure(error)
    
    async def process_query_stream(self, query: str):
        """Process query with streaming response"""
        context = self.curator.get_context()
        bullets = get_relevant_bullets(context, query)
        context_text = build_context_prompt(bullets)
        
        prompt = f"""{query}

Provide a brief answer in this format:
STEPS: [step1; step2; step3]
OUTCOME: your answer here
SUCCESS: true
USED_BULLETS: []"""
        
        full_response = ""
        async for result in self.client.generate_stream(prompt):
            match result:
                case Success(chunk):
                    full_response += chunk
                    yield chunk
                case Failure(error):
                    yield f"\n❌ Error: {error}"
                    return
        
        # Parse and learn from response
        trajectory = parse_trajectory_response(query, full_response)
        insights_result = await self.reflector.reflect(trajectory)
        
        match insights_result:
            case Success(insights):
                delta = self.curator.create_delta(insights)
                self.curator.apply_delta(delta)
                self.curator.update_feedback(list(trajectory.used_bullets), trajectory.success)
            case Failure(_):
                pass
    
    async def process_query(
        self,
        query: str,
        feedback: str | None = None
    ) -> Result[Tuple[str, DeltaUpdate], str]:
        """Process query through ACE pipeline"""
        # Step 1: Generate trajectory
        traj_result = await self.generator.generate_trajectory(
            query,
            self.curator.get_context()
        )
        
        match traj_result:
            case Failure(error):
                return Failure(f"Generation failed: {error}")
            case Success(trajectory):
                pass
        
        # Add feedback if provided
        if feedback:
            trajectory = Trajectory(
                query=trajectory.query,
                steps=trajectory.steps,
                outcome=trajectory.outcome,
                success=trajectory.success,
                used_bullets=trajectory.used_bullets,
                feedback=feedback
            )
        
        # Step 2: Reflect on trajectory
        insights_result = await self.reflector.reflect(trajectory)
        
        match insights_result:
            case Failure(error):
                return Failure(f"Reflection failed: {error}")
            case Success(insights):
                pass
        
        # Step 3: Create and apply delta
        delta = self.curator.create_delta(insights)
        self.curator.apply_delta(delta)
        
        # Update feedback for used bullets
        self.curator.update_feedback(list(trajectory.used_bullets), trajectory.success)
        
        # Build response
        steps_text = '; '.join(s.description for s in trajectory.steps)
        response = f"""Trajectory: {steps_text}

Outcome: {trajectory.outcome}
Success: {trajectory.success}
New insights: {len(delta.bullets)}"""
        
        return Success((response, delta))
    
    async def adaptive_learning(
        self,
        queries: List[str],
        max_iterations: int = 3
    ) -> Result[dict, str]:
        """Run adaptive learning cycle"""
        results = {"iterations": [], "context_stats": []}
        
        for iteration in range(max_iterations):
            iteration_results = []
            
            for query in queries:
                result = await self.process_query(query)
                match result:
                    case Success((response, delta)):
                        iteration_results.append({
                            "query": query,
                            "response": response,
                            "new_bullets": len(delta.bullets)
                        })
                    case Failure(error):
                        iteration_results.append({
                            "query": query,
                            "error": error
                        })
            
            # Apply grow-and-refine
            self.curator.grow_and_refine()
            
            context = self.curator.get_context()
            results["iterations"].append({
                "iteration": iteration + 1,
                "results": iteration_results
            })
            results["context_stats"].append({
                "total_bullets": len(context.bullets),
                "version": context.version
            })
        
        return Success(results)
    
    def get_context_stats(self) -> dict:
        """Get context statistics"""
        context = self.curator.get_context()
        helpful = sum(
            1 for b in context.bullets.values()
            if b.helpful_count > b.harmful_count
        )
        
        return {
            "total_bullets": len(context.bullets),
            "helpful_bullets": helpful,
            "version": context.version,
            "avg_helpfulness": (
                sum(b.helpful_count for b in context.bullets.values()) / 
                max(len(context.bullets), 1)
            )
        }
    
    async def shutdown(self) -> Result[None, str]:
        """Shutdown framework"""
        return await self.client.shutdown()
