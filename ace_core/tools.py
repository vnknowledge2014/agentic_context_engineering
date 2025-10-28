"""
ACE Tools - Thinking, Search, Deep Research
"""
from typing import List, Dict
from ace_types import Result, Success, Failure
import asyncio

class ThinkingTool:
    """Extended reasoning with step-by-step thinking"""
    
    async def think(self, query: str, ollama_client) -> Result[str, str]:
        """Generate deep thinking process with native thinking support"""
        prompt = f"""Think deeply about this query step by step:

Query: {query}

Provide detailed reasoning:
1. Break down the problem
2. Consider multiple approaches
3. Analyze pros and cons
4. Reach conclusion

Thinking process:"""
        
        return await ollama_client.generate(prompt, enable_thinking=True)

class SearchTool:
    """Search through context and knowledge"""
    
    def search(self, query: str, context_bullets: List) -> List[Dict]:
        """Search relevant information"""
        query_words = set(query.lower().split())
        results = []
        
        for bullet in context_bullets:
            bullet_words = set(bullet.content.lower().split())
            overlap = len(query_words.intersection(bullet_words))
            if overlap > 0:
                results.append({
                    'content': bullet.content,
                    'relevance': overlap,
                    'tags': bullet.tags
                })
        
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:5]

class DeepResearchTool:
    """Multi-step research with synthesis"""
    
    async def research(self, topic: str, ollama_client, context_bullets: List) -> Result[str, str]:
        """Conduct deep research"""
        # Step 1: Search existing knowledge
        search_tool = SearchTool()
        existing = search_tool.search(topic, context_bullets)
        
        # Step 2: Generate research questions
        questions_prompt = f"""Research topic: {topic}

Generate 3 key research questions to explore:"""
        
        questions_result = await ollama_client.generate(questions_prompt)
        if isinstance(questions_result, Failure):
            return questions_result
        
        # Step 3: Answer each question
        answers = []
        for i, line in enumerate(questions_result.value.split('\n')[:3], 1):
            if line.strip():
                answer_prompt = f"""Question: {line.strip()}

Provide detailed answer:"""
                answer_result = await ollama_client.generate(answer_prompt)
                if isinstance(answer_result, Success):
                    answers.append(f"Q{i}: {line.strip()}\nA{i}: {answer_result.value}")
        
        # Step 4: Synthesize
        synthesis_prompt = f"""Research topic: {topic}

Existing knowledge:
{chr(10).join([e['content'][:100] for e in existing[:3]])}

Research findings:
{chr(10).join(answers)}

Synthesize comprehensive answer:"""
        
        return await ollama_client.generate(synthesis_prompt)
