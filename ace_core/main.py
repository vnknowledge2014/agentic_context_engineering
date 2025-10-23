#!/usr/bin/env python3
"""
ACE System - Main Entry Point
Functional + Railway-Oriented Programming
"""
import asyncio
import sys
from ace_types import OllamaConfig, Success, Failure
from ace import ACEFramework
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
    print("\nCommands: 'stats', 'help', 'exit'")
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
                print("  - 'exit' - Exit system")
                continue
            
            # Process query with streaming
            print(f"\n🤖 ACE:")
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
