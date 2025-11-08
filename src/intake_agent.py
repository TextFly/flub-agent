import asyncio
import os
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
from workers import Worker1, Worker2, Worker3

load_dotenv()

# Configuration for General Agent
GENERAL_AGENT_CONFIG = {
    "model": "openai/gpt-4.1",  # Change this to your preferred model
    "mcp_servers": [
        # Add MCP servers for general agent here
        # Example: "dedalus-labs/brave-search",
    ]
}


# ============================================================================
# GENERAL AGENT (ORCHESTRATOR)
# ============================================================================

class GeneralAgent:
    """
    General agent that intakes messages and routes them to appropriate worker agents.
    Has fallback capability to respond directly if routing is unclear.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("DEDALUS_API_KEY") or os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set DEDALUS_API_KEY or API_KEY in your .env file")
        
        self.client = AsyncDedalus(api_key=self.api_key)
        self.runner = DedalusRunner(self.client)
        self.config = GENERAL_AGENT_CONFIG
        
        # State machine pattern: Store context and conversation history
        self.context = {
            "conversation_history": []  # List of {"role": "user"/"assistant", "content": "..."}
        }
        
        # Initialize worker agents
        self.worker1 = Worker1(api_key=self.api_key)
        self.worker2 = Worker2(api_key=self.api_key)
        self.worker3 = Worker3(api_key=self.api_key)
    
    def _get_conversation_context(self, max_messages: int = 10) -> str:
        """
        Get formatted conversation history for context.
        
        Args:
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Formatted conversation history string
        """
        history = self.context["conversation_history"]
        recent_history = history[-max_messages:] if len(history) > max_messages else history
        
        if not recent_history:
            return "No previous conversation."
        
        context_lines = []
        for msg in recent_history:
            role = msg["role"].upper()
            content = msg["content"]
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def _add_to_history(self, role: str, content: str):
        """Add a message to conversation history."""
        self.context["conversation_history"].append({
            "role": role,
            "content": content
        })
    
    def clear_history(self):
        """Clear conversation history."""
        self.context["conversation_history"] = []
    
    async def route_message(self, message: str) -> str:
        """
        Routes a message to the appropriate worker agent(s).
        Can use single worker, multiple workers in parallel, or fallback to general agent.
        Maintains conversation history in self.context.
        
        Args:
            message: The user's message string
            
        Returns:
            Response string from worker agent(s) or general agent
        """
        # Add user message to conversation history
        self._add_to_history("user", message)
        
        # Get conversation context
        conversation_context = self._get_conversation_context()
        
        # Step 1: Determine which worker(s) should handle this message
        routing_prompt = f"""Analyze this message and determine which worker agent(s) should handle it.

Previous conversation context:
{conversation_context}

Available workers:
- WORKER1: Weather agent - Checks weather conditions for specific dates and locations, identifies sunny/clear days for flight planning
- WORKER2: Specialized for specific tasks (configure MCP servers and model in WORKER_CONFIGS)
- WORKER3: Specialized for specific tasks (configure MCP servers and model in WORKER_CONFIGS)

Current user message: {message}

You can respond with:
- A single worker: WORKER1, WORKER2, or WORKER3
- Multiple workers (comma-separated): WORKER1,WORKER2 or WORKER1,WORKER2,WORKER3
- UNKNOWN if you cannot determine

If the message requires multiple perspectives or different types of information, use multiple workers.
If the message is unclear or doesn't fit any worker, respond with UNKNOWN.
Consider the conversation context when making your decision.

Examples:
- Simple query: "WORKER1"
- Complex query needing multiple perspectives: "WORKER1,WORKER2"
- Very complex query: "WORKER1,WORKER2,WORKER3"
"""

        try:
            # Use general agent to determine routing
            routing_result = await self.runner.run(
                input=routing_prompt,
                model=self.config["model"],
                mcp_servers=self.config["mcp_servers"] if self.config["mcp_servers"] else None
            )
            
            worker_choice = routing_result.final_output.strip().upper()
            
            # Parse worker selection (can be single or multiple)
            selected_workers = [w.strip() for w in worker_choice.split(",")]
            
            # Filter valid workers
            valid_workers = []
            worker_map = {
                "WORKER1": self.worker1,
                "WORKER2": self.worker2,
                "WORKER3": self.worker3
            }
            
            for worker_name in selected_workers:
                if worker_name in worker_map:
                    valid_workers.append((worker_name, worker_map[worker_name]))
            
            # Route based on number of workers
            if len(valid_workers) == 0:
                # Fallback: General agent responds directly
                response = await self._fallback_response(message)
            elif len(valid_workers) == 1:
                # Single worker - process sequentially
                _, worker = valid_workers[0]
                response = await worker.process(message, conversation_context)
            else:
                # Multiple workers - process in parallel
                response = await self._process_parallel(message, valid_workers, conversation_context)
            
            # Add assistant response to conversation history
            self._add_to_history("assistant", response)
            return response
                
        except Exception as e:
            print(f"Error in routing: {e}")
            # Fallback on error
            response = await self._fallback_response(message)
            self._add_to_history("assistant", response)
            return response
    
    async def _process_parallel(self, message: str, workers: list, conversation_context: str) -> str:
        """
        Process message using multiple workers in parallel, then synthesize results.
        
        Args:
            message: The user's message
            workers: List of (worker_name, worker_instance) tuples
            conversation_context: Previous conversation history
            
        Returns:
            Synthesized response string combining all worker outputs
        """
        worker_names = [name for name, _ in workers]
        worker_instances = [worker for _, worker in workers]
        
        print(f"Processing with {len(workers)} workers in parallel: {', '.join(worker_names)}")
        
        # Run all workers in parallel with conversation context
        try:
            results = await asyncio.gather(
                *[worker.process(message, conversation_context) for worker in worker_instances],
                return_exceptions=True
            )
            
            # Collect successful results
            worker_outputs = []
            for i, (worker_name, result) in enumerate(zip(worker_names, results)):
                if isinstance(result, Exception):
                    worker_outputs.append(f"{worker_name}: Error - {str(result)}")
                else:
                    worker_outputs.append(f"{worker_name}: {result}")
            
            # Synthesize the results using the general agent
            synthesis_prompt = f"""You are synthesizing responses from multiple specialized workers.

Previous conversation context:
{conversation_context}

Original user request: {message}

Worker responses:
{chr(10).join(worker_outputs)}

Synthesize these responses into a single, coherent, and comprehensive answer.
Combine the information from all workers, eliminate redundancy, and present a unified response.
If there are conflicting views, acknowledge them and provide a balanced perspective.
Make sure the final response directly addresses the user's original request and considers the conversation context."""
            
            synthesis_result = await self.runner.run(
                input=synthesis_prompt,
                model=self.config["model"],
                mcp_servers=self.config["mcp_servers"] if self.config["mcp_servers"] else None
            )
            
            return synthesis_result.final_output
            
        except Exception as e:
            print(f"Error in parallel processing: {e}")
            # Fallback: Try to return individual results if available
            if 'worker_outputs' in locals() and worker_outputs:
                return f"Processed with {len(workers)} workers. Results:\n\n" + "\n\n".join(worker_outputs)
            else:
                return f"Error processing with multiple workers: {str(e)}"
    
    async def _fallback_response(self, message: str) -> str:
        """
        Fallback method: General agent responds directly when routing fails.
        
        Args:
            message: The user's message
            
        Returns:
            Response string from general agent
        """
        conversation_context = self._get_conversation_context()
        
        fallback_prompt = f"""You are a helpful assistant. Respond to the user's message directly and helpfully.

Previous conversation context:
{conversation_context}

Current user message: {message}

Provide a helpful response that considers the conversation context."""
        
        try:
            result = await self.runner.run(
                input=fallback_prompt,
                model=self.config["model"],
                mcp_servers=self.config["mcp_servers"] if self.config["mcp_servers"] else None
            )
            return result.final_output
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}"


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

# Global GeneralAgent instance to maintain conversation history
_global_agent: GeneralAgent = None

def get_global_agent() -> GeneralAgent:
    """Get or create global GeneralAgent instance to maintain conversation history."""
    global _global_agent
    if _global_agent is None:
        _global_agent = GeneralAgent()
    return _global_agent

async def process_message(message: str) -> str:
    """
    Main entry point for processing a message through the multi-agent pipeline.
    Uses a persistent GeneralAgent instance to maintain conversation history.
    
    Args:
        message: The user's message string
        
    Returns:
        Response string from the appropriate agent
    """
    general_agent = get_global_agent()
    return await general_agent.route_message(message)

def clear_conversation():
    """Clear conversation history."""
    global _global_agent
    if _global_agent:
        _global_agent.clear_history()


async def main():
    """Test the multi-agent pipeline"""
    # Example usage
    test_message = "I want to plan a trip to Paris on a sunny day"
    print(f"Processing message: {test_message}\n")
    
    response = await process_message(test_message)
    print(f"Response:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
