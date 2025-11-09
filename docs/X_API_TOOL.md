# X (Twitter) API Tool

The X API tool provides Twitter/X functionality for the flub-agent, converted from the standalone X-mcp server.

## Overview

This tool allows you to:
- Search tweets from specific users
- Search for topics and keywords
- Get trending topics
- Analyze tweet sentiment and engagement

## Setup

### 1. Install Dependencies

Make sure `tweepy` is in your `requirements.txt`:

```bash
pip install tweepy python-dotenv
```

### 2. Configure X API Credentials

Create a `.env` file in the project root with your X API credentials:

```env
# Required for most operations
X_BEARER_TOKEN=your_bearer_token_here

# Required for trending topics (API v1.1)
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### 3. Get X API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app or use an existing one
3. Get your Bearer Token from the "Keys and tokens" section
4. For trending topics, you'll also need API keys and access tokens

## Usage

### Import the Tools

```python
from tools import (
    search_user_tweets,
    search_trending_topics,
    search_topics,
    analyze_tweet_sentiment
)
```

## Available Functions

### 1. `search_user_tweets(username, max_results=10)`

Search recent tweets from a specific user.

**Parameters:**
- `username` (str): Twitter username without @ symbol
- `max_results` (int): Maximum tweets to return (default: 10, max: 100)

**Returns:**
```python
{
    "success": True,
    "user": {
        "id": "123456789",
        "name": "User Name",
        "username": "username",
        "description": "User bio...",
        "followers": 1000,
        "following": 500
    },
    "tweets": [
        {
            "id": "tweet_id",
            "text": "Tweet content...",
            "created_at": "2025-01-01 12:00:00",
            "likes": 100,
            "retweets": 50,
            "replies": 25
        }
    ],
    "count": 10
}
```

**Example:**
```python
result = search_user_tweets("elonmusk", max_results=5)
if result["success"]:
    print(f"User: {result['user']['name']}")
    for tweet in result['tweets']:
        print(f"- {tweet['text']}")
```

---

### 2. `search_topics(query, max_results=10, sort_order="recency")`

Search for tweets matching a specific query/topic.

**Parameters:**
- `query` (str): Search query or topic
- `max_results` (int): Maximum tweets to return (default: 10, max: 100)
- `sort_order` (str): "recency" or "relevancy" (default: "recency")

**Returns:**
```python
{
    "success": True,
    "query": "search query",
    "tweets": [
        {
            "id": "tweet_id",
            "text": "Tweet content...",
            "created_at": "2025-01-01 12:00:00",
            "author": {
                "username": "username",
                "name": "Name"
            },
            "likes": 100,
            "retweets": 50,
            "replies": 25
        }
    ],
    "count": 10
}
```

**Example:**
```python
result = search_topics("artificial intelligence", max_results=10)
if result["success"]:
    print(f"Found {result['count']} tweets")
    for tweet in result['tweets']:
        print(f"- {tweet['author']['name']}: {tweet['text'][:50]}...")
```

---

### 3. `search_trending_topics(woeid=1)`

Get current trending topics for a location.

**Parameters:**
- `woeid` (int): Where On Earth ID (default: 1 for Worldwide)
  - Common WOEIDs:
    - 1 = Worldwide
    - 23424977 = USA
    - 2459115 = New York City
    - 2487956 = San Francisco

**Note:** Requires full API credentials (API keys + access tokens)

**Returns:**
```python
{
    "success": True,
    "location": "Worldwide",
    "as_of": "2025-01-01T12:00:00Z",
    "trends": [
        {
            "name": "#TrendingTopic",
            "url": "http://twitter.com/...",
            "tweet_volume": 50000
        }
    ],
    "count": 20
}
```

**Example:**
```python
result = search_trending_topics(woeid=1)  # Worldwide
if result["success"]:
    print(f"Trending in {result['location']}:")
    for trend in result['trends'][:10]:
        volume = trend['tweet_volume'] or 'N/A'
        print(f"- {trend['name']} ({volume} tweets)")
```

---

### 4. `analyze_tweet_sentiment(tweets_data)`

Analyze engagement metrics from tweet search results.

**Parameters:**
- `tweets_data` (dict): Output from `search_topics()` or `search_user_tweets()`

**Returns:**
```python
{
    "success": True,
    "query": "search query",
    "total_tweets": 20,
    "engagement_metrics": {
        "total_likes": 1000,
        "total_retweets": 500,
        "total_replies": 250,
        "avg_likes_per_tweet": 50.0,
        "avg_retweets_per_tweet": 25.0,
        "avg_replies_per_tweet": 12.5
    },
    "top_engaged_tweet": {
        "text": "Most popular tweet...",
        "likes": 200,
        "retweets": 100,
        "author": {...}
    }
}
```

**Example:**
```python
# First search for tweets
tweets = search_topics("climate change", max_results=20)

# Then analyze them
analysis = analyze_tweet_sentiment(tweets)
if analysis["success"]:
    print(f"Total engagement: {analysis['engagement_metrics']['total_likes']} likes")
    print(f"Average likes per tweet: {analysis['engagement_metrics']['avg_likes_per_tweet']}")
    print(f"Top tweet: {analysis['top_engaged_tweet']['text'][:50]}...")
```

## Error Handling

All functions return a dictionary with a `success` field:

```python
result = search_user_tweets("nonexistent_user")
if result["success"]:
    # Process successful result
    print(result["tweets"])
else:
    # Handle error
    print(f"Error: {result['error']}")
```

## Rate Limiting

The X API has rate limits. The tool uses `wait_on_rate_limit=True` to automatically wait when limits are hit.

**Typical limits:**
- User timeline: 900 requests per 15 minutes
- Search: 180 requests per 15 minutes
- Trending topics: 75 requests per 15 minutes

## Examples

Run the example script:

```bash
# Show all available examples
python examples/x_api_example.py

# Run specific example
python examples/x_api_example.py 1  # Search user tweets
python examples/x_api_example.py 2  # Search topics
python examples/x_api_example.py 3  # Trending topics
python examples/x_api_example.py 4  # Analyze sentiment

# Run all examples
python examples/x_api_example.py all
```

## Integration with Agents

The X API tool is designed to be used by agents in the flub-agent system:

```python
from tools import search_topics, analyze_tweet_sentiment

class XAgent(BrowserAgent):
    def __init__(self, api_key: str = None):
        super().__init__("x_agent", api_key)
    
    async def process(self, message: str, conversation_context: str = None) -> str:
        # Use X API tools
        if "trending" in message.lower():
            result = search_trending_topics()
            return f"Current trends: {result['trends'][:5]}"
        
        elif "search" in message.lower():
            query = extract_query(message)
            tweets = search_topics(query, max_results=10)
            analysis = analyze_tweet_sentiment(tweets)
            return f"Found {tweets['count']} tweets. {analysis['engagement_metrics']}"
```

## Troubleshooting

### Missing Bearer Token

```
Error: X_BEARER_TOKEN environment variable is required
```

**Solution:** Set `X_BEARER_TOKEN` in your `.env` file

### Trending Topics Error

```
Error: Trending topics require full API credentials
```

**Solution:** Set all API credentials (API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

### Rate Limit Errors

The tool automatically waits for rate limits, but if you hit them frequently, consider:
- Reducing `max_results`
- Caching results
- Spacing out requests

## Differences from X-mcp

This tool is the **direct function** version of X-mcp:

| Feature | X-mcp | X API Tool |
|---------|-------|------------|
| Type | MCP Server | Direct functions |
| Transport | stdio/HTTP | Direct import |
| Usage | External server | Internal tool |
| Rate Limiting | Server-side | Client handles |
| Dependencies | fastmcp, mcp | tweepy only |

## License

Same as parent project

