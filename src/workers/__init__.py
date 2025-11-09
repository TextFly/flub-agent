"""
Workers package - Contains all worker agent implementations
"""
from .browser_agent import BrowserAgent, WORKER_CONFIGS
from .weather_agent import WeatherAgent
from .worker2 import Worker2
from .worker3 import Worker3
from .judge import JudgeAgent

__all__ = ['BrowserAgent', 'WeatherAgent', 'Worker2', 'Worker3', 'JudgeAgent', 'WORKER_CONFIGS']

