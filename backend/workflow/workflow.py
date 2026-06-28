from typing import Callable, Dict, List, Optional

from models.pipeline import (
    ExecutePipelineRequest,
    ExecutePipelineResponse,
    OutputResult,
    PipelineNode,
)
from workflow.execution_context import ExecutionContext
from executors import create_executor_registry
from workflow.graph import DAGValidationError, PipelineGraph


class Workflow:
    def __init__(self, request: ExecutePipelineRequest, send_event: Optional[Callable] = None):
        self.request = request
        self.nodes_by_id: Dict[str, PipelineNode] = {
            node.id: node for node in request.nodes
        }
        self.graph = PipelineGraph(request.nodes, request.edges)
        self.context = ExecutionContext(send_event=send_event)
        self.registry = create_executor_registry()
        self.execution_order: List[str] = []

    def validate(self) -> None:
        if not self.request.nodes:
            raise ValueError("Pipeline must contain at least one node")
        self.graph.validate_dag()

    async def run(self) -> ExecutePipelineResponse:
        self.validate()
        self.execution_order = self.graph.topological_sort()

        for node_id in self.execution_order:
            node = self.nodes_by_id[node_id]
            if node.type == "note":
                continue

            executor = self.registry.get(node.type)
            if executor is None:
                continue

            await self.context.send_event({"event": "node_start", "nodeId": node_id})
            await executor.execute(node, self.context, self.request.edges)

            prefix = f"{node_id}-"
            handle_outputs = {
                handle_id.removeprefix(prefix): value
                for handle_id, value in self.context.values.items()
                if handle_id.startswith(prefix)
            }
            await self.context.send_event({
                "event": "node_complete",
                "nodeId": node_id,
                "outputs": handle_outputs,
            })

        return self._build_response()

    def _build_response(self) -> ExecutePipelineResponse:
        node_outputs: Dict[str, Dict[str, object]] = {}
        outputs: List[OutputResult] = []

        for node_id in self.execution_order:
            node = self.nodes_by_id[node_id]
            prefix = f"{node_id}-"
            handle_outputs = {
                handle_id.removeprefix(prefix): value
                for handle_id, value in self.context.values.items()
                if handle_id.startswith(prefix)
            }
            if handle_outputs:
                node_outputs[node_id] = handle_outputs

            if node.type == "customOutput":
                result = self.context.get_output_result(node_id)
                if result:
                    outputs.append(
                        OutputResult(
                            node_id=node_id,
                            name=result["name"],
                            type=result["type"],
                            value=result["value"],
                        )
                    )

        return ExecutePipelineResponse(
            success=True,
            execution_order=self.execution_order,
            node_outputs=node_outputs,
            outputs=outputs,
        )
