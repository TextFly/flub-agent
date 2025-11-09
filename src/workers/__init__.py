"""
Workers package - Contains all worker agent implementations
"""
from .browser_agent import BrowserAgent, WORKER_CONFIGS
from .weather_agent import WeatherAgent
from .x_agent import XAgent
from .flights import FlightsAgent
from .judge import JudgeAgent

__all__ = ['BrowserAgent', 'WeatherAgent', 'XAgent', 'FlightsAgent', 'WORKER_CONFIGS']

