"""
Simple Agent without MCP

Uses Claude API directly with function calling to access flight search tools.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Import our tools (after load_dotenv)
from .tools import (
    search_flights, 
    find_best_price,
    search_user_tweets,
    search_trending_topics,
    search_topics,
    analyze_tweet_sentiment,
    check_weather
)


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
            },
            {
                "name": "search_user_tweets",
                "description": "Search through the most recent tweets of a specific X/Twitter user. Returns user info and their recent tweets with engagement metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "The X/Twitter username without @ symbol (e.g., 'elonmusk', 'united', 'delta')"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of tweets to return (default: 10, max: 100)",
                            "default": 10
                        }
                    },
                    "required": ["username"]
                }
            },
            {
                "name": "search_topics",
                "description": "Search for tweets about specific topics or keywords on X/Twitter. Returns tweets matching the query with author info and engagement metrics. Useful for monitoring travel disruptions, delays, incidents.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query or topic to search for (e.g., 'flight delays LAX', 'airport security JFK', 'United Airlines delays')"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of tweets to return (default: 10, max: 100)",
                            "default": 10
                        },
                        "sort_order": {
                            "type": "string",
                            "description": "Sort order: 'recency' for newest first or 'relevancy' for most relevant",
                            "enum": ["recency", "relevancy"],
                            "default": "recency"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "analyze_tweet_sentiment",
                "description": "Analyze engagement metrics and sentiment from tweet search results. Takes the output from search_topics or search_user_tweets and provides aggregated statistics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tweets_data": {
                            "type": "object",
                            "description": "The complete output from search_topics or search_user_tweets functions"
                        }
                    },
                    "required": ["tweets_data"]
                }
            },
            {
                "name": "check_weather",
                "description": "Get current weather information for a specific city. Returns temperature, conditions, and other weather data.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city to check weather for (e.g., 'London', 'New York', 'Tokyo')"
                        }
                    },
                    "required": ["city"]
                }
            }
        ]

    def _call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Call the appropriate tool function."""
        if tool_name == "search_flights":
            return search_flights(**tool_input)
        elif tool_name == "find_best_price":
            return find_best_price(**tool_input)
        elif tool_name == "search_user_tweets":
            return search_user_tweets(**tool_input)
        elif tool_name == "search_topics":
            return search_topics(**tool_input)
        elif tool_name == "search_trending_topics":
            return search_trending_topics(**tool_input)
        elif tool_name == "analyze_tweet_sentiment":
            return analyze_tweet_sentiment(**tool_input)
        elif tool_name == "check_weather":
            return check_weather(**tool_input)
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

        # Get current datetime for context
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")

        try:
            # Call Claude with tools
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                system=f"""You are Flub, a helpful flight search assistant. You communicate via iMessage text messages.

TODAY'S DATE: {current_date}
CURRENT TIME: {current_datetime}

CRITICAL RULES - FOLLOW EXACTLY:

1. TEXT FORMATTING (STRICTLY ENFORCED):
   - NEVER use markdown: no **, no ##, no -, no * for bullets
   - NEVER use emojis
   - Write like texting a friend - natural and conversational
   - Use blank lines to separate information, not bullets or headers
   - Keep messages short and scannable on mobile

   WRONG: "**Flight Options:**\n- Delta 123 ($299)\n✈️"
   RIGHT: "Found a few options for you:\n\nDelta 123 for $299\nUnited 456 for $315\n\nDelta looks best."

2. DATE VALIDATION (MUST CHECK BEFORE SEARCHING):
   - Today is {current_date}
   - ONLY search for flights on dates >= {current_date}
   - If user asks for past dates, respond: "I can only search for upcoming flights. That date has passed."
   - Calculate relative dates: "tomorrow" = day after {current_date}, "next Friday" = calculate from {current_date}
   - NEVER call search tools for past dates

 3. WHAT YOU CAN DO:
    - Search flights between airports (future dates only)
    - Find best prices
    - Compare options
    - Check X/Twitter for travel disruptions and delays
    - Monitor airline accounts for updates
    - Search trending travel topics
    - Analyze social media sentiment about travel issues
 
 4. WHAT YOU CANNOT DO:
   - Book flights (you only search)
   - Process payments
   - Access existing reservations
   - Search past dates
   - Make up flight information

5. RESPONSE STYLE:
   - Be helpful but brief
   - Assume user is on mobile
   - Don't over-explain
   - If no flights found, say so simply
   - Match the user's message style: if they send a short message like "whats the date" or "hi", respond with a similarly brief, human reply

   Examples:
   User: "whats the date"
   You: "It's November 9, 2025"

   User: "hi"
   You: "Hey! Need help finding flights?"

Example good response:
"I found 3 flights from LAX to JFK on Dec 15:

American 234 at 8am - $289 (nonstop, 5h 20m)
Delta 567 at 11am - $305 (nonstop, 5h 15m)
United 890 at 3pm - $275 (1 stop, 7h 45m)

 The United flight is cheapest but has a stop. American is a good balance of price and convenience."
 
 6. USING X/TWITTER TOOLS:
    - Use search_topics to find tweets about "flight delays [airport]", "airline issues", etc.
    - Use search_user_tweets to check @united, @delta, @americanair for updates
    - Use search_trending_topics to see what's trending related to travel
    - When reporting X findings, keep it brief: "Checked X - no major delays reported" or "FYI, people on X are reporting long security lines at LAX"
    - Don't overuse X tools - only when user asks about disruptions or you think it's relevant
 
 Remember: Plain text only. No markdown. No emojis. Check dates before searching.""",
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
