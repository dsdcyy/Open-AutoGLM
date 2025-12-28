from phone_agent.adb.input import detect_and_set_adb_keyboard
from phone_agent.adb.connection import ADBConnection
from agent_manager import agent_manager
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from typing import List
import sys
import os

# Add project root to path so we can import phone_agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


app = FastAPI()

# Global reference to the event loop
main_loop = None


@app.on_event("startup")
async def startup_event():
    global main_loop
    import asyncio
    main_loop = asyncio.get_running_loop()

# Setup templates
templates = Jinja2Templates(directory="web_ui/templates")

# Store active websockets


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

# Hook up agent logging to websockets


def log_to_ws(message: str):
    import asyncio
    global main_loop
    if main_loop and main_loop.is_running():
        # Schedule the broadcast in the main event loop from the worker thread
        asyncio.run_coroutine_threadsafe(manager.broadcast(message), main_loop)


def step_to_ws(event: dict):
    import asyncio
    import json
    global main_loop
    if main_loop and main_loop.is_running():
        # Serialize to JSON and broadcast
        message = json.dumps(event)
        asyncio.run_coroutine_threadsafe(manager.broadcast(message), main_loop)


agent_manager.set_log_callback(log_to_ws)
agent_manager.set_step_callback(step_to_ws)


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/app", response_class=HTMLResponse)
async def get_app(request: Request):
    return templates.TemplateResponse("app.html", {"request": request})


@app.post("/check")
async def check_system():
    """Verify ADB connection and Keyboard"""
    conn = ADBConnection()
    devices = conn.list_devices()

    # Filter only devices with status "device" (not "offline" or "unauthorized")
    online_devices = [d for d in devices if d.status == "device"]
    adb_ok = len(online_devices) > 0

    keyboard_ok = False
    if adb_ok:
        try:
            # Check for ADB Keyboard
            # We assume the first online device is the target
            ime = detect_and_set_adb_keyboard(online_devices[0].device_id)
            keyboard_ok = True
        except Exception as e:
            print(f"Keyboard check check failed: {e}")
            keyboard_ok = False

    return {"adb": adb_ok, "keyboard": keyboard_ok}


class WirelessConnection(BaseModel):
    ip: str
    port: str


@app.post("/connect_wireless")
async def connect_wireless(config: WirelessConnection):
    """Connect to device via wireless ADB"""
    import subprocess

    target = f"{config.ip}:{config.port}"

    try:
        # Execute adb connect command
        result = subprocess.run(
            ["adb", "connect", target],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout + result.stderr

        # Check if connection successful
        if "connected" in output.lower() or "already connected" in output.lower():
            return {
                "success": True,
                "message": f"Successfully connected to {target}"
            }
        else:
            return {
                "success": False,
                "message": f"Failed to connect: {output.strip()}"
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "Connection timeout. Please check IP and port."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


class InitConfig(BaseModel):
    base_url: str
    model: str
    apikey: str


@app.post("/init_agent")
async def init_agent(config: InitConfig):
    agent_manager.initialize_agent(
        base_url=config.base_url,
        model=config.model,
        apikey=config.apikey
    )
    return {"status": "ok"}


class TaskRequest(BaseModel):
    task: str


@app.post("/run_task")
async def run_task(req: TaskRequest):
    if not agent_manager.agent:
        return {"status": "error", "message": "Agent not initialized"}

    # Run in background event loop
    import asyncio
    asyncio.create_task(agent_manager.run_task(req.task))
    return {"status": "started"}


@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Just keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="AutoGLM Web UI")
    parser.add_argument("--port", type=int, default=8001,
                        help="Port to run the server on")
    args = parser.parse_args()

    # Check for ENV overrides if CLI arg is default
    port = args.port
    if port == 8001 and os.environ.get("PORT"):
        port = int(os.environ.get("PORT"))

    # Make sure to run from project root
    uvicorn.run(app, host="0.0.0.0", port=port)
