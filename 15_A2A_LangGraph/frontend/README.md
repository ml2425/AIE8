# Client-Side LangGraph Agent (A2A Wrapper)

This folder contains a minimal LangGraph client that forwards user input to the server-side agent (in `app/`) via the A2A protocol. The client does not perform its own tool use; it simply wraps the A2A API and supports multi-turn conversations by preserving `context_id` across turns and automatically creating a new `task_id` per turn.

## Quickstart

- Ensure the server is running:
  - `uv run python -m app` (defaults to `http://localhost:10000`)
- Run the client (from repo root):
  - `uv run python -m frontend.client_graph.run`

Tips:
- Type `new` (and press Enter) to start a fresh conversation (clears both IDs).
- By default, after a completed answer, the client keeps the same `context_id` and clears `task_id`, so your follow-up stays in-thread without reusing a terminal task.

## Environment

- `FRONTEND_A2A_BASE_URL` (optional): defaults to `http://localhost:10000`
- `A2A_HTTP_TIMEOUT_SECONDS` (optional): defaults to `60`

## Architecture

- `client_graph/a2a_client.py`: Thin wrapper over A2A client/libs. Extracts `content`, `context_id`, `task_id`, and `completed` (based on `result.status.state`).
- `client_graph/graph.py`: LangGraph nodes:
  - `maybe_reset`: if user types `new` or `/new`, clears IDs and prints a reset message.
  - `call_a2a`: sends the user message to the server via A2A, returns normalized response.
  - `format_response`: extracts a human-readable answer (prefers `artifacts[].parts[].text`) and prints a short meta block (context/task IDs).
- `client_graph/run.py`: CLI loop. Prints formatted output. If the last turn is `completed`, it keeps `context_id` and clears `task_id` to enable follow-ups in the same thread.

## How this “wraps” A2A in LangGraph

We embed an A2A client call inside a LangGraph node (`call_a2a`). The graph handles UX and control flow (reset detection, formatting, carrying conversation state), while the server-side agent (in `app/`) handles all reasoning and tool use. This demonstrates turning an external API (A2A) into a composable LangGraph node.
