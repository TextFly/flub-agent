# Flub Agent - Simple Travel Planning Assistant

A clean, single-agent travel planning system built with **Claude API** and **direct tool integration** (no MCP needed!).

## Overview

Flub Agent is a simple, powerful travel planning assistant that uses Claude's native function calling with direct Python tool integration for flight search and other travel services.

### Key Features

- **Single Agent Architecture**: One Claude agent with direct access to all tools
- **No MCP Complexity**: Tools are simple Python functions - no servers to run
- **Natural Tool Selection**: Claude automatically uses the right tools for each query
- **Conversation Context**: Maintains history for multi-turn planning
- **Easy to Extend**: Add new tools by creating Python functions

## Quick Start

### Prerequisites
- Python 3.10+
- An Anthropic API key

### Installation

1. **Clone and navigate to the repository**
```bash
cd flub-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

4. **Run the agent**
```bash
python main.py
```

## Usage

### Basic Usage

```python
from src.simple_agent import SimpleFlubAgent

# Create agent
agent = SimpleFlubAgent()

# Ask a question
response = agent.process("What's the cheapest flight from EWR to LAX on 2025-11-10?")
print(response)
```

### Multi-turn Conversation

```python
agent = SimpleFlubAgent()

# First query
response1 = agent.process("Find flights from NYC to LA on December 1st")
print(response1)

# Follow-up with context
response2 = agent.process("What's the cheapest option?")
print(response2)

# Clear history when done
agent.clear_history()
```

## Project Structure

```
flub-agent/
├── src/
│   ├── simple_agent.py        # Main agent using Claude function calling
│   └── tools/                 # Tool functions
│       ├── __init__.py
│       └── flight_search.py   # Flight search tools
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
└── README.md                  # This file
```

## Architecture

```
User Query
    ↓
SimpleFlubAgent (Claude with Function Calling)
    │
    ├─ Tool: search_flights()
    ├─ Tool: find_best_price()
    └─ Tool: [Add more tools...]
    │
    ↓
Claude automatically selects and calls appropriate Python functions
    ↓
Unified Response
```

## Available Tools

### Flight Search Tools

**search_flights**
- Search for flights between airports on a specific date
- Parameters: date, from_airport, to_airport, adults, max_results
- Returns: List of flights with pricing, duration, and details

**find_best_price**
- Find the cheapest flight for a route and date
- Parameters: date, from_airport, to_airport, adults
- Returns: Cheapest flight with price comparisons

## Adding New Tools

To add a new tool:

1. **Create a tool file** in `src/tools/`:
```python
# src/tools/weather.py
def get_weather(city: str, date: str):
    """Get weather forecast for a city on a specific date."""
    # Your implementation
    return {"temperature": 72, "conditions": "sunny"}
```

2. **Export it** in `src/tools/__init__.py`:
```python
from .flight_search import search_flights, find_best_price
from .weather import get_weather

__all__ = ['search_flights', 'find_best_price', 'get_weather']
```

3. **Register it** in `src/simple_agent.py`:
```python
# Import the tool
from tools import get_weather

# Add to self.tools list
self.tools.append({
    "name": "get_weather",
    "description": "Get weather forecast for a city on a specific date",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"},
            "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
        },
        "required": ["city", "date"]
    }
})

# Add to _call_tool method
def _call_tool(self, tool_name: str, tool_input: Dict[str, Any]):
    if tool_name == "get_weather":
        return get_weather(**tool_input)
    # ... existing tools
```

That's it! No servers to run, no HTTP endpoints to configure.

## API Reference

### SimpleFlubAgent

```python
SimpleFlubAgent(api_key: Optional[str] = None)
```

**Methods:**
- `process(message: str) -> str`: Process a message and return response
- `clear_history()`: Clear conversation history

## Examples

See `main.py` for a working example:

```python
from datetime import datetime, timedelta
from src.simple_agent import SimpleFlubAgent

agent = SimpleFlubAgent()

tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
response = agent.process(f"What is the best flight from EWR to LAX on {tomorrow}?")
print(response)
```

## Environment Variables

Required:
- `ANTHROPIC_API_KEY`: Your Anthropic API key

## Troubleshooting

### API Key Issues
Make sure `ANTHROPIC_API_KEY` is set in your `.env` file.

### Import Errors
Make sure you're running from the project root:
```bash
cd /path/to/flub-agent
python main.py
```

### Tool Errors
If a tool fails, check the error message in the response. The agent will report tool errors gracefully.

## Resources

- [Claude API Documentation](https://docs.anthropic.com)
- [Function Calling Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.
