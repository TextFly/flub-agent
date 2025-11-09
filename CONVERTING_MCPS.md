# Converting MCP Servers to Direct Tools

This guide shows you how to convert any MCP server into a direct Python tool for flub-agent.

## Why Convert?

**Benefits of Direct Tools:**
- ✅ No servers to run or manage
- ✅ No HTTP endpoints or ports
- ✅ Faster execution (no network overhead)
- ✅ Simpler debugging
- ✅ Easier to deploy
- ✅ No MCP protocol complexity

## Step-by-Step Conversion Process

### 1. Find the MCP Tool Functions

Look in the MCP server code for functions decorated with `@mcp.tool()`:

```python
# From MCP server
@mcp.tool()
def search_flights(date: str, from_airport: str, to_airport: str) -> Dict[str, Any]:
    """Search for flights..."""
    # Implementation here
    return results
```

### 2. Extract the Function

Copy the function to a new file in `src/tools/`, removing the `@mcp.tool()` decorator:

```python
# src/tools/flight_search.py
def search_flights(date: str, from_airport: str, to_airport: str) -> Dict[str, Any]:
    """Search for flights..."""
    # Same implementation
    return results
```

### 3. Copy Helper Functions

If the tool uses helper functions, copy those too:

```python
# src/tools/flight_search.py
def parse_price(price_str: str) -> int:
    """Helper function"""
    return int(price_str.replace('$', ''))

def search_flights(date: str, from_airport: str, to_airport: str) -> Dict[str, Any]:
    """Main tool function"""
    price = parse_price(result.price)  # Uses helper
    return results
```

### 4. Update Imports

Replace MCP-specific imports with the actual libraries:

```python
# Before (in MCP):
from mcp.server.fastmcp import FastMCP
from fast_flights import FlightData

# After (in tool):
from fast_flights import FlightData
# No MCP imports needed!
```

### 5. Export the Tool

Add to `src/tools/__init__.py`:

```python
from .flight_search import search_flights, find_best_price
from .new_tool import new_function

__all__ = ['search_flights', 'find_best_price', 'new_function']
```

### 6. Register in Agent

Add the tool to `src/simple_agent.py`:

```python
class SimpleFlubAgent:
    def __init__(self, api_key: Optional[str] = None):
        # ... existing code ...

        # Import the tool
        from tools import new_function

        # Add to tools list
        self.tools.append({
            "name": "new_function",
            "description": "What this tool does...",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Description of param1"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Description of param2"
                    }
                },
                "required": ["param1"]
            }
        })

    def _call_tool(self, tool_name: str, tool_input: Dict[str, Any]):
        """Call the appropriate tool function."""
        if tool_name == "new_function":
            return new_function(**tool_input)
        # ... existing tools ...
```

### 7. Update Requirements

Add any new dependencies to `requirements.txt`:

```txt
anthropic
python-dotenv
fast-flights>=2.2
new-library>=1.0  # Add this
```

## Complete Example: Weather MCP → Weather Tool

### Original MCP Server

```python
# weather-mcp/src/main.py
from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Weather Server")

@mcp.tool()
def get_weather(city: str, date: str) -> Dict[str, Any]:
    """Get weather forecast for a city."""
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.weather.com/forecast?city={city}&date={date}"
    response = requests.get(url, headers={"Authorization": api_key})
    return response.json()
```

### Converted Tool

**Step 1:** Create `src/tools/weather.py`:

```python
"""Weather Tool - Converted from weather-mcp"""

import os
import requests
from typing import Dict, Any

def get_weather(city: str, date: str) -> Dict[str, Any]:
    """
    Get weather forecast for a city on a specific date.

    Args:
        city: City name (e.g., "Los Angeles", "New York")
        date: Date in YYYY-MM-DD format

    Returns:
        Dictionary with weather data including temperature, conditions, etc.
    """
    try:
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return {"success": False, "error": "WEATHER_API_KEY not set"}

        url = f"https://api.weather.com/forecast?city={city}&date={date}"
        response = requests.get(url, headers={"Authorization": api_key})
        response.raise_for_status()

        data = response.json()
        return {
            "success": True,
            "city": city,
            "date": date,
            "temperature": data.get("temp"),
            "conditions": data.get("conditions"),
            "humidity": data.get("humidity")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Step 2:** Export in `src/tools/__init__.py`:

```python
from .flight_search import search_flights, find_best_price
from .weather import get_weather

__all__ = ['search_flights', 'find_best_price', 'get_weather']
```

**Step 3:** Register in `src/simple_agent.py`:

```python
from tools import search_flights, find_best_price, get_weather

class SimpleFlubAgent:
    def __init__(self, api_key: Optional[str] = None):
        # ... existing init code ...

        self.tools = [
            # ... existing tools ...
            {
                "name": "get_weather",
                "description": "Get weather forecast for a city on a specific date. Returns temperature, conditions, and humidity.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name (e.g., 'Los Angeles', 'New York')"
                        },
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format"
                        }
                    },
                    "required": ["city", "date"]
                }
            }
        ]

    def _call_tool(self, tool_name: str, tool_input: Dict[str, Any]):
        if tool_name == "search_flights":
            return search_flights(**tool_input)
        elif tool_name == "find_best_price":
            return find_best_price(**tool_input)
        elif tool_name == "get_weather":
            return get_weather(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
```

**Step 4:** Add to `requirements.txt`:

```txt
requests>=2.31.0
```

**Step 5:** Add to `.env`:

```env
WEATHER_API_KEY=your_weather_api_key_here
```

Done! The weather tool is now integrated.

## Testing Your Tool

Create a simple test:

```python
# test_tool.py
from src.simple_agent import SimpleFlubAgent

agent = SimpleFlubAgent()
response = agent.process("What's the weather in Los Angeles on 2025-11-15?")
print(response)
```

## Common Patterns

### Pattern 1: API-based Tools

For tools that call external APIs:

```python
def api_tool(param: str) -> Dict[str, Any]:
    try:
        api_key = os.getenv("API_KEY")
        response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Pattern 2: Library-based Tools

For tools that use Python libraries:

```python
def library_tool(input_data: str) -> Dict[str, Any]:
    try:
        from some_library import process_data
        result = process_data(input_data)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Pattern 3: Data Processing Tools

For tools that process data:

```python
def process_tool(data: List[Dict]) -> Dict[str, Any]:
    try:
        processed = []
        for item in data:
            # Process each item
            processed.append(transform(item))
        return {"success": True, "results": processed}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Best Practices

1. **Always handle errors** - Return `{"success": False, "error": "message"}` on failure
2. **Use type hints** - Makes the code clearer and helps with debugging
3. **Document parameters** - Claude uses descriptions to understand how to use tools
4. **Return structured data** - Use dictionaries with clear keys
5. **Test independently** - Test tools before integrating with agent
6. **Keep it simple** - Don't overcomplicate; one tool = one clear purpose

## Troubleshooting

### Tool not being called
- Check the tool description is clear
- Verify the input_schema matches your function parameters
- Make sure the tool is in the `_call_tool` method

### Import errors
- Check `__init__.py` exports
- Verify all dependencies are in `requirements.txt`
- Run `pip install -r requirements.txt`

### Tool returns errors
- Test the function directly first
- Check environment variables are set
- Look at the error message in the response

## Next Steps

Now you can convert any MCP server to a direct tool! Some ideas:

- **X/Twitter monitoring** - Convert photon-imsg-mcp
- **Weather forecasts** - Use a weather API
- **News search** - Search and summarize news articles
- **Database queries** - Query your database directly
- **Calendar management** - Manage events and schedules

The sky's the limit! 🚀
