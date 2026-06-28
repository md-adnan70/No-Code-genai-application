from executors.api_executor import APINodeExecutor
from executors.base import NodeExecutorRegistry
from executors.input_executor import InputNodeExecutor
from executors.llm_executor import LLMNodeExecutor
from executors.output_executor import OutputNodeExecutor
from executors.text_executor import TextNodeExecutor


def create_executor_registry() -> NodeExecutorRegistry:
    registry = NodeExecutorRegistry()
    registry.register("customInput", InputNodeExecutor())
    registry.register("text", TextNodeExecutor())
    registry.register("llm", LLMNodeExecutor())
    registry.register("customOutput", OutputNodeExecutor())
    registry.register("api", APINodeExecutor())
    return registry
