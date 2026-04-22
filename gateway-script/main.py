import os
import docker
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv, set_key

app = FastAPI(title="AI Agent Gateway & Spawner")

DATA_DIR = os.getenv("DATA_DIR", "./data")
ENV_FILE = os.path.join(DATA_DIR, "env", ".env")

# Ensure env dir exists
os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)
if not os.path.exists(ENV_FILE):
    with open(ENV_FILE, "w") as f:
        f.write("# API Keys Configuration\n")

load_dotenv(ENV_FILE)

client = docker.from_env()

class SpawnerRequest(BaseModel):
    agent_type: str  # "hermes" or "openclaw"
    instruction: str # The task or job description for this agent
    parent_agent: str = "CEO"

class APIKeyUpdate(BaseModel):
    openai_key: str = ""
    anthropic_key: str = ""
    gemini_key: str = ""

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.post("/api/keys")
async def update_keys(keys: APIKeyUpdate):
    if keys.openai_key:
        set_key(ENV_FILE, "OPENAI_API_KEY", keys.openai_key)
    if keys.anthropic_key:
        set_key(ENV_FILE, "ANTHROPIC_API_KEY", keys.anthropic_key)
    if keys.gemini_key:
        set_key(ENV_FILE, "GEMINI_API_KEY", keys.gemini_key)
    
    # Reload environment
    load_dotenv(ENV_FILE)
    return {"status": "success", "message": "Keys updated."}

@app.post("/api/spawn")
async def spawn_agent(req: SpawnerRequest):
    """
    Spawns a new Docker container for the requested agent type.
    """
    agent_id = f"worker_{req.agent_type}_{os.urandom(4).hex()}"
    agent_dir = os.path.join(DATA_DIR, "agents", agent_id)
    os.makedirs(agent_dir, exist_ok=True)

    env_vars = {
        "AGENT_INSTRUCTION": req.instruction,
        "PARENT_AGENT": req.parent_agent,
        "AGENT_WING_ID": agent_id,  # Memory wing for MemPalace
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", "")
    }

    try:
        if req.agent_type.lower() == "hermes":
            container = client.containers.run(
                image="nousresearch/hermes-agent:latest",
                name=agent_id,
                environment=env_vars,
                volumes={
                    os.path.abspath(agent_dir): {'bind': '/opt/data', 'mode': 'rw'}
                },
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
        else: # OpenClaw fallback
            container = client.containers.run(
                image="node:20",
                name=agent_id,
                command='sh -c "npm install -g openclaw && openclaw start --daemon"',
                environment=env_vars,
                volumes={
                    os.path.abspath(agent_dir): {'bind': '/root/.openclaw', 'mode': 'rw'}
                },
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
        return {"status": "success", "agent_id": agent_id, "container_id": container.short_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "reason": str(e)})

@app.post("/webhook/paperclip")
async def paperclip_webhook(request: Request):
    """
    Receives tasks from Paperclip HTTP Adapter and routes them to the CEO or appropriate worker.
    """
    payload = await request.json()
    task_id = payload.get("task", {}).get("id", "unknown")
    task_desc = payload.get("task", {}).get("description", "No description")
    
    # Normally we would POST this to the Hermes CEO Gateway port:
    # requests.post("http://ceo_hermes:8642/v1/chat/completions", json={...})
    
    print(f"[Paperclip Webhook] Received task {task_id}: {task_desc}")
    
    # To conform with async response pattern in Paperclip
    return JSONResponse(status_code=202, content={"status": "accepted", "message": "Task queued for CEO."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
