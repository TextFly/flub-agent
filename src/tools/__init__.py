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
from .weather import check_weather

__all__ = [
    # Flight search tools
    'search_flights',
    'find_best_price',
    'parse_price',
    'calculate_price_range',
    'find_shortest_duration',
    'compare_flight_options',
    'filter_flights_by_criteria',
    # X API tools
    'search_user_tweets',
    'search_trending_topics',
    'search_topics',
    'analyze_tweet_sentiment',
    # Weather tools
    'check_weather'
]
