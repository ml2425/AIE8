from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import StateGraph, END

from .a2a_client import SimpleA2AClient


class ClientState(TypedDict, total=False):
    user_message: str
    task_id: Optional[str]
    context_id: Optional[str]
    agent_response: Dict[str, Any]
    # For internal routing
    _a2a_client: Any
    reset_triggered: bool
    # Formatted outputs
    formatted_display: str
    formatted_meta: str


async def call_a2a_node(state: ClientState) -> ClientState:
    text = state.get("user_message", "").strip()
    if not text:
        return state

    client = state.get("_a2a_client")  # type: ignore[assignment]
    if client is None:
        client = SimpleA2AClient()
        await client.ainit()
        state["_a2a_client"] = client  # type: ignore[index]

    result = await client.send_message(text, task_id=state.get("task_id"), context_id=state.get("context_id"))
    state["agent_response"] = result
    state["task_id"] = result.get("task_id")
    state["context_id"] = result.get("context_id")
    return state


def maybe_reset_node(state: ClientState) -> ClientState:
    """If the user typed 'new' or '/new', clear context and set a friendly message.

    Keeps this logic separate from network and formatting nodes.
    """
    text = state.get("user_message", "").strip().lower()
    if text in {"new", "/new"}:
        state["task_id"] = None
        state["context_id"] = None
        state["reset_triggered"] = True
        state["agent_response"] = {  # minimal shape for formatter
            "content": "Started a new conversation."
        }
    else:
        state["reset_triggered"] = False
    return state


def format_response_node(state: ClientState) -> ClientState:
    """Produce a human-friendly display block plus a compact metadata block."""
    resp = state.get("agent_response", {}) or {}
    display = resp.get("content")

    # If content looks like a JSON blob, try to parse and extract artifacts text
    if isinstance(display, str) and display.strip().startswith("{"):
        try:
            import json

            data = json.loads(display)
            result = data.get("result") if isinstance(data, dict) else None
            if result and isinstance(result, dict):
                artifacts = result.get("artifacts")
                if isinstance(artifacts, list) and artifacts:
                    first = artifacts[0]
                    parts = first.get("parts") if isinstance(first, dict) else None
                    if isinstance(parts, list):
                        for part in parts:
                            if isinstance(part, dict) and part.get("kind") == "text":
                                text_val = part.get("text")
                                if isinstance(text_val, str) and text_val.strip():
                                    display = text_val
                                    break
        except Exception:
            # If parsing fails, keep original content as-is
            pass

    # Build a small meta block
    task_id = state.get("task_id")
    context_id = state.get("context_id")
    meta_lines = []
    if context_id:
        meta_lines.append(f"context_id: {context_id}")
    if task_id:
        meta_lines.append(f"task_id: {task_id}")
    meta_text = "\n".join(meta_lines)

    state["formatted_display"] = display or "(no content)"
    state["formatted_meta"] = meta_text
    return state


def _route_after_reset(state: ClientState) -> str:
    return "format_response" if state.get("reset_triggered") else "call_a2a"


def build_client_graph():
    graph = StateGraph(ClientState)
    graph.add_node("maybe_reset", maybe_reset_node)
    graph.add_node("call_a2a", call_a2a_node)
    graph.add_node("format_response", format_response_node)

    graph.set_entry_point("maybe_reset")
    graph.add_conditional_edges("maybe_reset", _route_after_reset, {
        "format_response": "format_response",
        "call_a2a": "call_a2a",
    })
    graph.add_edge("call_a2a", "format_response")
    graph.add_edge("format_response", END)
    return graph.compile()


