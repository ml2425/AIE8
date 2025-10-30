from typing import Any, Dict, Optional
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import AgentCard, MessageSendParams, SendMessageRequest
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

from .settings import get_base_url, get_timeout_seconds


class SimpleA2AClient:
    """Thin wrapper around the A2A client used by the frontend graph.

    Responsibilities:
    - Resolve AgentCard from the server
    - Send a message and return normalized fields for the graph
    """

    def __init__(self) -> None:
        base_url = get_base_url()
        timeout = get_timeout_seconds()
        self._httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))
        self._resolver = A2ACardResolver(httpx_client=self._httpx_client, base_url=base_url)
        self._agent_card: Optional[AgentCard] = None
        self._client: Optional[A2AClient] = None

    async def ainit(self) -> None:
        # Fetch the public agent card
        self._agent_card = await self._resolver.get_agent_card(AGENT_CARD_WELL_KNOWN_PATH)
        self._client = A2AClient(httpx_client=self._httpx_client, agent_card=self._agent_card)

    async def aclose(self) -> None:
        await self._httpx_client.aclose()

    async def send_message(
        self,
        text: str,
        task_id: Optional[str] = None,
        context_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        assert self._client is not None, "Client not initialized; call ainit() first."

        payload: Dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "message_id": uuid4().hex,
            }
        }
        if task_id:
            payload["message"]["task_id"] = task_id
        if context_id:
            payload["message"]["context_id"] = context_id

        request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**payload))
        response = await self._client.send_message(request)

        # Normalize a minimal view for the graph.
        # The server's agent packs helpful state in result fields.
        root = response.root
        result = root.result if hasattr(root, "result") else None
        content_text = None
        new_task_id = None
        new_context_id = None
        completed = None

        if result is not None:
            new_task_id = getattr(result, "id", None)
            new_context_id = getattr(result, "context_id", None)
            # Best-effort extraction of textual content
            if getattr(result, "final", None) and getattr(result.final, "parts", None):
                for part in result.final.parts:
                    if getattr(part, "kind", None) == "text":
                        content_text = getattr(part, "text", None)
                        break

        # Capture completion state if available
        if result is not None and getattr(result, "status", None):
            status = getattr(result, "status")
            state = getattr(status, "state", None)
            if isinstance(state, str):
                completed = (state.lower() == "completed")

        # Fallback: raw dump if not found
        if content_text is None:
            content_text = response.model_dump_json()

        # We don't know completed/input_required at the A2A envelope level.
        # Let the client loop decide based on further turns; return flags as None.
        return {
            "content": content_text,
            "task_id": new_task_id or task_id,
            "context_id": new_context_id or context_id,
            "completed": completed,
        }


