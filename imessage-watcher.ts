/**
 * iMessage Watcher for Flub Agent
 *
 * Behaviors:
 * 1. Text received -> Send to Flub Agent API -> Reply with agent response
 * 2. Maintains conversation history per phone number (via API)
 *
 * Requirements:
 * 1. Install: bun add @photon-ai/imessage-kit
 * 2. Start the agent API server: python agent_server.py
 * 3. Run this watcher: bun run imessage-watcher.ts
 */

import { IMessageSDK, type Message } from '@photon-ai/imessage-kit'

declare const process: any

const AGENT_API_URL = 'http://localhost:3000'
const processedIds = new Set<string>()

/**
 * Call the Flub Agent API with a query
 */
async function queryFlubAgent(sender: string, query: string): Promise<string> {
    const response = await fetch(`${AGENT_API_URL}/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sender,
            query,
        }),
    })

    if (!response.ok) {
        throw new Error(`Agent API returned ${response.status}`)
    }

    const data = await response.json()

    if (!data.success) {
        throw new Error(data.error || 'Unknown error')
    }

    return data.response
}

/**
 * Check if the agent API is healthy
 */
async function checkAgentHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${AGENT_API_URL}/health`)
        return response.ok
    } catch {
        return false
    }
}

async function main() {
    // Check if agent API is running
    console.log('Checking agent API...')
    const isHealthy = await checkAgentHealth()

    if (!isHealthy) {
        console.error('\n✗ Agent API is not running!')
        console.error('Please start it first: python agent_server.py\n')
        process.exit(1)
    }

    console.log('✓ Agent API is healthy\n')

    const sdk = new IMessageSDK({
        debug: false,
        watcher: {
            pollInterval: 2000,
        },
    })

    console.log('='.repeat(70))
    console.log('iMessage Watcher for Flub Agent')
    console.log('='.repeat(70))
    console.log('Watching for new messages...')
    console.log('Press Ctrl+C to stop\n')

    await sdk.startWatching({
        onNewMessage: async (msg: Message) => {
            // Skip if already processed
            if (processedIds.has(msg.id)) {
                return
            }

            processedIds.add(msg.id)

            // Prevent memory leak by limiting processed IDs cache size
            if (processedIds.size > 1000) {
                const ids = Array.from(processedIds)
                processedIds.clear()
                ids.slice(-500).forEach(id => processedIds.add(id))
            }

            // Only handle text messages
            if (!msg.text?.trim()) {
                return
            }

            const timestamp = new Date().toLocaleTimeString()
            console.log(`\n[${timestamp}] New message from: ${msg.sender}`)
            console.log(`  Message: ${msg.text}`)

            try {
                // Query the Flub Agent via API
                console.log(`  Processing with Flub Agent...`)
                const response = await queryFlubAgent(msg.sender, msg.text)

                // Log response preview
                const preview = response.length > 100
                    ? response.substring(0, 100) + '...'
                    : response
                console.log(`  Agent response: ${preview}`)

                // Send response back
                await sdk.send(msg.sender, response)
                console.log(`  ✓ Sent response to ${msg.sender}`)

                // Small delay between messages
                await new Promise(r => setTimeout(r, 500))

            } catch (error) {
                console.error(`  ✗ Error: ${error}`)

                // Send error message to user
                try {
                    await sdk.send(
                        msg.sender,
                        "Sorry, I encountered an error processing your request. Please try again."
                    )
                } catch (sendError) {
                    console.error(`  ✗ Failed to send error message: ${sendError}`)
                }
            }
        },

        onError: (error) => {
            console.error(`\n✗ Watcher error: ${error.message}`)
        },
    })

    const stopHandler = async () => {
        console.log('\n\nStopping watcher...')
        sdk.stopWatching()
        await sdk.close()
        console.log(`Processed ${processedIds.size} messages`)
        console.log('Stopped\n')
        if (typeof process !== 'undefined') {
            process.exit(0)
        }
    }

    if (typeof process !== 'undefined') {
        process.on('SIGINT', stopHandler)
        process.on('SIGTERM', stopHandler)
    }
}

main().catch((error) => {
    console.error('Fatal error:', error)
    if (typeof process !== 'undefined') {
        process.exit(1)
    }
})
