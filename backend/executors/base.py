from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from models.pipeline import PipelineEdge, PipelineNode
from workflow.execution_context import ExecutionContext


class NodeExecutor(ABC):
    @abstractmethod
    async def execute(
        self,
        node: PipelineNode,
        ctx: ExecutionContext,
        edges: List[PipelineEdge],
    ) -> None:
        pass


class NodeExecutorRegistry:
    def __init__(self) -> None:
        self._executors: Dict[str, NodeExecutor] = {}

    def register(self, node_type: str, executor: NodeExecutor) -> None:
        self._executors[node_type] = executor

    def get(self, node_type: str) -> Optional[NodeExecutor]:
        return self._executors.get(node_type)
