import asyncio
import datetime
import uuid

import openai
from typing import List, Dict
from fastapi import WebSocket
from utils.utils import *
# from config import check_openai_api_key
from agent.research_agent import ResearchAgent


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.sender_tasks: Dict[WebSocket, asyncio.Task] = {}
        self.message_queues: Dict[WebSocket, asyncio.Queue] = {}

    async def start_sender(self, websocket: WebSocket):
        queue = self.message_queues[websocket]
        while True:
            message = await queue.get()
            if websocket in self.active_connections:
                await websocket.send_text(message)
            else:
                break

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.message_queues[websocket] = asyncio.Queue()
        self.sender_tasks[websocket] = asyncio.create_task(self.start_sender(websocket))

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.sender_tasks[websocket].cancel()
        del self.sender_tasks[websocket]
        del self.message_queues[websocket]

    async def start_streaming(self, task, report_type, agent, websocket, api_key):
        report, path = await run_agent(task, report_type, agent, websocket, api_key)
        return report, path


async def run_agent(task, report_type, agent, websocket, api_key):
    openai.api_key = api_key

    start_time = datetime.now()
    print(f"Start time: {start_time}")
    document_id = query2db(task, agent, report_type, start_time)
    assistant = ResearchAgent(task, agent, websocket)
    result, error = await assistant.conduct_research()
    if result == "Error":
        await websocket.send_json({"type": "logs", "output": error})
        end_time = datetime.now()
        total_time = end_time - start_time
        update_query(document_id=document_id, status="failed", end_time=end_time, total_time=total_time,error=error)

        return None, None
    report, encoded_path, path = await assistant.write_report(report_type, websocket)
    await websocket.send_json({"type": "path", "output": encoded_path})

    end_time = datetime.now()
    total_time = end_time - start_time
    await websocket.send_json({"type": "logs", "output": f"\nEnd time: {end_time}\n"})
    await websocket.send_json({"type": "logs", "output": f"\nTotal run time: {total_time}\n"})

    file_name = str(uuid.uuid4()) + '.pdf'

    url = upload_to_s3(path, "tavily-reports", file_name)
    update_query(document_id=document_id, path=url, status="finished", end_time=end_time, total_time=total_time,)

    return report, path

