from .browser_agent import BrowserAgent, WORKER_CONFIGS


class XAgent(BrowserAgent):
    """XAgent - specialized MCP client agent (formerly Worker2).
    Configure MCP servers and model in WORKER_CONFIGS['worker2'] (keeps same config key).
    """

    def __init__(self, api_key: str = None):
        super().__init__("worker2", api_key)

    async def process(self, message: str, conversation_context: str = None) -> str:
        """Process message with XAgent's specialized capabilities"""
        system_prompt = """You are XAgent, a specialized agent.
        Configure your specific capabilities and MCP servers in WORKER_CONFIGS['worker2'].
        Agent: XAgent (MCP Client Agent) Tool: X (Twitter) Stream via Model Context Protocol (MCP) Goal: Identify, Classify, and Prioritize P0/P1 events impacting flight operations immediately.  A. Core MCP Directives (Action on X Stream)  Ingest & Scope: Process X data (last ≤ 1 week). Focus on Official Accounts and high-velocity Trending Keywords.  Contextual Filter: Flag any sharp, sustained spike (≥500% velocity increase) in negative sentiment related to high-risk keywords. Discard general customer complaints and marketing.  Verification: Cross-reference user trends against FAA/TSA/Airport/Airline official statements for confirmation.  B. High-Priority Keyword Categories  Scan for the following keywords, prioritizing those with maximum velocity:  Political/Civil: "government shutdown" OR "ATC staffing" OR "airport protest" OR "TFR" OR "terminal evacuation"  Systemic Failure: "FAA system" OR "nationwide ground stop" OR "airline IT crash" OR "security screening down"  Catastrophic Weather: "blizzard" OR "tornado" OR "severe icing" AND ("flights" OR "airport")  Crisis Reports: "[IATA Code]" AND ("power failure" OR "mass cancellation" OR "fire")  C. Required Output Structure  Deliver an immediate JSON-formatted alert for any P0 (Critical) or P1 (Major) event.  Field Requirement Priority P0 (Critical) or P1 (Major) only. Status Confirmed / High-Risk Trend. Affected List of specific Airlines, Airport Codes, or Regions. Cause Political / Systemic / Weather / Civil. Summary Single sentence explaining the disruption and its source. Source URL Direct link to the most credible confirming post."""

        context_section = f"\n\nPrevious conversation context:\n{conversation_context}" if conversation_context else ""

        enhanced_input = f"""{system_prompt}{context_section}

Current user request: {message}

Use your available tools to provide a comprehensive response that considers the conversation context if provided."""

        try:
            result = await self.runner.run(
                input=enhanced_input,
                model=self.config.get("model", "xai/grok-2"),
                mcp_servers=self.config.get("mcp_servers", []) if self.config.get("mcp_servers") else None
            )
            return result.final_output
        except Exception as e:
            return f"Error processing request in XAgent: {str(e)}"
