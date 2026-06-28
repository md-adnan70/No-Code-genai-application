from collections import deque
from typing import Dict, List

from models.pipeline import PipelineEdge, PipelineNode


class DAGValidationError(Exception):
    pass


class PipelineGraph:
    def __init__(self, nodes: List[PipelineNode], edges: List[PipelineEdge]):
        self.nodes = nodes
        self.edges = edges
        self.node_ids = [node.id for node in nodes]
        self._adjacency: Dict[str, List[str]] = {node.id: [] for node in nodes}
        self._in_degree: Dict[str, int] = {node.id: 0 for node in nodes}

        for edge in edges:
            if edge.source in self._adjacency and edge.target in self._in_degree:
                self._adjacency[edge.source].append(edge.target)
                self._in_degree[edge.target] += 1

    def validate_dag(self) -> None:
        if not self.is_dag():
            raise DAGValidationError("Pipeline contains a cycle and is not a DAG")

    def is_dag(self) -> bool:
        state = {node_id: 0 for node_id in self.node_ids}

        def has_cycle(node_id: str) -> bool:
            if state[node_id] == 1:
                return True
            if state[node_id] == 2:
                return False
            state[node_id] = 1
            for neighbor in self._adjacency.get(node_id, []):
                if has_cycle(neighbor):
                    return True
            state[node_id] = 2
            return False

        for node_id in self.node_ids:
            if state[node_id] == 0 and has_cycle(node_id):
                return False
        return True

    def topological_sort(self) -> List[str]:
        self.validate_dag()

        in_degree = dict(self._in_degree)
        queue = deque([node_id for node_id in self.node_ids if in_degree[node_id] == 0])
        order: List[str] = []

        while queue:
            node_id = queue.popleft()
            order.append(node_id)
            for neighbor in self._adjacency.get(node_id, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.node_ids):
            raise DAGValidationError("Pipeline contains a cycle and is not a DAG")

        return order

    def get_incoming_edges(self, node_id: str) -> List[PipelineEdge]:
        return [edge for edge in self.edges if edge.target == node_id]
