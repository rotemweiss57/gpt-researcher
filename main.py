import time

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import os

from agent.run import WebSocketManager


class ResearchRequest(BaseModel):
    task: str
    report_type: str
    agent: str



app = FastAPI()
print("Starting server...")
app.mount("/site", StaticFiles(directory="client"), name="site")
app.mount("/static", StaticFiles(directory="client/static"), name="static")
# Dynamic directory for outputs once first research is run
@app.on_event("startup")
def startup_event():
    if not os.path.isdir("outputs"):
        os.makedirs("outputs")
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

templates = Jinja2Templates(directory="client")

manager = WebSocketManager()


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request, "report": None})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Client connected")  # New log
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("start"):
                json_data = json.loads(data[6:])
                task = json_data.get("task")
                report_type = json_data.get("report_type")
                agent = json_data.get("agent")
                api_key = json_data.get("api_key")
                await websocket.send_json({"type": "logs",
                                           "output": "Due to the high volume of requests, we are unable to process your request at this time. Please try again later."})
                time.sleep(1)
                await websocket.send_json({"type": "email",
                                           "output": "Please enter your email address and we will update you when you can access the site"})
                data = await websocket.receive_text()
                json_data = json.loads(data)
                email = json_data.get("email")
                if task and report_type and agent:
                    await manager.start_streaming(task, report_type, agent, websocket, api_key, email)
                else:
                    print("Error: not enough parameters provided.")

    except WebSocketDisconnect:
        print("Client disconnected")  # New log
        await manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
