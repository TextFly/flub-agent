# iMessage Integration Setup

This guide shows you how to set up the iMessage watcher to automatically respond to text messages using Flub Agent.

## Architecture

```
iMessage → photon-imsg-mcp → TypeScript Watcher → HTTP API → Flub Agent → Response → iMessage
```

## Prerequisites

1. **macOS** (iMessage only works on Mac)
2. **Bun or Node.js** (for running the TypeScript watcher)
3. **Python 3.10+** (for the Flub Agent API)

## Setup Steps

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# TypeScript/Node dependencies
bun install
# or: npm install
```

### 2. Start the Agent API Server

In terminal 1:

```bash
python agent_server.py
```

You should see:
```
======================================================================
Flub Agent API Server
======================================================================
Starting server on http://localhost:3000
Endpoints:
  POST /query - Process a query
  POST /clear - Clear conversation history
  GET  /health - Health check
```

### 3. Start the iMessage Watcher

In terminal 2:

```bash
bun run watch
# or: bun run imessage-watcher.ts
```

You should see:
```
Checking agent API...
✓ Agent API is healthy

======================================================================
iMessage Watcher for Flub Agent
======================================================================
Watching for new messages...
Press Ctrl+C to stop
```

### 4. Test It!

Send a text message to your Mac from another device:

```
"What's the best flight from EWR to LAX on 2025-11-15?"
```

You should see:
1. The watcher detect the message
2. The query sent to the agent API
3. The agent search for flights
4. A response sent back to your phone!

## How It Works

### 1. Message Flow

```typescript
// imessage-watcher.ts watches for new messages
onNewMessage: async (msg: Message) => {
    // Tracks unique phone numbers
    const sender = msg.sender  // e.g., "+1234567890"

    // Sends to agent API
    const response = await queryFlubAgent(sender, msg.text)

    // Sends response back to same number
    await sdk.send(sender, response)
}
```

### 2. Conversation History

Each phone number gets its own agent instance with separate conversation history:

```python
# agent_server.py maintains per-sender history
agents = {}

def get_agent_for_sender(sender: str):
    if sender not in agents:
        agents[sender] = SimpleFlubAgent()  # New conversation
    return agents[sender]
```

### 3. Duplicate Prevention

```typescript
const processedIds = new Set<string>()

// Skip already processed messages
if (processedIds.has(msg.id)) {
    return
}
processedIds.add(msg.id)
```

## API Endpoints

### POST /query

Process a query from a sender.

**Request:**
```json
{
    "sender": "+1234567890",
    "query": "Find flights from NYC to LA on Dec 1st"
}
```

**Response:**
```json
{
    "success": true,
    "response": "I'll help you find flights from NYC to LA..."
}
```

### POST /clear

Clear conversation history for a sender.

**Request:**
```json
{
    "sender": "+1234567890"
}
```

### GET /health

Check if the API is running.

**Response:**
```json
{
    "status": "healthy",
    "active_conversations": 3
}
```

## Configuration

### Change Poll Interval

In `imessage-watcher.ts`:

```typescript
const sdk = new IMessageSDK({
    watcher: {
        pollInterval: 2000,  // Check every 2 seconds (default)
    },
})
```

### Change API Port

In `agent_server.py`:

```python
app.run(host='0.0.0.0', port=3000, debug=False)
```

And in `imessage-watcher.ts`:

```typescript
const AGENT_API_URL = 'http://localhost:3000'
```

## Troubleshooting

### Watcher says "Agent API is not running"

Make sure `agent_server.py` is running in another terminal:
```bash
python agent_server.py
```

### No messages being detected

1. Check that photon-imsg-mcp is working:
```bash
cd ../photon-imsg-mcp
bun run src/cli.ts list
```

2. Make sure you have iMessage permissions enabled

### Messages processed multiple times

This shouldn't happen due to `processedIds` tracking, but if it does:
- Restart the watcher
- The set will reset

### Agent responses are slow

This is normal - the agent needs to:
1. Call Claude API
2. Potentially call the flight search tool
3. Format the response

Typical response time: 2-10 seconds

## Example Conversations

### Flight Search

**You:** "What's the cheapest flight from Newark to LA tomorrow?"

**Agent:** "I'll help you find the cheapest flight from Newark (EWR) to Los Angeles (LAX) tomorrow..."
[Uses find_best_price tool]
"The cheapest flight is Spirit Airlines at $230, departing at 12:04 PM..."

### Multi-turn Conversation

**You:** "Find flights from NYC to Miami on December 1st"

**Agent:** "I'll search for flights from NYC to Miami on December 1st..."

**You:** "What's the cheapest option?"

**Agent:** "Based on our previous search, the cheapest flight is..."
[Maintains context from first message]

## Production Deployment

For production use:

1. **Use a process manager** like PM2:
```bash
pm2 start agent_server.py --interpreter python --name flub-agent-api
pm2 start imessage-watcher.ts --interpreter bun --name imessage-watcher
```

2. **Add logging** to track usage

3. **Set up monitoring** for the API health endpoint

4. **Add rate limiting** to prevent abuse

5. **Secure the API** with authentication if exposing externally

## Next Steps

Now that you have iMessage integration working, you can:

1. **Add more tools** - Weather, news, calendar, etc.
2. **Customize responses** - Modify the agent's system prompt
3. **Add commands** - Implement special commands like `/help`, `/clear`
4. **Monitor usage** - Track which tools are used most
5. **Improve error handling** - Better error messages for users

Enjoy your AI-powered iMessage assistant! 🎉
