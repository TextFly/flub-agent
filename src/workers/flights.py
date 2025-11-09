from .browser_agent import BrowserAgent, WORKER_CONFIGS


class FlightsAgent(BrowserAgent):
    """Worker Agent 3 - Configure MCP servers and model in WORKER_CONFIGS['worker3']"""
    
    def __init__(self, api_key: str = None):
        super().__init__("worker3", api_key)
    
    async def process(self, message: str, conversation_context: str = None) -> str:
        """Process message with Worker 3's specialized capabilities"""
        system_prompt = """You are Worker 3, a specialized agent.
        Configure your specific capabilities and MCP servers in WORKER_CONFIGS['worker3'].
        Use the available MCP tools to help the user with their request."""
        
        context_section = f"\n\nPrevious conversation context:\n{conversation_context}" if conversation_context else ""
        
        enhanced_input = f"""{system_prompt}{context_section}

Current user request: {message}

Use your available tools to provide a comprehensive response that considers the conversation context if provided."""
        
        try:
            result = await self.runner.run(
                input=enhanced_input,
                model=self.config.get("model", "xai/grok-3"),
                mcp_servers=self.config.get("mcp_servers", []) if self.config.get("mcp_servers") else None
            )
            return result.final_output
        except Exception as e:
            return f"Error processing request in Worker 3: {str(e)}"

