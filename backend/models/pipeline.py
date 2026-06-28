from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PipelineNode(BaseModel):
    id: str
    type: str
    data: Dict[str, Any] = {}


class PipelineEdge(BaseModel):
    source: str
    target: str
    sourceHandle: str
    targetHandle: str


class ExecutePipelineRequest(BaseModel):
    nodes: List[PipelineNode]
    edges: List[PipelineEdge]


class OutputResult(BaseModel):
    node_id: str
    name: str
    type: str
    value: Any


class ExecutePipelineResponse(BaseModel):
    success: bool
    execution_order: List[str]
    node_outputs: Dict[str, Dict[str, Any]]
    outputs: List[OutputResult]
    error: Optional[str] = None
