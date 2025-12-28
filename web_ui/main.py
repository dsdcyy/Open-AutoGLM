import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Add project root to path so we can import phone_agent
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from agent_manager import agent_manager
from phone_agent.adb.connection import ADBConnection
from phone_agent.adb.input import detect_and_set_adb_keyboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    global main_loop
    main_loop = asyncio.get_running_loop()
    yield


app = FastAPI(lifespan=lifespan)


# Setup templates
templates = Jinja2Templates(directory="web_ui/templates")

# Serve static files
app.mount("/static", StaticFiles(directory="web_ui/static"), name="static")

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

    # Determine connection type and get device info
    conn_type = "none"
    device_info = None

    if adb_ok:
        first_device = online_devices[0]
        device_info = {"id": first_device.device_id, "model": first_device.model}

        # Check if wireless (contains ":")
        if ":" in first_device.device_id:
            conn_type = "wireless"
            # Parse IP and port from device_id (format: ip:port)
            parts = first_device.device_id.split(":")
            device_info["ip"] = parts[0]
            device_info["port"] = parts[1]
        else:
            conn_type = "usb"

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

    return {
        "adb": adb_ok,
        "keyboard": keyboard_ok,
        "connection_type": conn_type,
        "device": device_info,
    }


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
            ["adb", "connect", target], capture_output=True, text=True, timeout=10
        )

        output = result.stdout + result.stderr

        # Check if connection successful
        if "connected" in output.lower() or "already connected" in output.lower():
            return {"success": True, "message": f"Successfully connected to {target}"}
        else:
            return {"success": False, "message": f"Failed to connect: {output.strip()}"}
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "Connection timeout. Please check IP and port.",
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


@app.post("/disconnect_wireless")
async def disconnect_wireless():
    """Disconnect wireless ADB device"""
    import subprocess

    try:
        # Execute adb disconnect command (disconnect all)
        result = subprocess.run(
            ["adb", "disconnect"], capture_output=True, text=True, timeout=5
        )

        output = result.stdout + result.stderr

        return {"success": True, "message": "Wireless ADB disconnected"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


class InitConfig(BaseModel):
    base_url: Optional[str] = "https://api.openai.com/v1"
    model: Optional[str] = "gpt-4-vision-preview"
    apikey: Optional[str] = ""


@app.post("/init_agent")
async def init_agent(config: InitConfig):
    agent_manager.initialize_agent(
        base_url=config.base_url or "",
        model=config.model or "",
        apikey=config.apikey or "",
    )
    return {"status": "ok"}


class TaskRequest(BaseModel):
    task: str


@app.post("/run_task")
async def run_task(req: TaskRequest):
    if not agent_manager.agent:
        return {"status": "error", "message": "Agent not initialized"}

    # Run the task and wait for it to finish
    await agent_manager.run_task(req.task)
    return {"status": "done"}


@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Just keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/cancel")
async def cancel_task():
    """Cancel the ongoing task"""
    agent_manager.cancel_task()
    return {"success": True}


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="AutoGLM Web UI")
    parser.add_argument(
        "--port", type=int, default=8001, help="Port to run the server on"
    )
    args = parser.parse_args()

    # Check for ENV overrides if CLI arg is default
    port = args.port
    if port == 8001 and os.environ.get("PORT"):
        port = int(os.environ.get("PORT"))

    # Make sure to run from project root
    uvicorn.run(app, host="0.0.0.0", port=port)
