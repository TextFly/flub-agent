import asyncio
import random
import os
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv


# Intakes messages from user
# Create a task using that message 
# Assign said task to a MCP server
load_dotenv()

async def process_travel_request(message: str, model: str = None):
    """
    Processes a travel-related message and uses Dedalus to determine which tools
    from the available MCP servers should be used.
    Args:
        message: The travel request message from the user
        model: Optional model name. If None, will randomly select from available models.
    Returns:
        The result from DedalusRunner
    """
    # Get API key from environment variable
    api_key = os.getenv("DEDALUS_API_KEY") or os.getenv("API_KEY")
    
    if not api_key:
        raise ValueError("API key not found. Please set DEDALUS_API_KEY or API_KEY in your .env file")
    
    # Initialize client with API key
    client = AsyncDedalus(api_key=api_key)
    runner = DedalusRunner(client)
    
    # Models to choose from
    available_models = [
        "openai/gpt-4.1",
        "xai/grok-2",
        "xai/grok-3",
        # Add more models as needed
    ]
    
    # Select a model or random
    if model is None:
        selected_model = random.choice(available_models)
    else:
        selected_model = model
    
    # TODO: INSERT MCP SERVERS HERE 
    mcp_servers = []
    
    # Include system instructions in the input message since system_prompt isn't supported
    enhanced_input = f"""You are a helpful travel assistant. Your role is to help users plan their trips by:
    - Finding flights, hotels, and transportation options
    - Providing weather information for destinations
    - Suggesting activities and attractions
    - Answering questions about travel requirements, visas, and local information
    - Comparing prices and options
    
    Use the available tools from the MCP servers to gather information and provide comprehensive travel assistance.

    User request: {message}"""
    
    result = await runner.run(
        input=enhanced_input,
        model=selected_model,
        mcp_servers=mcp_servers
    )
    return result


async def main():
    # Example usage - test with a simple travel query
    message = "I want to plan a trip to Paris"
    print(f"Testing with message: {message}")
    print("Processing...\n")
    
    result = await process_travel_request(message)
    
    # Print for testing (remove this when integrating with iMessage)
    print(f"Response:\n{result.final_output}")
    
    return result.final_output

if __name__ == "__main__":
    asyncio.run(main())