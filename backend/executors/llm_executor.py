from __future__ import annotations

import os
from typing import List

from groq import AsyncGroq

from models.pipeline import PipelineEdge, PipelineNode
from workflow.execution_context import ExecutionContext
from executors.base import NodeExecutor

_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client


class LLMNodeExecutor(NodeExecutor):
    async def execute(
        self,
        node: PipelineNode,
        ctx: ExecutionContext,
        edges: List[PipelineEdge],
    ) -> None:
        groq_model = node.data.get("model", "llama-3.1-8b-instant")

        inputs = ctx.resolve_inputs(node.id, ["system", "prompt"], edges)
        system = str(inputs.get("system") or node.data.get("systemPrompt", "")).strip()
        prompt = str(inputs.get("prompt", "")).strip()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt or "(no prompt provided)"})

        stream = await _get_client().chat.completions.create(
            model=groq_model,
            messages=messages,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        response = ""
        async for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            if token:
                response += token
                await ctx.send_event({
                    "event": "llm_token",
                    "nodeId": node.id,
                    "token": token,
                })

        ctx.set_handle_value(f"{node.id}-response", response)
