#!/usr/bin/env python3
"""
Simple HTTP API server for Flub Agent

Provides a REST API that the TypeScript iMessage watcher can call.
Much more efficient than spawning Python processes.

Usage:
    python agent_server.py

Then POST to http://localhost:3000/query with:
    {"sender": "+1234567890", "query": "What is the best flight from EWR to LAX?"}
"""

import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.simple_agent import SimpleFlubAgent
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Maintain separate agent instances per sender (conversation history)
agents = {}


def get_agent_for_sender(sender: str) -> SimpleFlubAgent:
    """Get or create agent instance for a sender."""
    if sender not in agents:
        agents[sender] = SimpleFlubAgent()
    return agents[sender]


@app.route('/query', methods=['POST'])
def query():
    """
    Process a query from a sender.

    Body:
        {
            "sender": "+1234567890",
            "query": "What is the best flight from EWR to LAX?"
        }

    Returns:
        {
            "success": true,
            "response": "The best flight is..."
        }
    """
    try:
        data = request.json

        if not data:
            return jsonify({"success": False, "error": "No JSON body provided"}), 400

        sender = data.get('sender')
        query = data.get('query')

        if not sender or not query:
            return jsonify({
                "success": False,
                "error": "Both 'sender' and 'query' are required"
            }), 400

        # Get agent for this sender
        agent = get_agent_for_sender(sender)

        # Process the query
        response = agent.process(query)

        return jsonify({
            "success": True,
            "response": response
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/clear', methods=['POST'])
def clear_history():
    """
    Clear conversation history for a sender.

    Body:
        {
            "sender": "+1234567890"
        }
    """
    try:
        data = request.json
        sender = data.get('sender')

        if not sender:
            return jsonify({"success": False, "error": "'sender' is required"}), 400

        if sender in agents:
            agents[sender].clear_history()
            return jsonify({"success": True, "message": "History cleared"})
        else:
            return jsonify({"success": True, "message": "No history found"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "active_conversations": len(agents)
    })


if __name__ == '__main__':
    print("=" * 70)
    print("Flub Agent API Server")
    print("=" * 70)
    print("Starting server on http://localhost:3000")
    print("Endpoints:")
    print("  POST /query - Process a query")
    print("  POST /clear - Clear conversation history")
    print("  GET  /health - Health check")
    print()

    app.run(host='0.0.0.0', port=3000, debug=False)
