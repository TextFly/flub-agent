"""
Simple Agent without MCP

Uses Claude API directly with function calling to access flight search tools.
"""

import os
import json
from typing import Dict, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Import our tools (after load_dotenv)
from .tools import search_flights, find_best_price


class SimpleFlubAgent:
    """
    Simple Claude agent that uses direct function calling instead of MCP.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Simple Flub Agent.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set ANTHROPIC_API_KEY in .env")

        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history = []

        # Define tools for Claude
        self.tools = [
            {
                "name": "search_flights",
                "description": "Search for flights between two airports on a specific date. Returns a list of available flights with pricing, duration, and other details.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Flight date in YYYY-MM-DD format (e.g., '2025-11-10')"
                        },
                        "from_airport": {
                            "type": "string",
                            "description": "Departure airport code (e.g., 'EWR', 'JFK', 'LAX')"
                        },
                        "to_airport": {
                            "type": "string",
                            "description": "Arrival airport code (e.g., 'LAX', 'SFO', 'LHR')"
                        },
                        "adults": {
                            "type": "integer",
                            "description": "Number of adult passengers",
                            "default": 1
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of flights to return",
                            "default": 10
                        }
                    },
                    "required": ["date", "from_airport", "to_airport"]
                }
            },
            {
                "name": "find_best_price",
                "description": "Find the cheapest flight option for a specific route and date. Returns the single cheapest flight with price comparisons.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Flight date in YYYY-MM-DD format"
                        },
                        "from_airport": {
                            "type": "string",
                            "description": "Departure airport code"
                        },
                        "to_airport": {
                            "type": "string",
                            "description": "Arrival airport code"
                        },
                        "adults": {
                            "type": "integer",
                            "description": "Number of adult passengers",
                            "default": 1
                        }
                    },
                    "required": ["date", "from_airport", "to_airport"]
                }
            }
        ]

    def _call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Call the appropriate tool function."""
        if tool_name == "search_flights":
            return search_flights(**tool_input)
        elif tool_name == "find_best_price":
            return find_best_price(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def process(self, message: str) -> str:
        """
        Process a user message and return a response.

        Args:
            message: The user's message/query

        Returns:
            The agent's response string
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        try:
            # Call Claude with tools
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system="""You are Flub, an intelligent travel planning assistant with access to flight search tools.

Your capabilities:
- Search for flights between airports
- Find the best prices
- Provide travel recommendations

When users ask about flights:
1. Use the search_flights or find_best_price tools
2. Present the results clearly and concisely
3. Highlight the best options based on price, duration, and convenience

Always use airport codes (like EWR, LAX, JFK) when searching for flights.""",
                messages=self.conversation_history,
                tools=self.tools
            )

            # Process the response
            while response.stop_reason == "tool_use":
                # Extract tool uses
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_use_id = block.id

                        print(f"[Tool Call] {tool_name} with {tool_input}")

                        # Call the tool
                        result = self._call_tool(tool_name, tool_input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(result)
                        })

                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Add tool results to history
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue the conversation with tool results
                response = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4096,
                    messages=self.conversation_history,
                    tools=self.tools
                )

            # Extract final text response
            final_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    final_text += block.text

            # Add final response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": final_text
            })

            return final_text

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"Error processing request: {str(e)}"
            return error_msg

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
