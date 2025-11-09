"""
X (Twitter) API Tool

Provides X/Twitter API functionality for searching tweets and topics.
Converted from X-mcp to be a direct tool for flub-agent.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
import tweepy

# Load environment variables
load_dotenv()

# Get X API credentials from environment variables
BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")


def get_twitter_client() -> tweepy.Client:
    """Initialize and return Twitter API client."""
    if not BEARER_TOKEN:
        raise ValueError(
            "X_BEARER_TOKEN environment variable is required. "
            "Please set it with your Twitter API Bearer Token."
        )
    
    return tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )


def search_user_tweets(
    username: str,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search through the most recent tweets of a specific user.
    
    Args:
        username: The X/Twitter username (without @)
        max_results: Maximum number of tweets to return (default: 10, max: 100)
    
    Returns:
        Dictionary containing user info and their recent tweets
    """
    try:
        client = get_twitter_client()
        
        # Get user by username
        user = client.get_user(username=username, user_fields=["description", "public_metrics"])
        if not user.data:
            return {"success": False, "error": f"User @{username} not found"}
        
        user_id = user.data.id
        user_info = {
            "id": user.data.id,
            "name": user.data.name,
            "username": user.data.username,
            "description": user.data.description,
            "followers": user.data.public_metrics["followers_count"],
            "following": user.data.public_metrics["following_count"],
        }
        
        # Get user's recent tweets
        tweets = client.get_users_tweets(
            id=user_id,
            max_results=min(max_results, 100),
            tweet_fields=["created_at", "public_metrics", "text"],
        )
        
        tweet_list = []
        if tweets.data:
            for tweet in tweets.data:
                tweet_list.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": str(tweet.created_at),
                    "likes": tweet.public_metrics["like_count"],
                    "retweets": tweet.public_metrics["retweet_count"],
                    "replies": tweet.public_metrics["reply_count"],
                })
        
        return {
            "success": True,
            "user": user_info,
            "tweets": tweet_list,
            "count": len(tweet_list),
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_trending_topics(
    woeid: int = 1  # 1 = Worldwide
) -> Dict[str, Any]:
    """
    Search for current trending topics on X/Twitter.
    
    Args:
        woeid: Where On Earth ID for location (default: 1 for Worldwide)
               Common WOEIDs: 1=Worldwide, 23424977=USA, 2459115=NYC
    
    Returns:
        Dictionary containing current trending topics
    """
    try:
        # Note: Trending topics require API v1.1 which needs API keys
        if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
            return {
                "success": False,
                "error": "Trending topics require full API credentials. "
                        "Please set X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, "
                        "and X_ACCESS_TOKEN_SECRET environment variables."
            }
        
        # Use API v1.1 for trends
        auth = tweepy.OAuth1UserHandler(
            API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)
        
        trends = api.get_place_trends(id=woeid)
        
        if not trends:
            return {"success": False, "error": "No trends found"}
        
        trending_list = []
        for trend in trends[0]["trends"][:20]:  # Get top 20 trends
            trending_list.append({
                "name": trend["name"],
                "url": trend["url"],
                "tweet_volume": trend.get("tweet_volume"),
            })
        
        return {
            "success": True,
            "location": trends[0]["locations"][0]["name"],
            "as_of": trends[0]["as_of"],
            "trends": trending_list,
            "count": len(trending_list),
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_topics(
    query: str,
    max_results: int = 10,
    sort_order: str = "recency"
) -> Dict[str, Any]:
    """
    Search for specific user-generated topics on X/Twitter.
    
    Args:
        query: The search query/topic to search for
        max_results: Maximum number of tweets to return (default: 10, max: 100)
        sort_order: Sort order - "recency" or "relevancy" (default: "recency")
    
    Returns:
        Dictionary containing tweets matching the search query
    """
    try:
        client = get_twitter_client()
        
        # Search for tweets matching the query
        tweets = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            tweet_fields=["created_at", "public_metrics", "author_id"],
            user_fields=["username", "name"],
            expansions=["author_id"],
            sort_order=sort_order if sort_order in ["recency", "relevancy"] else "recency",
        )
        
        if not tweets.data:
            return {
                "success": True,
                "query": query,
                "tweets": [],
                "count": 0,
                "message": "No tweets found matching the query",
            }
        
        # Create a mapping of user IDs to user info
        users = {user.id: user for user in tweets.includes.get("users", [])}
        
        tweet_list = []
        for tweet in tweets.data:
            author = users.get(tweet.author_id)
            tweet_list.append({
                "id": tweet.id,
                "text": tweet.text,
                "created_at": str(tweet.created_at),
                "author": {
                    "username": author.username if author else "unknown",
                    "name": author.name if author else "unknown",
                } if author else None,
                "likes": tweet.public_metrics["like_count"],
                "retweets": tweet.public_metrics["retweet_count"],
                "replies": tweet.public_metrics["reply_count"],
            })
        
        return {
            "success": True,
            "query": query,
            "tweets": tweet_list,
            "count": len(tweet_list),
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_tweet_sentiment(tweets_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze sentiment and engagement metrics from tweet search results.
    
    Args:
        tweets_data: Output from search_topics or search_user_tweets
    
    Returns:
        Dictionary with sentiment analysis and engagement metrics
    """
    try:
        if not tweets_data.get("success") or not tweets_data.get("tweets"):
            return {
                "success": False,
                "error": "No valid tweets data provided"
            }
        
        tweets = tweets_data["tweets"]
        total_tweets = len(tweets)
        
        # Calculate engagement metrics
        total_likes = sum(t.get("likes", 0) for t in tweets)
        total_retweets = sum(t.get("retweets", 0) for t in tweets)
        total_replies = sum(t.get("replies", 0) for t in tweets)
        
        # Calculate averages
        avg_likes = round(total_likes / total_tweets, 2) if total_tweets > 0 else 0
        avg_retweets = round(total_retweets / total_tweets, 2) if total_tweets > 0 else 0
        avg_replies = round(total_replies / total_tweets, 2) if total_tweets > 0 else 0
        
        # Find top engaged tweet
        top_tweet = max(tweets, key=lambda t: t.get("likes", 0) + t.get("retweets", 0)) if tweets else None
        
        return {
            "success": True,
            "query": tweets_data.get("query"),
            "total_tweets": total_tweets,
            "engagement_metrics": {
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "total_replies": total_replies,
                "avg_likes_per_tweet": avg_likes,
                "avg_retweets_per_tweet": avg_retweets,
                "avg_replies_per_tweet": avg_replies,
            },
            "top_engaged_tweet": {
                "text": top_tweet.get("text") if top_tweet else None,
                "likes": top_tweet.get("likes") if top_tweet else 0,
                "retweets": top_tweet.get("retweets") if top_tweet else 0,
                "author": top_tweet.get("author") if top_tweet else None,
            } if top_tweet else None
        }
    
    except Exception as e:
        return {"success": False, "error": f"Analysis failed: {str(e)}"}

