from .browser_agent import BrowserAgent, WORKER_CONFIGS

class JudgeAgent(BrowserAgent):
    def __init__(self, api_key: str = None):
        super().__init__("worker1", api_key)
    async def process(self, message: str, conversation_context: str = None) -> str:
        """
        Process outputs of other agents for user output
        """
        system_prompt = """"""