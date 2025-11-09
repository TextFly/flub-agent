"""
Workers package - Contains all worker agent implementations
"""
from .browser_agent import BrowserAgent, WORKER_CONFIGS
from .worker1 import Worker1
from .worker2 import Worker2
from .worker3 import Worker3

__all__ = ['BrowserAgent', 'Worker1', 'Worker2', 'Worker3', 'WORKER_CONFIGS']

