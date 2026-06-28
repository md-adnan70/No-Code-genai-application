from __future__ import annotations
from typing import List
from models.pipeline import PipelineEdge, PipelineNode
from workflow.execution_context import ExecutionContext
from executors.base import NodeExecutor


class OutputNodeExecutor(NodeExecutor):
    async def execute(
        self,
        node: PipelineNode,
        ctx: ExecutionContext,
        edges: List[PipelineEdge],
    ) -> None:
        inputs = ctx.resolve_inputs(node.id, ["value"], edges)
        value = inputs.get("value", "")
        ctx.set_handle_value(f"{node.id}-value", value)
        ctx.set_output_result(
            node.id,
            {
                "name": node.data.get("outputName", node.id),
                "type": node.data.get("outputType", "Text"),
                "value": value,
            },
        )
