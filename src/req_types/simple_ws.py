import websockets

from fastapi import WebSocket
from utils import get_origin_from_url


async def proxy_simple_ws(websocket: WebSocket, request_url: str):
    # Connect to the target WebSocket server
    async with websockets.connect(
            request_url,
            user_agent_header=websocket.headers["user-agent"],
            origin=websockets.Origin(get_origin_from_url(request_url)),
    ) as target_ws:
        await websocket.accept()

        # Forward messages from client to target server
        async for message in websocket.iter_text():
            await target_ws.send(message)

        # Forward messages from target server to client
        async for message in target_ws:
            await websocket.send_text(message)
