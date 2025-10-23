"""
LangGraph Agent for MCP Server Integration
Natural language interface to MCP tools (weather, dice, web search)
"""

import asyncio
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from fastmcp import Client
import re


class AgentState(TypedDict):
    """State for the LangGraph agent"""
    user_input: str
    intent: str  # "weather", "dice", "search", "unknown"
    extracted_params: dict  # {"place": "Paris"} or {"notation": "3d6"}
    tool_result: str
    final_response: str


class MCPAgent:
    """LangGraph agent that interfaces with MCP server tools"""
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_intent", self.classify_intent)
        workflow.add_node("call_mcp_tool", self.call_mcp_tool)
        workflow.add_node("format_response", self.format_response)
        
        # Add edges
        workflow.set_entry_point("classify_intent")
        workflow.add_edge("classify_intent", "call_mcp_tool")
        workflow.add_edge("call_mcp_tool", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def classify_intent(self, state: AgentState) -> AgentState:
        """Classify user intent and extract parameters"""
        user_input = state["user_input"].lower()
        
        # Weather patterns
        weather_patterns = [
            r"weather.*in\s+(\w+)",
            r"what.*weather.*(\w+)",
            r"temperature.*in\s+(\w+)",
            r"how.*weather.*(\w+)",
            r"climate.*in\s+(\w+)"
        ]
        
        for pattern in weather_patterns:
            match = re.search(pattern, user_input)
            if match:
                place = match.group(1).strip()
                return {
                    **state,
                    "intent": "weather",
                    "extracted_params": {"place": place}
                }
        
        # Default to unknown for now
        return {
            **state,
            "intent": "unknown",
            "extracted_params": {}
        }
    
    async def call_mcp_tool(self, state: AgentState) -> AgentState:
        """Call the appropriate MCP tool based on intent"""
        intent = state["intent"]
        params = state["extracted_params"]
        
        try:
            async with Client("server.py") as client:
                if intent == "weather":
                    result = await client.call_tool("weather_by_place", params)
                    tool_result = str(result)
                else:
                    tool_result = f"Unknown intent: {intent}"
                
                return {
                    **state,
                    "tool_result": tool_result
                }
        except Exception as e:
            return {
                **state,
                "tool_result": f"Error calling MCP tool: {str(e)}"
            }
    
    def format_response(self, state: AgentState) -> AgentState:
        """Format the tool result into a user-friendly response"""
        tool_result = state["tool_result"]
        intent = state["intent"]
        
        if intent == "weather":
            # Extract summary from weather result
            import json
            try:
                # Parse the CallToolResult to extract the actual content
                if "summary" in tool_result:
                    # Extract the JSON content from the CallToolResult
                    start_idx = tool_result.find('"summary": "') + 12
                    end_idx = tool_result.find('"', start_idx)
                    if start_idx > 11 and end_idx > start_idx:
                        summary = tool_result[start_idx:end_idx]
                        final_response = f"Weather information: {summary}"
                    else:
                        final_response = f"Weather data: {tool_result}"
                else:
                    final_response = f"Weather data: {tool_result}"
            except:
                final_response = f"Weather information: {tool_result}"
        else:
            final_response = tool_result
        
        return {
            **state,
            "final_response": final_response
        }
    
    async def run(self, user_input: str) -> str:
        """Run the agent with user input"""
        initial_state = {
            "user_input": user_input,
            "intent": "",
            "extracted_params": {},
            "tool_result": "",
            "final_response": ""
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result["final_response"]


async def main():
    """Test the agent"""
    agent = MCPAgent()
    
    # Test weather query
    test_query = "What's the weather in Paris?"
    print(f"Query: {test_query}")
    response = await agent.run(test_query)
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
