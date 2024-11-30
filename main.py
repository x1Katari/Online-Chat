import names
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
from uuid import uuid4

app = FastAPI()

clients = {}

message_history: List[str] = []

@app.get("/")
async def get():
    with open("chat.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    username = names.get_full_name(gender='male')
    user_id = str(uuid4())
    clients[websocket] = {'username': username, 'user_id': user_id}

    if len(clients) >= 5:
        await websocket.send_text("💡 Chat is full. Try again later.")
        await websocket.close()
        for client in clients.keys():
            await client.close()
            clients.pop(client)
        return None

    for message in message_history:
        await websocket.send_text(message)

    join_message = f"💡 {username} joined the chat."
    message_history.append(join_message)
    for client in clients.keys():
        await client.send_text(join_message)

    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"
            message_history.append(message)

            for client in clients.keys():
                await client.send_text(message)

    except WebSocketDisconnect:
        clients.pop(websocket)
        disconnect_message = f"💡 {username} left the chat."
        message_history.append(disconnect_message)
        for client in clients.keys():
            await client.send_text(disconnect_message)
