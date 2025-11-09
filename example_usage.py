#!/usr/bin/env python3
"""
Example usage of the simplified single-agent Flub Agent architecture.

This demonstrates how to use the FlubAgent with your MCP servers.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import FlubAgent, process_query
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# STEP 1: Configure your MCP servers
# ============================================================================

# Replace this with your actual MCP server configurations
YOUR_MCP_SERVERS = {
    # Example: Weather MCP server
    # "weather": {
    #     "command": "npx",
    #     "args": ["-y", "@modelcontextprotocol/server-weather"],
    #     "env": {}
    # },

    # Example: Your flight MCP server
    # "flights": {
    #     "command": "python",
    #     "args": ["/path/to/your/flight_mcp_server.py"],
    #     "env": {"API_KEY": "your_key"}
    # },

    # Add more MCP servers as needed...
}

# Optional: Specify which tools are allowed (leave empty list to allow all)
ALLOWED_TOOLS = [
    # "mcp__weather__get_forecast",
    # "mcp__flights__search_flights",
    # Add your tool names here...
]


# ============================================================================
# Example 1: Simple one-off query
# ============================================================================

async def example_simple_query():
    """Example of a simple one-off query without conversation history."""
    print("=" * 70)
    print("Example 1: Simple Query")
    print("=" * 70)

    query = "What's the weather like in San Francisco tomorrow?"

    response = await process_query(
        message=query,
        mcp_servers=YOUR_MCP_SERVERS,
        allowed_tools=ALLOWED_TOOLS
    )

    print(f"\nQuery: {query}")
    print(f"\nResponse:\n{response}\n")


# ============================================================================
# Example 2: Multi-turn conversation with context
# ============================================================================

async def example_conversation():
    """Example of a multi-turn conversation that maintains context."""
    print("=" * 70)
    print("Example 2: Multi-turn Conversation")
    print("=" * 70)

    # Create an agent instance (maintains conversation history)
    agent = FlubAgent(
        mcp_servers=YOUR_MCP_SERVERS,
        allowed_tools=ALLOWED_TOOLS
    )

    # First message
    response1 = await agent.process("I want to fly from NYC to Miami next week")
    print(f"\nUser: I want to fly from NYC to Miami next week")
    print(f"Agent: {response1}\n")

    # Second message (uses context from first message)
    response2 = await agent.process("What's the weather like on the sunny days?")
    print(f"User: What's the weather like on the sunny days?")
    print(f"Agent: {response2}\n")

    # Third message (continues to use full context)
    response3 = await agent.process("Are there any flight disruptions?")
    print(f"User: Are there any flight disruptions?")
    print(f"Agent: {response3}\n")

    # You can clear history if starting a new topic
    agent.clear_history()
    print("(Conversation history cleared)")


# ============================================================================
# Example 3: Streaming response
# ============================================================================

async def example_streaming():
    """Example of streaming a response as it's generated."""
    print("=" * 70)
    print("Example 3: Streaming Response")
    print("=" * 70)

    agent = FlubAgent(
        mcp_servers=YOUR_MCP_SERVERS,
        allowed_tools=ALLOWED_TOOLS
    )

    query = "Find me the best flights from Boston to Seattle next month when it's sunny"
    print(f"\nQuery: {query}\n")
    print("Response (streaming):")

    # Stream the response
    async for chunk in agent.stream(query):
        print(chunk, end='', flush=True)

    print("\n")


# ============================================================================
# Example 4: Complex travel planning query
# ============================================================================

async def example_complex_query():
    """Example of a complex travel planning query that uses multiple tools."""
    print("=" * 70)
    print("Example 4: Complex Travel Planning")
    print("=" * 70)

    agent = FlubAgent(
        mcp_servers=YOUR_MCP_SERVERS,
        allowed_tools=ALLOWED_TOOLS
    )

    query = """I want to plan a trip from New York to San Francisco next week.
    I prefer to fly on days with clear weather.
    Check if there are any flight disruptions I should know about.
    What are my best options?"""

    print(f"\nQuery: {query}\n")
    print("Processing... (this may take a moment as the agent uses multiple tools)\n")

    response = await agent.process(query)
    print(f"Response:\n{response}\n")


# ============================================================================
# Main function - run examples
# ============================================================================

async def main():
    """Run all examples."""

    # Check if MCP servers are configured
    if not YOUR_MCP_SERVERS:
        print("=" * 70)
        print("⚠️  No MCP servers configured!")
        print("=" * 70)
        print("\nPlease configure your MCP servers in YOUR_MCP_SERVERS")
        print("See example_mcp_config.py for configuration examples.")
        print("\nThe agent will still work but won't have access to tools.")
        print("=" * 70)
        print()

    # Uncomment the examples you want to run:

    # await example_simple_query()
    # await example_conversation()
    # await example_streaming()
    # await example_complex_query()

    # Default: run a simple test
    print("=" * 70)
    print("Flub Agent - Simple Architecture Test")
    print("=" * 70)

    agent = FlubAgent(
        mcp_servers=YOUR_MCP_SERVERS,
        allowed_tools=ALLOWED_TOOLS
    )

    test_query = "I want to fly from NYC to Miami next week. What are my options?"
    print(f"\nTest Query: {test_query}\n")
    print("Processing...\n")

    response = await agent.process(test_query)
    print(f"Response:\n{response}\n")

    print("=" * 70)
    print("✓ Single-agent architecture is working!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Configure your MCP servers in YOUR_MCP_SERVERS")
    print("2. Add your tool names to ALLOWED_TOOLS (optional)")
    print("3. Run this script again to test with real tools")
    print("\nSee example_mcp_config.py for MCP configuration examples.")


if __name__ == "__main__":
    asyncio.run(main())
