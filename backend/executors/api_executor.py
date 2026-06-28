from __future__ import annotations

import json
import re
from typing import List

import httpx

from models.pipeline import PipelineEdge, PipelineNode
from workflow.execution_context import ExecutionContext
from executors.base import NodeExecutor

VARIABLE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


class APINodeExecutor(NodeExecutor):
    async def execute(
        self,
        node: PipelineNode,
        ctx: ExecutionContext,
        edges: List[PipelineEdge],
    ) -> None:
        method = node.data.get("method", "GET").upper()
        url = node.data.get("url", "").strip()

        # Resolve {{variable}} placeholders in the URL
        url_variables = [m.group(1) for m in VARIABLE_PATTERN.finditer(url)]
        input_keys = url_variables + (["body"] if method in ("POST", "PUT", "PATCH") else [])
        inputs = ctx.resolve_inputs(node.id, input_keys, edges)

        def replace_var(match: re.Match) -> str:
            return str(inputs.get(match.group(1), ""))

        url = VARIABLE_PATTERN.sub(replace_var, url)

        if not url:
            ctx.set_handle_value(f"{node.id}-response", "")
            ctx.set_handle_value(f"{node.id}-status", "400")
            return

        async with httpx.AsyncClient(timeout=15) as client:
            kwargs = {}
            body = inputs.get("body")
            if body:
                kwargs["content"] = body if isinstance(body, str) else json.dumps(body)
                kwargs["headers"] = {"Content-Type": "application/json"}

            response = await client.request(method, url, **kwargs)

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text

        ctx.set_handle_value(f"{node.id}-response", response_text)
        ctx.set_handle_value(f"{node.id}-status", str(response.status_code))
