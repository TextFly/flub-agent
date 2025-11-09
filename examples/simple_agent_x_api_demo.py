"""
Demo script showing SimpleFlubAgent with X API integration

This demonstrates how the agent can now use both flight search and X API tools.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from simple_agent import SimpleFlubAgent


def demo_x_api_integration():
    """Demo the X API integration with simple agent"""
    print("=" * 80)
    print("SimpleFlubAgent with X API Integration Demo")
    print("=" * 80)
    print("\nNote: Make sure ANTHROPIC_API_KEY and X_BEARER_TOKEN are set in .env\n")
    
    # Initialize agent
    agent = SimpleFlubAgent()
    
    # Example queries that use X API
    queries = [
        "What's trending on X/Twitter right now?",
        "Check recent tweets from @united about flight delays",
        "Search X for any reports about airport security issues today",
        "Find me flights from EWR to LAX on 2025-11-20 and also check if there are any travel disruptions being reported on X",
    ]
    
    print("\nAvailable demo queries:")
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")
    
    print("\nChoose a query (1-4) or type 'custom' for your own query:")
    choice = input("> ").strip()
    
    if choice.lower() == "custom":
        query = input("\nEnter your query: ").strip()
    elif choice.isdigit() and 1 <= int(choice) <= len(queries):
        query = queries[int(choice) - 1]
    else:
        print("Invalid choice. Using first query.")
        query = queries[0]
    
    print("\n" + "=" * 80)
    print(f"User: {query}")
    print("=" * 80)
    print("\nAgent is processing (this may take a moment)...\n")
    
    try:
        response = agent.process(query)
        print("-" * 80)
        print("Agent Response:")
        print("-" * 80)
        print(response)
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def interactive_mode():
    """Run in interactive mode"""
    print("=" * 80)
    print("SimpleFlubAgent - Interactive Mode")
    print("=" * 80)
    print("\nAgent has access to:")
    print("  • Flight search tools")
    print("  • X/Twitter API (search users, topics, trends, analyze sentiment)")
    print("\nType 'quit' or 'exit' to end the conversation")
    print("Type 'clear' to clear conversation history\n")
    
    agent = SimpleFlubAgent()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\nGoodbye! 👋")
                break
            
            if user_input.lower() == 'clear':
                agent.clear_history()
                print("\n✓ Conversation history cleared")
                continue
            
            print("\nAgent: ", end="", flush=True)
            response = agent.process(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        demo_x_api_integration()


if __name__ == "__main__":
    main()

