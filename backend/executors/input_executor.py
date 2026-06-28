from __future__ import annotations

from typing import List

from models.pipeline import PipelineEdge, PipelineNode
from workflow.execution_context import ExecutionContext
from executors.base import NodeExecutor


class InputNodeExecutor(NodeExecutor):
    async def execute(
        self,
        node: PipelineNode,
        ctx: ExecutionContext,
        edges: List[PipelineEdge],
    ) -> None:
        value = node.data.get("inputValue", "")
        ctx.set_handle_value(f"{node.id}-value", value)
