# Flub Agent - Multi-Agent Orchestration System

A sophisticated multi-agent system with intelligent routing, parallel processing, and automated quality evaluation through a JudgeAgent.

## Overview

The Flub Agent system consists of:
- **OrchestratorAgent**: Routes messages to appropriate worker agents and synthesizes responses
- **Worker Agents**: Specialized agents with different capabilities and MCP servers
  - **WeatherAgent** (WORKER1): Weather forecasting and conditions
  - **Worker2**: Social media monitoring (X/Twitter via MCP)
  - **Worker3**: General purpose (configurable)
- **JudgeAgent**: Evaluates worker outputs for quality, relevance, and accuracy

## Key Features

### 🎯 Intelligent Routing
The orchestrator analyzes incoming messages and automatically routes them to the most appropriate worker agent(s).

### ⚡ Parallel Processing
When multiple workers are needed, they process requests simultaneously for faster responses.

### 🏆 Quality Evaluation
The JudgeAgent automatically evaluates worker outputs and provides:
- Individual scoring (relevance, accuracy, completeness, quality, coherence)
- Comparative analysis between workers
- Best response identification
- Actionable recommendations

### 💬 Conversation Context
Maintains conversation history to provide context-aware responses.

## Architecture

```
User Query
    ↓
OrchestratorAgent (routing)
    ↓
    ├→ WeatherAgent (WORKER1) ──┐
    ├→ Worker2 ─────────────────┤
    └→ Worker3 ─────────────────┤
                                 ↓
                          Worker Outputs
                                 ↓
                          JudgeAgent (evaluation)
                                 ↓
                          Synthesis & Response
                                 ↓
                            User Response
```

## Installation

1. **Clone the repository**
```bash
cd flub-agent
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the project root:
```env
DEDALUS_API_KEY=your_dedalus_api_key_here
# or
API_KEY=your_api_key_here
```

## Usage

### Basic Usage

```python
import asyncio
from orchestrator_agent import OrchestratorAgent

async def main():
    orchestrator = OrchestratorAgent()
    
    # Simple query
    response = await orchestrator.route_message(
        "What's the weather like in Paris?"
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Using the JudgeAgent (Automatic Mode)

The judge automatically evaluates worker outputs when multiple workers are used:

```python
orchestrator = OrchestratorAgent()

# Judge is enabled by default
# This will automatically trigger judge evaluation
response = await orchestrator.route_message(
    "What's the weather in NYC and are there any flight disruptions?"
)
```

### Using the JudgeAgent (Explicit Mode)

```python
orchestrator = OrchestratorAgent()

# Get explicit judge evaluation
evaluation = await orchestrator.get_judge_evaluation(
    message="Tell me about flying to Boston",
    worker_names=["WORKER1", "WORKER2"]  # Optional: specify which workers
)

print(evaluation)
```

### Toggle Judge Evaluation

```python
orchestrator = OrchestratorAgent()

# Disable judge
orchestrator.toggle_judge(False)

# Enable judge
orchestrator.toggle_judge(True)

# Toggle current state
orchestrator.toggle_judge()  # Flips current state
```

### Standalone Judge Usage

```python
from workers import JudgeAgent

judge = JudgeAgent()

# Evaluate worker outputs
worker_outputs = [
    {
        "worker_name": "WORKER1",
        "output": "Weather response..."
    },
    {
        "worker_name": "WORKER2",
        "output": "Social media response..."
    }
]

evaluation = await judge.evaluate_workers(
    original_message="User's question",
    worker_outputs=worker_outputs,
    conversation_context="Previous conversation..."  # Optional
)

print(evaluation['evaluation'])
```

### Quick Assessment

```python
judge = JudgeAgent()

# Fast pass/fail assessment
quick_result = await judge.quick_assessment(
    original_message="Is it safe to fly?",
    worker_outputs=worker_outputs
)
print(quick_result)
```

### Conflict Detection

```python
judge = JudgeAgent()

# Detect conflicts between worker responses
conflicts = await judge.detect_conflicts(
    worker_outputs=worker_outputs,
    original_message="User's question"  # Optional
)

print(conflicts['conflict_analysis'])
```

## Configuration

### Worker Configuration

Edit `src/workers/browser_agent.py` to configure worker models and MCP servers:

```python
WORKER_CONFIGS = {
    "worker1": {
        "model": "openai/gpt-4.1",
        "mcp_servers": [
            "cathy-di/open-meteo-mcp"
        ]
    },
    "worker2": {
        "model": "xai/grok-2",
        "mcp_servers": [
            "bolaji/X-mcp"
        ]
    },
    "worker3": {
        "model": "xai/grok-3",
        "mcp_servers": []
    }
}
```

### Orchestrator Configuration

Edit `src/orchestrator_agent.py`:

```python
ORCHESTRATOR_AGENT_CONFIG = {
    "model": "openai/gpt-4.1",
    "mcp_servers": []
}
```

### Judge Configuration

Edit `src/workers/judge.py`:

```python
JUDGE_CONFIG = {
    "model": "openai/gpt-4.1",  # Use high-quality model for evaluation
    "mcp_servers": []  # Judge doesn't need MCP servers
}
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python test_judge.py all

# Run specific test
python test_judge.py 1  # Toggle judge
python test_judge.py 2  # Standalone judge
python test_judge.py 3  # Quick assessment
python test_judge.py 4  # Conflict detection
python test_judge.py 5  # Explicit evaluation
python test_judge.py 6  # Judge with orchestrator
```

## JudgeAgent Evaluation Criteria

The judge evaluates responses based on five key criteria (scored 0-10):

1. **Relevance**: How well the response addresses the original request
2. **Accuracy**: Correctness and reliability of information
3. **Completeness**: Coverage of all aspects of the request
4. **Quality**: Soundness of reasoning and structure
5. **Coherence**: Logical organization and clarity

## Advanced Features

### Conversation History Management

```python
orchestrator = OrchestratorAgent()

# Process multiple messages with context
await orchestrator.route_message("What's the weather in NYC?")
await orchestrator.route_message("How about tomorrow?")  # Uses context

# Clear history
orchestrator.clear_history()
```

### Global Agent Instance

```python
from orchestrator_agent import get_global_agent, clear_conversation

# Use persistent global agent (maintains history across calls)
agent = get_global_agent()
response = await agent.route_message("Hello")

# Clear global conversation history
clear_conversation()
```

## API Reference

### OrchestratorAgent

- `route_message(message: str) -> str`: Route and process a message
- `get_judge_evaluation(message: str, worker_names: list = None) -> str`: Get explicit judge evaluation
- `toggle_judge(enabled: bool = None) -> bool`: Enable/disable/toggle judge
- `clear_history()`: Clear conversation history

### JudgeAgent

- `evaluate_workers(original_message, worker_outputs, conversation_context=None) -> Dict`: Comprehensive evaluation
- `evaluate_single_response(original_message, response, worker_name, conversation_context=None) -> Dict`: Evaluate single response
- `quick_assessment(original_message, worker_outputs, conversation_context=None) -> str`: Fast pass/fail assessment
- `detect_conflicts(worker_outputs, original_message=None) -> Dict`: Detect conflicts between outputs

## Project Structure

```
flub-agent/
├── src/
│   ├── orchestrator_agent.py      # Main orchestrator
│   └── workers/
│       ├── __init__.py
│       ├── browser_agent.py       # Base worker class
│       ├── weather_agent.py       # Weather worker
│       ├── worker2.py             # Social media worker
│       ├── worker3.py             # General worker
│       └── judge.py               # Judge agent
├── test_judge.py                   # Comprehensive test suite
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

## Best Practices

1. **Use Judge for Complex Queries**: Enable judge evaluation when you need quality assurance
2. **Disable Judge for Speed**: Turn off judge for simple queries where evaluation isn't needed
3. **Conversation Context**: Leverage conversation history for multi-turn interactions
4. **Error Handling**: Workers return error messages rather than crashing
5. **Configuration**: Customize models and MCP servers per worker for optimal performance

## Troubleshooting

### Judge Not Activating
- Judge only activates automatically when multiple workers are used
- Verify `orchestrator.use_judge = True`
- Check that more than one worker is processing the message

### API Key Issues
```python
# Set in .env file
DEDALUS_API_KEY=your_key_here

# Or pass directly
orchestrator = OrchestratorAgent(api_key="your_key")
```

### Worker Configuration
- Ensure MCP servers are properly formatted in `WORKER_CONFIGS`
- Use valid model identifiers (e.g., `openai/gpt-4.1`, `xai/grok-2`)

## Contributing

When adding new workers:
1. Extend `BrowserAgent` class
2. Add to `WORKER_CONFIGS` in `browser_agent.py`
3. Import and initialize in `OrchestratorAgent`
4. Update routing logic if needed

## License

[Your License Here]

## Support

For issues and questions, please open an issue on the repository.
