# SimpleFlubAgent X API Integration

## Overview

The `SimpleFlubAgent` has been updated to include X/Twitter API tools alongside the existing flight search functionality.

## What Changed

### 1. **Imports Updated** (`src/simple_agent.py`)

Added X API tool imports:
```python
from .tools import (
    search_flights, 
    find_best_price,
    search_user_tweets,
    search_trending_topics,
    search_topics,
    analyze_tweet_sentiment
)
```

### 2. **New Tool Definitions** 

Added 4 new tool definitions to `self.tools`:

#### a. `search_user_tweets`
- Search recent tweets from a specific X/Twitter user
- Parameters: `username`, `max_results`
- Returns: User info and recent tweets with engagement metrics

#### b. `search_topics`
- Search for tweets about specific topics/keywords
- Parameters: `query`, `max_results`, `sort_order`
- Returns: Tweets matching query with author and engagement data

#### c. `search_trending_topics`
- Get current trending topics for a location
- Parameters: `woeid` (Where On Earth ID)
- Returns: Top trending hashtags and topics with volumes

#### d. `analyze_tweet_sentiment`
- Analyze engagement metrics from tweet searches
- Parameters: `tweets_data` (output from other search functions)
- Returns: Aggregated engagement statistics and top tweets

### 3. **Tool Execution Handler Updated**

The `_call_tool()` method now routes to X API functions:
```python
def _call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == "search_flights":
        return search_flights(**tool_input)
    elif tool_name == "find_best_price":
        return find_best_price(**tool_input)
    elif tool_name == "search_user_tweets":
        return search_user_tweets(**tool_input)
    elif tool_name == "search_topics":
        return search_topics(**tool_input)
    # ... etc
```

### 4. **System Prompt Enhanced**

Updated agent capabilities description:
```
Your capabilities:
- Search for flights between airports
- Find the best prices for future travel
- Provide travel recommendations
- Search X/Twitter for user tweets, topics, and trends
- Monitor social media for travel-related disruptions and incidents
- Analyze tweet engagement and sentiment
```

Added guidance for X API usage:
```
When users ask about travel disruptions, incidents, or social media updates:
1. Use search_topics to search for relevant keywords
2. Use search_user_tweets to check specific airline/airport accounts
3. Use search_trending_topics to see what's trending
4. Use analyze_tweet_sentiment to understand engagement
5. Provide a clear summary of any relevant disruptions found
```

### 5. **Documentation Updated**

- Updated class docstring to list X API capabilities
- Updated module docstring to mention X API tools

## New Files Created

### `examples/simple_agent_x_api_demo.py`

Demo script showing X API integration with two modes:

**Demo Mode** (default):
```bash
python examples/simple_agent_x_api_demo.py
```
- Provides 4 pre-written example queries
- Choose a query or enter custom

**Interactive Mode:**
```bash
python examples/simple_agent_x_api_demo.py interactive
```
- Chat with agent in real-time
- Supports conversation history
- Clear history with 'clear' command

## Usage Examples

### Example 1: Check Trending Topics
```python
from simple_agent import SimpleFlubAgent

agent = SimpleFlubAgent()
response = agent.process("What's trending on X/Twitter right now?")
print(response)
```

### Example 2: Monitor Airline Updates
```python
response = agent.process("Check recent tweets from @united about flight delays")
print(response)
```

### Example 3: Search for Disruptions
```python
response = agent.process("Search X for any reports about airport security issues today")
print(response)
```

### Example 4: Combined Flight + Social Monitoring
```python
response = agent.process(
    "Find flights from EWR to LAX on 2025-11-20 and check if there are "
    "any travel disruptions being reported on X"
)
print(response)
```

## Requirements

### Environment Variables

Make sure these are set in your `.env` file:

```env
# Required for agent
ANTHROPIC_API_KEY=your_anthropic_api_key

# Required for X API tools
X_BEARER_TOKEN=your_x_bearer_token

# Optional (for trending topics)
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### Dependencies

Ensure these packages are installed:
```bash
pip install anthropic tweepy python-dotenv fast-flights
```

## Tool Capabilities Summary

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `search_flights` | Find available flights | date, from_airport, to_airport |
| `find_best_price` | Find cheapest flight | date, from_airport, to_airport |
| `search_user_tweets` | Get user's recent tweets | username, max_results |
| `search_topics` | Search for keywords/topics | query, max_results, sort_order |
| `search_trending_topics` | Get trending hashtags | woeid (location) |
| `analyze_tweet_sentiment` | Analyze engagement metrics | tweets_data |

## Benefits

1. **Social Media Monitoring**: Agent can now check for real-time travel disruptions
2. **Airline Updates**: Monitor official airline accounts for delays/cancellations
3. **Trend Awareness**: Know what's trending in travel/aviation
4. **Sentiment Analysis**: Understand public sentiment around travel topics
5. **Enhanced Context**: Combine flight search with social media intelligence

## Testing

Run the demo to verify integration:
```bash
# Demo mode
python examples/simple_agent_x_api_demo.py

# Interactive mode
python examples/simple_agent_x_api_demo.py interactive
```

## Verification

✅ All imports added
✅ All tool definitions added
✅ Tool execution handler updated
✅ System prompt enhanced
✅ Documentation updated
✅ Demo script created
✅ No linter errors
✅ All syntax valid

## Next Steps

1. Test with actual X API credentials
2. Try the demo queries
3. Experiment with custom queries combining flights + X API
4. Monitor rate limits (X API has usage limits)

## Notes

- The agent intelligently decides when to use X API tools based on user queries
- X API tools respect rate limits (built into tweepy)
- All tools return consistent `success`/`error` format
- The agent can use multiple tools in sequence (e.g., search + analyze)

## Related Documentation

- [X API Tool Documentation](./X_API_TOOL.md)
- [Flight Search Documentation](../README.md)
- [X API Examples](../examples/x_api_example.py)

