'''
Minimal, production-lean code
A) Direct A2A call from a LangGraph node (Python)
Use a normal node/handoff that calls your A2A server via JSON-RPC. Keep it pure I/O so it’s easy to retry/trace.
'''
from typing import TypedDict, Annotated, Sequence
import asyncio, uuid, httpx
from langgraph.graph import StateGraph, END

A2A_URL = "http://localhost:10000/jsonrpc"  # your A2A server

class AgentState(TypedDict):
    messages: Annotated[Sequence[dict], "conversation history"]

async def a2a_send(message: dict) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "method": "message.send",
        "params": {"message": message},
        "id": str(uuid.uuid4()),
    }
    async with httpx.AsyncClient(timeout=60) as cli:
        r = await cli.post(A2A_URL, json=payload)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(data["error"])
        return data["result"]

async def call_remote_agent(state: AgentState) -> AgentState:
    user_msg = next(m for m in reversed(state["messages"]) if m["role"] == "user")
    result = await a2a_send({
        "role": "user",
        "parts": [{"kind": "text", "text": user_msg["content"]}],
        "message_id": uuid.uuid4().hex,
    })
    # Normalize A2A's response into your state schema
    content = result.get("content") or result.get("text") or str(result)
    return {"messages": [*state["messages"], {"role": "assistant", "content": content}]}

# Graph
graph = StateGraph(AgentState)
graph.add_node("remote_a2a", call_remote_agent)
graph.set_entry_point("remote_a2a")
graph.add_edge("remote_a2a", END)
app = graph.compile()

# Notes
# If your A2A server streams, replace a2a_send with an async generator consuming SSE and build up the assistant message before returning.
# Wrap with retries/jitter and log a corr_id (UUID) into LangSmith run metadata for observability.

#B) Using MCP adapters (preferred when available)
#If your remote exposes MCP (or you add a shim), you can load tools and let the graph’s agent do tool-use natively.


from langchain_mcp_adapters import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio

async def build_agent():
    async with MultiServerMCPClient.from_servers([
        # stdio or streamable-http
        {"transport": "streamable-http", "url": "https://mcp.your-host.com/mcp"},
    ]) as mcp:
        tools = await mcp.get_tools()
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        agent = create_react_agent(llm, tools)   # tools are MCP-backed
        return agent

# agent = asyncio.run(build_agent())


#LangGraph/LC officially support this path; you get multi-server discovery, streaming, auth headers, etc. out of the box. (Langchain AI)
#LangGraph Server can expose your graph as an MCP endpoint at /mcp, so other frameworks (or your own graphs) can use it as a tool. (LangChain Docs)
