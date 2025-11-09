import asyncio
import os
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
from workers import Worker1, Worker2, Worker3

load_dotenv()

# Configuration for Orchestrator Agent
ORCHESTRATOR_AGENT_CONFIG = {
    "model": "openai/gpt-4.1",  # Change this to your preferred model
    "mcp_servers": [
        # Add MCP servers for orchestrator (general) agent here
        # Example: "dedalus-labs/brave-search",
    ]
}


# ============================================================================
# ORCHESTRATOR AGENT (FORMERLY GENERAL AGENT)
# ============================================================================

class OrchestratorAgent:
    """
    OrchestratorAgent that intakes messages and routes them to appropriate worker agents.
    Has fallback capability to respond directly if routing is unclear.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("DEDALUS_API_KEY") or os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set DEDALUS_API_KEY or API_KEY in your .env file")
        
        self.client = AsyncDedalus(api_key=self.api_key)
        self.runner = DedalusRunner(self.client)
        self.config = ORCHESTRATOR_AGENT_CONFIG
        
        # State machine pattern: Store context and conversation history
        self.context = {
            "conversation_history": []  # List of {"role": "user"/"assistant", "content": "..."}
        }
        
        # Initialize worker agents
        self.worker1 = Worker1(api_key=self.api_key)
        self.worker2 = Worker2(api_key=self.api_key)
        self.worker3 = Worker3(api_key=self.api_key)
    
    def _get_conversation_context(self, max_messages: int = 10) -> str:
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
        self.context["conversation_history"].append({
            "role": role,
            "content": content
        })
    
    def clear_history(self):
        self.context["conversation_history"] = []
    
    async def route_message(self, message: str) -> str:
        # Add user message to conversation history
        self._add_to_history("user", message)
        
        # Get conversation context
        conversation_context = self._get_conversation_context()
        
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
            routing_result = await self.runner.run(
                input=routing_prompt,
                model=self.config["model"],
                mcp_servers=self.config["mcp_servers"] if self.config["mcp_servers"] else None
            )
            
            worker_choice = routing_result.final_output.strip().upper()
            selected_workers = [w.strip() for w in worker_choice.split(",")]
            
            valid_workers = []
            worker_map = {
                "WORKER1": self.worker1,
                "WORKER2": self.worker2,
                "WORKER3": self.worker3
            }
            
            for worker_name in selected_workers:
                if worker_name in worker_map:
                    valid_workers.append((worker_name, worker_map[worker_name]))
            
            if len(valid_workers) == 0:
                response = await self._fallback_response(message)
            elif len(valid_workers) == 1:
                _, worker = valid_workers[0]
                response = await worker.process(message, conversation_context)
            else:
                response = await self._process_parallel(message, valid_workers, conversation_context)
            
            self._add_to_history("assistant", response)
            return response
        except Exception as e:
            print(f"Error in routing: {e}")
            response = await self._fallback_response(message)
            self._add_to_history("assistant", response)
            return response
    
    async def _process_parallel(self, message: str, workers: list, conversation_context: str) -> str:
        worker_names = [name for name, _ in workers]
        worker_instances = [worker for _, worker in workers]
        
        print(f"Processing with {len(workers)} workers in parallel: {', '.join(worker_names)}")
        
        try:
            results = await asyncio.gather(
                *[worker.process(message, conversation_context) for worker in worker_instances],
                return_exceptions=True
            )
            
            worker_outputs = []
            for i, (worker_name, result) in enumerate(zip(worker_names, results)):
                if isinstance(result, Exception):
                    worker_outputs.append(f"{worker_name}: Error - {str(result)}")
                else:
                    worker_outputs.append(f"{worker_name}: {result}")
            
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
            if 'worker_outputs' in locals() and worker_outputs:
                return f"Processed with {len(workers)} workers. Results:\n\n" + "\n\n".join(worker_outputs)
            else:
                return f"Error processing with multiple workers: {str(e)}"
    
    async def _fallback_response(self, message: str) -> str:
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

# Global OrchestratorAgent instance to maintain conversation history
_orchestrator_agent: OrchestratorAgent = None

def get_global_agent() -> OrchestratorAgent:
    """Get or create global OrchestratorAgent instance to maintain conversation history."""
    global _orchestrator_agent
    if _orchestrator_agent is None:
        _orchestrator_agent = OrchestratorAgent()
    return _orchestrator_agent

async def process_message(message: str) -> str:
    """
    Main entry point for processing a message through the multi-agent pipeline.
    Uses a persistent OrchestratorAgent instance to maintain conversation history.
    """
    orchestrator = get_global_agent()
    return await orchestrator.route_message(message)

def clear_conversation():
    """Clear conversation history."""
    global _orchestrator_agent
    if _orchestrator_agent:
        _orchestrator_agent.clear_history()


async def main():
    """Test the multi-agent pipeline"""
    test_message = "I want to plan a trip to Paris on a sunny day"
    print(f"Processing message: {test_message}\n")
    
    response = await process_message(test_message)
    print(f"Response:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
