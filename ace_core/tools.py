"""
ACE Tools - Thinking, Search, Deep Research
"""
from typing import List, Dict
from ace_types import Result, Success, Failure
import asyncio
import aiohttp

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
    """Search through context, knowledge and web (like OpenAI)"""
    
    def __init__(self, enable_web_search: bool = False):
        self.enable_web_search = enable_web_search
    
    def search_context(self, query: str, context_bullets: List) -> List[Dict]:
        """Search in local context"""
        query_words = set(query.lower().split())
        results = []
        
        for bullet in context_bullets:
            bullet_words = set(bullet.content.lower().split())
            overlap = len(query_words.intersection(bullet_words))
            if overlap > 0:
                results.append({
                    'content': bullet.content,
                    'relevance': overlap,
                    'tags': bullet.tags,
                    'source': 'context'
                })
        
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:5]
    
    async def search_web(self, query: str) -> List[Dict]:
        """Search web using DuckDuckGo (free alternative to OpenAI search)"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = []
                        
                        if data.get('Abstract'):
                            results.append({
                                'content': data['Abstract'],
                                'url': data.get('AbstractURL', ''),
                                'source': 'web',
                                'relevance': 10
                            })
                        
                        for topic in data.get('RelatedTopics', [])[:3]:
                            if isinstance(topic, dict) and topic.get('Text'):
                                results.append({
                                    'content': topic['Text'],
                                    'url': topic.get('FirstURL', ''),
                                    'source': 'web',
                                    'relevance': 5
                                })
                        
                        return results
        except Exception:
            pass
        return []
    
    async def search(self, query: str, context_bullets: List) -> List[Dict]:
        """Unified search: context + web (like OpenAI)"""
        context_results = self.search_context(query, context_bullets)
        
        web_results = []
        if self.enable_web_search:
            web_results = await self.search_web(query)
        
        all_results = context_results + web_results
        all_results.sort(key=lambda x: x['relevance'], reverse=True)
        return all_results[:5]

class DeepResearchTool:
    """Multi-step research with synthesis (like OpenAI deep research)"""
    
    def __init__(self, enable_web_search: bool = False):
        self.enable_web_search = enable_web_search
    
    async def research(self, topic: str, ollama_client, context_bullets: List) -> Result[str, str]:
        """Conduct deep research with web search"""
        output = []
        
        output.append("🔍 Step 1: Searching knowledge sources...")
        search_tool = SearchTool(enable_web_search=self.enable_web_search)
        existing = await search_tool.search(topic, context_bullets)
        
        if existing:
            output.append(f"   Found {len(existing)} relevant sources")
            for i, result in enumerate(existing[:3], 1):
                source_type = "🌐 Web" if result['source'] == 'web' else "📚 Context"
                output.append(f"   {i}. {source_type}: {result['content'][:80]}...")
        
        output.append("\n🤔 Step 2: Generating research questions...")
        questions_prompt = f"""Research topic: {topic}

Based on available information, generate 3 specific research questions to explore:"""
        
        questions_result = await ollama_client.generate(questions_prompt)
        if isinstance(questions_result, Failure):
            return Failure("\n".join(output) + f"\n\n❌ Error: {questions_result.error}")
        
        questions = [q.strip() for q in questions_result.value.split('\n')[:3] if q.strip()]
        for i, q in enumerate(questions, 1):
            output.append(f"   Q{i}: {q}")
        
        output.append("\n💡 Step 3: Researching answers...")
        answers = []
        for i, question in enumerate(questions, 1):
            q_results = await search_tool.search(question, context_bullets)
            context_info = "\n".join([r['content'][:150] for r in q_results[:2]])
            
            answer_prompt = f"""Question: {question}

Relevant information:
{context_info}

Provide detailed answer:"""
            answer_result = await ollama_client.generate(answer_prompt)
            if isinstance(answer_result, Success):
                output.append(f"   ✓ Answered Q{i}")
                answers.append(f"Q{i}: {question}\nA{i}: {answer_result.value}")
        
        output.append("\n📝 Step 4: Synthesizing comprehensive report...\n")
        
        sources_text = "\n".join([f"- {e['content'][:200]}" for e in existing[:3]])
        synthesis_prompt = f"""Research topic: {topic}

Sources consulted:
{sources_text}

Research findings:
{chr(10).join(answers)}

Synthesize a comprehensive, well-structured report with:
1. Executive summary
2. Key findings
3. Detailed analysis
4. Conclusion

Report:"""
        
        synthesis_result = await ollama_client.generate(synthesis_prompt)
        
        if isinstance(synthesis_result, Success):
            final_output = "\n".join(output) + "\n" + "="*60 + "\n" + synthesis_result.value
            return Success(final_output)
        else:
            return Failure("\n".join(output) + f"\n\n❌ Synthesis error: {synthesis_result.error}")
