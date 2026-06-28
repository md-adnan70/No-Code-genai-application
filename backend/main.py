from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from models.pipeline import ExecutePipelineRequest
from workflow.graph import DAGValidationError, PipelineGraph
from workflow.workflow import Workflow

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Ping": "Pong"}


@app.post("/pipelines/parse")
def parse_pipeline(pipeline: ExecutePipelineRequest):
    graph = PipelineGraph(pipeline.nodes, pipeline.edges)
    return {
        "num_nodes": len(pipeline.nodes),
        "num_edges": len(pipeline.edges),
        "is_dag": graph.is_dag(),
    }


@app.websocket("/pipelines/run")
async def run_pipeline_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        pipeline = ExecutePipelineRequest(**data)

        async def send_event(event: dict) -> None:
            await websocket.send_json(event)

        workflow = Workflow(pipeline, send_event=send_event)
        result = await workflow.run()

        await websocket.send_json({
            "event": "pipeline_complete",
            **result.model_dump(),
        })
    except DAGValidationError as exc:
        await websocket.send_json({"event": "error", "message": str(exc)})
    except ValueError as exc:
        await websocket.send_json({"event": "error", "message": str(exc)})
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"event": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
