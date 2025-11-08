import os
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()

# Configuration for Worker Agents
WORKER_CONFIGS = {
    "worker1": {
        "model": "openai/gpt-4.1",  # Change this to your preferred model
        "mcp_servers": [
            # Add MCP servers for worker 1 here
            # Example: "windsor/flight-mcp",
        ]
    },
    "worker2": {
        "model": "xai/grok-2",  # Change this to your preferred model
        "mcp_servers": [
            # Add MCP servers for worker 2 here
            # Example: "windsor/hotel-mcp",
        ]
    },
    "worker3": {
        "model": "xai/grok-3",  # Change this to your preferred model
        "mcp_servers": [
            # Add MCP servers for worker 3 here
            # Example: "windsor/weather-mcp",
        ]
    }
}


class BaseWorker:
    """Base class for worker agents with common functionality"""
    
    def __init__(self, worker_name: str, api_key: str = None):
        self.worker_name = worker_name
        self.api_key = api_key or os.getenv("DEDALUS_API_KEY") or os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set DEDALUS_API_KEY or API_KEY in your .env file")
        
        self.client = AsyncDedalus(api_key=self.api_key)
        self.runner = DedalusRunner(self.client)
        self.config = WORKER_CONFIGS.get(worker_name, {})
    
    async def process(self, message: str, conversation_context: str = None) -> str:
        """
        Process a message using this worker agent.
        
        Args:
            message: The user's message
            conversation_context: Optional conversation history
            
        Returns:
            Response string from the worker agent
        """
        system_prompt = f"""You are {self.worker_name}, a specialized worker agent.
        Use the available MCP tools to help the user with their request.
        Provide a helpful and detailed response."""
        
        context_section = f"\n\nPrevious conversation context:\n{conversation_context}" if conversation_context else ""
        
        enhanced_input = f"""{system_prompt}{context_section}

Current user request: {message}

Use your available tools to provide a comprehensive response that considers the conversation context if provided."""
        
        try:
            result = await self.runner.run(
                input=enhanced_input,
                model=self.config.get("model", "openai/gpt-4.1"),
                mcp_servers=self.config.get("mcp_servers", []) if self.config.get("mcp_servers") else None
            )
            return result.final_output
        except Exception as e:
            return f"Error processing request in {self.worker_name}: {str(e)}"

