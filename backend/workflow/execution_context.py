from typing import Any, Callable, Coroutine, Dict, List, Optional

from models.pipeline import PipelineEdge


class ExecutionContext:
    def __init__(self, send_event: Optional[Callable] = None) -> None:
        self.values: Dict[str, Any] = {}
        self.output_results: Dict[str, Any] = {}
        self._send_event = send_event

    async def send_event(self, event: dict) -> None:
        if self._send_event:
            await self._send_event(event)

    def get_handle_value(self, handle_id: str) -> Any:
        return self.values.get(handle_id)

    def set_handle_value(self, handle_id: str, value: Any) -> None:
        self.values[handle_id] = value

    def resolve_inputs(
        self,
        node_id: str,
        input_suffixes: List[str],
        edges: List[PipelineEdge],
    ) -> Dict[str, Any]:
        resolved: Dict[str, Any] = {}
        incoming = [edge for edge in edges if edge.target == node_id]

        for suffix in input_suffixes:
            target_handle = f"{node_id}-{suffix}"
            for edge in incoming:
                if edge.targetHandle == target_handle:
                    resolved[suffix] = self.get_handle_value(edge.sourceHandle)
                    break

        return resolved

    def set_output_result(self, node_id: str, result: Any) -> None:
        self.output_results[node_id] = result

    def get_output_result(self, node_id: str) -> Optional[Any]:
        return self.output_results.get(node_id)
