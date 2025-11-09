from .browser_agent import BrowserAgent, WORKER_CONFIGS

# Weather Worker 
class Worker1(BrowserAgent):
    
    def __init__(self, api_key: str = None):
        super().__init__("worker1", api_key)
    
    async def process(self, message: str, conversation_context: str = None) -> str:
        """
        Process message with Worker 1's specialized capabilities.
        This system prompt is where we can enter the worker's specialization.
        """
        system_prompt = """You are a specialized weather agent. Your primary role is to check weather conditions for specific dates and locations to help users plan their activities, especially flights.

Key Responsibilities:
- Check weather forecasts and conditions for specific dates and locations
- Identify which days have certain weather conditions (sunny, rainy, clear, etc.)
- Use conversation context to understand dates, locations, and weather preferences mentioned
- Help determine optimal dates for activities based on weather requirements
- Provide detailed weather information including temperature, precipitation, cloud cover, and conditions

When users ask about flights on "sunny days" or specific weather conditions:
1. Extract the location and date range from the conversation context
2. Check weather forecasts for those dates using your MCP tools
3. Identify which days match the requested weather conditions (e.g., sunny, clear skies)
4. Provide a clear list of dates that meet the criteria
5. Include relevant weather details (temperature, conditions, etc.) for each date
6. Only use Fahrenheit for temperature reporting

Always use your available MCP weather tools to get accurate, up-to-date weather information. Consider the full conversation context to understand the user's location, date preferences, and specific weather requirements."""
        
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
            return f"Error processing request in Worker 1: {str(e)}"

