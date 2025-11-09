"""
Example usage of X API tool in flub-agent

This script demonstrates how to use the X API functionality
that was converted from X-mcp.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tools import (
    search_user_tweets,
    search_trending_topics,
    search_topics,
    analyze_tweet_sentiment
)


def example_search_user_tweets():
    """Example: Search tweets from a specific user"""
    print("=" * 80)
    print("Example 1: Search User Tweets")
    print("=" * 80)
    
    username = "elonmusk"  # Example username
    print(f"\nSearching tweets from @{username}...\n")
    
    result = search_user_tweets(username=username, max_results=5)
    
    if result.get("success"):
        print(f"User: {result['user']['name']} (@{result['user']['username']})")
        print(f"Followers: {result['user']['followers']:,}")
        print(f"Description: {result['user']['description']}")
        print(f"\nRecent Tweets ({result['count']}):")
        print("-" * 80)
        
        for tweet in result['tweets']:
            print(f"\n📝 {tweet['text'][:100]}...")
            print(f"   ❤️  {tweet['likes']}  |  🔄 {tweet['retweets']}  |  💬 {tweet['replies']}")
            print(f"   📅 {tweet['created_at']}")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    print("\n")


def example_search_topics():
    """Example: Search for specific topics"""
    print("=" * 80)
    print("Example 2: Search Topics")
    print("=" * 80)
    
    query = "artificial intelligence"  # Example query
    print(f"\nSearching for: '{query}'...\n")
    
    result = search_topics(query=query, max_results=5, sort_order="recency")
    
    if result.get("success"):
        print(f"Found {result['count']} tweets about '{query}':")
        print("-" * 80)
        
        for i, tweet in enumerate(result['tweets'], 1):
            print(f"\n{i}. {tweet['text'][:100]}...")
            if tweet['author']:
                print(f"   👤 {tweet['author']['name']} (@{tweet['author']['username']})")
            print(f"   ❤️  {tweet['likes']}  |  🔄 {tweet['retweets']}  |  💬 {tweet['replies']}")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    print("\n")


def example_trending_topics():
    """Example: Get trending topics"""
    print("=" * 80)
    print("Example 3: Trending Topics")
    print("=" * 80)
    
    print("\nFetching worldwide trending topics...\n")
    
    result = search_trending_topics(woeid=1)  # 1 = Worldwide
    
    if result.get("success"):
        print(f"Trending in: {result['location']}")
        print(f"As of: {result['as_of']}")
        print(f"\nTop {result['count']} Trends:")
        print("-" * 80)
        
        for i, trend in enumerate(result['trends'][:10], 1):
            volume = f"({trend['tweet_volume']:,} tweets)" if trend['tweet_volume'] else "(volume N/A)"
            print(f"{i:2d}. {trend['name']} {volume}")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    print("\n")


def example_analyze_sentiment():
    """Example: Analyze tweet sentiment and engagement"""
    print("=" * 80)
    print("Example 4: Analyze Tweet Sentiment")
    print("=" * 80)
    
    query = "climate change"  # Example query
    print(f"\nAnalyzing tweets about: '{query}'...\n")
    
    # First, search for tweets
    tweets_result = search_topics(query=query, max_results=20)
    
    if tweets_result.get("success"):
        # Then analyze them
        analysis = analyze_tweet_sentiment(tweets_result)
        
        if analysis.get("success"):
            print(f"Analysis for query: '{analysis['query']}'")
            print(f"Total tweets analyzed: {analysis['total_tweets']}")
            print("\nEngagement Metrics:")
            print("-" * 80)
            
            metrics = analysis['engagement_metrics']
            print(f"Total Likes:     {metrics['total_likes']:,}")
            print(f"Total Retweets:  {metrics['total_retweets']:,}")
            print(f"Total Replies:   {metrics['total_replies']:,}")
            print(f"\nAverage per tweet:")
            print(f"  Likes:    {metrics['avg_likes_per_tweet']:.2f}")
            print(f"  Retweets: {metrics['avg_retweets_per_tweet']:.2f}")
            print(f"  Replies:  {metrics['avg_replies_per_tweet']:.2f}")
            
            if analysis['top_engaged_tweet']:
                top = analysis['top_engaged_tweet']
                print(f"\nMost Engaged Tweet:")
                print("-" * 80)
                print(f"📝 {top['text'][:100]}...")
                if top['author']:
                    print(f"👤 {top['author']['name']} (@{top['author']['username']})")
                print(f"❤️  {top['likes']}  |  🔄 {top['retweets']}")
        else:
            print(f"❌ Analysis Error: {analysis.get('error')}")
    else:
        print(f"❌ Search Error: {tweets_result.get('error')}")
    
    print("\n")


def main():
    """Run all examples"""
    print("\n" + "🐦" * 40)
    print("X (Twitter) API Tool Examples")
    print("🐦" * 40 + "\n")
    
    print("Note: Make sure X_BEARER_TOKEN is set in your .env file\n")
    
    examples = [
        ("Search User Tweets", example_search_user_tweets),
        ("Search Topics", example_search_topics),
        ("Trending Topics", example_trending_topics),
        ("Analyze Sentiment", example_analyze_sentiment),
    ]
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        if choice.isdigit() and 1 <= int(choice) <= len(examples):
            examples[int(choice) - 1][1]()
        elif choice == "all":
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"❌ Error in {name}: {e}\n")
        else:
            print(f"Invalid choice. Use 1-{len(examples)} or 'all'")
    else:
        print("Available examples:")
        for i, (name, _) in enumerate(examples, 1):
            print(f"  {i}. {name}")
        print("  all. Run all examples")
        print(f"\nUsage: python {os.path.basename(__file__)} [1-{len(examples)}|all]")
        print(f"Example: python {os.path.basename(__file__)} 1\n")


if __name__ == "__main__":
    main()

