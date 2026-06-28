# No-Code-genai-application

https://github.com/user-attachments/assets/5df538fc-cdc0-4143-a0a0-3363f104361a

🎨 Visually Build GenAI Workflows in Minutes
This platform is a completely visual, drag-and-drop No-Code LLM Application Builder. It completely eliminates the overhead of manually stitching together APIs, data prompt pipelines, and frontend interfaces.

How It Works:
Drag-and-Drop Canvas: Simply pick up specialized node chips from the top toolbar—such as Input, Text Template, API Call, LLM, or Output—and drop them directly onto an expansive canvas.

Intuitive Wiring: Seamlessly connect input and output handles together to define your data logic pipeline visually.

Dynamic Node Variables: Typing variables inside a Text Node (like {{owner}} or {{repo}}) instantly generates a new input handle on the fly, ready to map incoming data.

Instant Single-Click Execution: Hit Run Pipeline at the bottom of the screen to watch your entire custom workflow light up and execute in real time.

You can see a complete end-to-end walkthrough of a multi-node workflow executing live in the repository video: no_code_app_video.mp4.

This project implements a production-grade Event-Driven Backend Engine powered by FastAPI WebSockets, dynamic runtime dependency sorting, and live streaming inference through Groq.

1. Real-Time WebSocket Architecture
When a user triggers a pipeline execution, the frontend opens a stateful WebSocket connection to /pipelines/run.

Topological Sorting: The backend analyzes the pipeline graph dynamically, checks for cycles via DFS, and performs a topological sort to walk the execution nodes in strict dependency order.

Shared Execution Context: An abstract ExecutionContext object acts as the pipeline memory. It resolves inputs dynamically by tracing incoming edges and securely maps handle values across nodes.

Granular Event Streaming: The backend streams explicit execution phases back to the UI:

node_start: Triggers a pulsing amber active-state animation on the executing node.

node_complete: Switches the node status badge to a green checkmark and lights up connecting edges.

llm_token: Streams LLM inference data token-by-token for live updates.

2. Extensible Executor Registry
The codebase enforces a highly modular, decoupled architecture using the Registry Pattern:

Every node type maps directly to a dedicated executor class (e.g., InputNodeExecutor, APINodeExecutor, LLMNodeExecutor).

All executors inherit from a unified NodeExecutor base class exposing a single .execute() method.

Developers can spin up custom functional nodes by registering them under the centralized NodeExecutorRegistry without mutating core workflow logic.

🛠️ Showcase Workflow: GitHub Repo Extractor
The capabilities of this real-time execution engine are demonstrated through a fully integrated pipeline that performs live API orchestration and LLM synthesis:

[Input Node] ➔ [Text Template] ➔ [API Node (GitHub GET)] ➔ [LLM Node (Groq)] ➔ [Output Node]
Input & Templating: An Input Node feeds repository parameters into a dynamically resizing Text Node to construct the absolute endpoint URL ([https://api.github.com/repos/](https://api.github.com/repos/){{owner}}/{{repo}}).

Dynamic API Extraction: The API Node dynamically reads the template variables at runtime, triggers a live REST request to the GitHub API, and caches the raw JSON payload into the ExecutionContext.

Streaming Inference: The JSON payload passes downstream into the LLM Node. The backend establishes a streaming connection to the Groq API, and raw tokens stream back to the UI via the active WebSocket connection to populate an intelligence report live.

📂 Layered Codebase Architecture
The backend code is cleanly split into three decoupled, independent packages to maximize testability and maintainability:

Plaintext
├── models/       # Pydantic data schemas for pipeline graphs, nodes, and edges
├── workflow/     # Core graph-parsing, DAG validation, and cycle detection
└── executors/    # Abstract executor base, registry, and individual node runtime logic
⚡ Quick Start
1. Environment Configuration
Create a .env file in your backend directory and supply your API key:

Code snippet
GROQ_API_KEY=your_groq_api_key_here
2. Spin up the Backend
Bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
3. Spin up the Frontend
'''code
Bash
cd frontend
npm install
npm start
