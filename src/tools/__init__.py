"""
Tools package for Flub Agent

Each tool provides specific functionality that the agent can use.
"""

from .flight_search import search_flights, find_best_price
from .x_api import (
    search_user_tweets,
    search_trending_topics,
    search_topics,
    analyze_tweet_sentiment
)

__all__ = [
    # Flight search tools
    'search_flights',
    'find_best_price',
    # X API tools
    'search_user_tweets',
    'search_trending_topics',
    'search_topics',
    'analyze_tweet_sentiment'
]
