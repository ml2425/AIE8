import asyncio
from typing import Dict, Any

from frontend.client_graph.graph import build_client_graph


async def main() -> None:
    print("Client LangGraph (A2A wrapper). Type 'exit' to quit. Type 'new' to start a fresh conversation.\n")
    task_id = None
    context_id = None
    graph = build_client_graph()

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in {"exit", "quit"}:
            print("Bye!")
            break

        state: Dict[str, Any] = {
            "user_message": user_text,
            "task_id": task_id,
            "context_id": context_id,
        }

        result = await graph.ainvoke(state)

        # Prefer formatted outputs if present
        display = result.get("formatted_display")
        meta = result.get("formatted_meta")
        if display:
            print(f"Agent: {display}")
            if meta:
                print("\n" + meta)
        else:
            # Fallback to raw content
            agent_response = result.get("agent_response", {})
            content = agent_response.get("content")
            if content:
                print(f"Agent: {content}")

        # Carry forward IDs for multi-turn. If the last task completed,
        # clear task_id so the next turn creates a new task in the same context.
        agent_response = result.get("agent_response", {})
        context_id = agent_response.get("context_id", context_id)
        if agent_response.get("completed") is True:
            task_id = None
        else:
            task_id = agent_response.get("task_id", task_id)


if __name__ == "__main__":
    asyncio.run(main())


