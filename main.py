#!/usr/bin/env python3
"""
Flub Agent - Simple single-agent travel planning assistant

Main entry point for the Flub Agent.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.simple_agent import SimpleFlubAgent
from dotenv import load_dotenv

load_dotenv()


async def main():
    """Main entry point."""

    # Create the simple agent (no MCP needed!)
    agent = SimpleFlubAgent()

    print("=" * 70)
    print("Flub Agent - Travel Planning Assistant")
    print("=" * 70)
    print()

    # Example query - with tomorrow's date
    from datetime import datetime, timedelta
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    query = f"What is the best flight from EWR to LAX on {tomorrow}?"

    print(f"Query: {query}\n")
    print("Processing...\n")

    # Note: SimpleFlubAgent.process() is not async
    response = agent.process(query)

    print("=" * 70)
    print("Response:")
    print("=" * 70)
    print(response)
    print()


if __name__ == "__main__":
    asyncio.run(main())
