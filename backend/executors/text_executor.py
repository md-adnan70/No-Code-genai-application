from __future__ import annotations

import re
from typing import List

from models.pipeline import PipelineEdge, PipelineNode
from workflow.execution_context import ExecutionContext
from executors.base import NodeExecutor

VARIABLE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


class TextNodeExecutor(NodeExecutor):
    async def execute(
        self,
        node: PipelineNode,
        ctx: ExecutionContext,
        edges: List[PipelineEdge],
    ) -> None:
        text = node.data.get("text", "")

        # Collect all variable names referenced in the text
        variables = self._extract_variables(text)

        # Resolve by variable name from connected handles
        inputs = ctx.resolve_inputs(node.id, variables, edges)

        # Also resolve any incoming edges whose source handle suffix matches a variable
        # (covers api node response, output node, or any other node type)
        incoming = [e for e in edges if e.target == node.id]
        for edge in incoming:
            # derive the variable name from the target handle: "{nodeId}-{varName}"
            prefix = f"{node.id}-"
            if edge.targetHandle.startswith(prefix):
                var_name = edge.targetHandle[len(prefix):]
                if var_name not in inputs:
                    inputs[var_name] = ctx.get_handle_value(edge.sourceHandle)

        def replace_var(match: re.Match) -> str:
            var_name = match.group(1)
            value = inputs.get(var_name)
            return str(value) if value is not None else ""

        result = VARIABLE_PATTERN.sub(replace_var, text)
        ctx.set_handle_value(f"{node.id}-output", result)

    def _extract_variables(self, text: str) -> List[str]:
        found: List[str] = []
        for match in VARIABLE_PATTERN.finditer(text):
            var_name = match.group(1)
            if var_name not in found:
                found.append(var_name)
        return found
