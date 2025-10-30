Short answer: **LangGraph doesn’t (yet) ship a first-class A2A wrapper.** Today you’ve got three pragmatic patterns:

1. **Use MCP as the bridge** (recommended when the remote exposes MCP or you can add an adapter).
   LangGraph has mature, supported MCP adapters (multi-server, streamable HTTP/stdio). You can expose your graph as MCP and/or consume MCP tools inside a graph. ([Langchain AI][1])

2. **Call A2A directly from a node** (custom “handoff” node).
   Treat the A2A agent like a remote service (JSON-RPC/SSE). This is a small amount of glue code and works today.

3. **Run an adapter service** (A2A⇄MCP shim).
   Present A2A agents as MCP tools (or vice-versa) so you can stay on the happy path with LangGraph’s MCP support. Community packages exist that advertise LangGraph compatibility. ([PyPI][2])

There are community requests for **native A2A nodes/sub-graphs** in LangGraph, but they’re not part of the public, stable API yet. ([LangChain Forum][3])

---

# Minimal, production-lean code

## A) Direct A2A call from a LangGraph node (Python)

Use a normal node/handoff that calls your A2A server via JSON-RPC. Keep it pure I/O so it’s easy to retry/trace.

```python
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
```

**Notes**

* If your A2A server streams, replace `a2a_send` with an async generator consuming SSE and build up the assistant message before returning.
* Wrap with retries/jitter and log a `corr_id` (UUID) into LangSmith run metadata for observability.

## B) Using MCP adapters (preferred when available)

If your remote exposes MCP (or you add a shim), you can load tools and let the graph’s agent do tool-use natively.

```python
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
```

* LangGraph/LC officially support this path; you get multi-server discovery, streaming, auth headers, etc. out of the box. ([Langchain AI][1])
* LangGraph Server can **expose your graph as an MCP endpoint** at `/mcp`, so other frameworks (or your own graphs) can use it as a tool. ([LangChain Docs][4])

---

# When to choose which

* **You control both sides** or can add adapters → **MCP route** (cleanest, best-supported; future-proof in LangGraph). ([Langchain AI][1])
* **You must talk to a raw A2A server** with no MCP → implement the small **handoff node** (snippet A).
* **Heterogeneous estate** (A2A + MCP + others) → run a small **A2A⇄MCP shim** so agents appear as tools. Community packages advertise this pattern. ([PyPI][2])

---

# Related LangGraph work

* LangGraph’s broader **Agent Protocol**/interoperability push (runs/threads/memory) points in the same direction, but it’s distinct from A2A. Useful context if you’re designing for cross-framework federation. ([LangChain Changelog][5])

---

If you share the exact A2A server semantics (method names, streaming shape), I can drop in a streaming-aware version of the node and a tiny “capability cache” so the graph lazily discovers the remote’s skills once and avoids prompt/token bloat on every call.

[1]: https://langchain-ai.github.io/langgraph/agents/mcp/?utm_source=chatgpt.com "Use MCP"
[2]: https://pypi.org/project/universal-a2a-agent/0.1.3/?utm_source=chatgpt.com "universal-a2a-agent · PyPI"
[3]: https://forum.langchain.com/t/native-support-for-a2a-protocol/1302?utm_source=chatgpt.com "Native Support for A2A Protocol - LangGraph - LangChain Forum"
[4]: https://docs.langchain.com/langgraph-platform/server-mcp?utm_source=chatgpt.com "MCP endpoint in LangGraph Server - Docs by LangChain"
[5]: https://changelog.langchain.com/announcements/langgraph-agent-protocol-langgraph-studio-for-local-execution?utm_source=chatgpt.com "LangChain - Changelog | 🤖 LangGraph Agent Protocol + LangGraph Studio"
