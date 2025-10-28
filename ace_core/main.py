#!/usr/bin/env python3
"""
ACE System - Main Entry Point
Functional + Railway-Oriented Programming
"""
import asyncio
import sys
from ace_types import OllamaConfig, Success, Failure
from ace import ACEFramework
from tools import ThinkingTool, SearchTool, DeepResearchTool
from imperative_shell import log_info, log_success, log_error

async def demo_mode(ace: ACEFramework) -> None:
    """Demo mode with predefined queries"""
    log_info("ACE Demo Mode - Agentic Context Engineering")
    
    queries = [
        "Agentic Context Engineering là gì?",
        "Viết Python function tính fibonacci",
        "Phân tích ưu nhược điểm của ACE framework"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print('='*60)
        
        print(f"\n🤖 Response:")
        async for chunk in ace.process_query_stream(query):
            print(chunk, end='', flush=True)
        print()  # New line
        
        # Show stats
        stats = ace.get_context_stats()
        print(f"\n📈 Context: {stats['total_bullets']} bullets, "
              f"version {stats['version']}\n")

async def interactive_mode(ace: ACEFramework) -> None:
    """Interactive chat mode"""
    log_info("ACE Interactive Mode")
    thinking_tool = ThinkingTool()
    web_search_enabled = False
    search_tool = SearchTool(enable_web_search=web_search_enabled)
    research_tool = DeepResearchTool(enable_web_search=web_search_enabled)
    thinking_mode = False
    print("\nCommands: 'stats', 'help', 'exit', '/think', '/search', '/research', '/thinking on|off', '/web on|off'")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                log_info("Goodbye!")
                break
            
            if user_input.lower() == 'stats':
                stats = ace.get_context_stats()
                print(f"\n📊 Context Statistics:")
                print(f"  Total bullets: {stats['total_bullets']}")
                print(f"  Helpful bullets: {stats['helpful_bullets']}")
                print(f"  Version: {stats['version']}")
                print(f"  Avg helpfulness: {stats['avg_helpfulness']:.2f}")
                continue
            
            if user_input.lower() == 'help':
                print("\n📖 ACE Framework Help")
                print("  - Ask any question naturally")
                print("  - 'stats' - Show context statistics")
                print("  - '/think <query>' - Deep thinking mode")
                print("  - '/search <query>' - Search in context/web")
                print("  - '/research <topic>' - Deep research mode")
                print("  - '/thinking on|off' - Toggle native thinking mode")
                print("  - '/web on|off' - Toggle web search (like OpenAI)")
                print("  - 'exit' - Exit system")
                continue
            
            if user_input.lower().startswith('/thinking '):
                mode = user_input[10:].strip().lower()
                if mode == 'on':
                    thinking_mode = True
                    log_success("Native thinking mode enabled")
                elif mode == 'off':
                    thinking_mode = False
                    log_success("Native thinking mode disabled")
                else:
                    log_error("Use: /thinking on or /thinking off")
                continue
            
            if user_input.lower().startswith('/web '):
                mode = user_input[5:].strip().lower()
                if mode == 'on':
                    web_search_enabled = True
                    search_tool = SearchTool(enable_web_search=True)
                    research_tool = DeepResearchTool(enable_web_search=True)
                    log_success("🌐 Web search enabled (like OpenAI)")
                elif mode == 'off':
                    web_search_enabled = False
                    search_tool = SearchTool(enable_web_search=False)
                    research_tool = DeepResearchTool(enable_web_search=False)
                    log_success("Web search disabled")
                else:
                    log_error("Use: /web on or /web off")
                continue
            
            if user_input.startswith('/think '):
                query = user_input[7:]
                print(f"\n🧠 Thinking:")
                result = await thinking_tool.think(query, ace.client)
                match result:
                    case Success(response):
                        print(response)
                    case Failure(error):
                        log_error(f"Error: {error}")
                continue
            
            if user_input.startswith('/search '):
                query = user_input[8:]
                context = ace.curator.get_context()
                print(f"\n🔍 Searching...")
                results = await search_tool.search(query, list(context.bullets.values()))
                if not results:
                    print("No results found.")
                else:
                    for i, r in enumerate(results, 1):
                        source = "🌐" if r['source'] == 'web' else "📚"
                        print(f"{i}. {source} {r['content'][:100]}...")
                        if 'url' in r and r['url']:
                            print(f"   🔗 {r['url']}")
                continue
            
            if user_input.startswith('/research '):
                topic = user_input[10:]
                print(f"\n🔬 Researching:")
                context = ace.curator.get_context()
                result = await research_tool.research(topic, ace.client, list(context.bullets.values()))
                match result:
                    case Success(response):
                        print(response)
                    case Failure(error):
                        log_error(f"Error: {error}")
                continue
            
            # Process query with streaming
            print(f"\n🤖 ACE:")
            if thinking_mode:
                async for result in ace.client.generate_stream(user_input, enable_thinking=True):
                    match result:
                        case Success(chunk):
                            print(chunk, end='', flush=True)
                        case Failure(error):
                            log_error(f"Error: {error}")
                            break
            else:
                async for chunk in ace.process_query_stream(user_input):
                    print(chunk, end='', flush=True)
            print()  # New line
            
            # Show stats
            stats = ace.get_context_stats()
            if stats['total_bullets'] > 0:
                print(f"💡 Context: {stats['total_bullets']} bullets learned")
        
        except KeyboardInterrupt:
            log_info("\nGoodbye!")
            break
        except Exception as e:
            log_error(f"Unexpected error: {e}")

async def main():
    """Main entry point"""
    # Parse arguments
    mode = "interactive"
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        mode = "demo"
    
    # Create ACE framework
    config = OllamaConfig(
        url="http://localhost:11434",
        model="qwen2.5-coder:1.5b",
        temperature=0.7,
        max_tokens=256,
        context_window=2048
    )
    ace = ACEFramework(config)
    
    # Initialize
    init_result = await ace.initialize()
    match init_result:
        case Failure(error):
            log_error(f"Failed to initialize: {error}")
            return
        case Success(_):
            pass
    
    try:
        # Run mode
        if mode == "demo":
            await demo_mode(ace)
        else:
            await interactive_mode(ace)
    finally:
        # Shutdown
        await ace.shutdown()
        log_success("ACE Framework shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
