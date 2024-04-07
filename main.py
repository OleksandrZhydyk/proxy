import httpx
import os
import uvicorn
import websockets

from fastapi import FastAPI, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from starlette.requests import Request
from urllib.parse import urlparse


app = FastAPI(title="proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_default_cookie() -> Dict[str, str]:
    cookies = {}
    for k, v in os.environ.items():
        if k.startswith(custom_cookie_prefix):
            cookies[k.split(custom_cookie_prefix)[1]] = v
    return cookies


custom_cookie_prefix = "c_"
default_cookies = get_default_cookie()


@app.get("/http/{request_url:path}")
async def get(request: Request, request_url: str):
    cookies = get_cookies(request)
    cookies.update(default_cookies)
    headers = get_request_headers(request)

    async with httpx.AsyncClient() as client:
        resp = await client.get(request_url, cookies=cookies, headers=headers)

    content_type = resp.headers.get("content-type")
    content = resp.content
    response = Response(content, media_type=content_type, headers=resp.headers, status_code=resp.status_code)
    return set_cookie_to_response(resp, response)


@app.post("/http/{request_url:path}")
async def post(request: Request, request_url: str, data: Dict[str, str]):
    cookies = get_cookies(request)
    cookies.update(default_cookies)
    headers = get_request_headers(request)

    async with httpx.AsyncClient() as client:
        resp = await client.post(request_url, cookies=cookies, headers=headers, json=data)

    content_type = resp.headers.get("content-type")
    content = resp.content
    response = Response(content, media_type=content_type, headers=resp.headers, status_code=resp.status_code)
    return set_cookie_to_response(resp, response)


@app.websocket("/ws/{request_url:path}")
async def websocket_proxy(websocket: WebSocket, request_url: str):
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


def get_cookies(request: Request) -> Dict[str, str]:
    return request.cookies


def set_cookie_to_response(source_response: httpx.Response, proxy_response: Response) -> Response:
    for cookie in source_response.cookies.items():
        proxy_response.set_cookie(
            key=cookie[0],
            value=cookie[1]
        )
    return proxy_response


def get_request_headers(request: Request) -> Dict[str, str]:
    headers = {header: request.headers[header] for header in request.headers}
    headers.pop('host', None)
    headers.pop('origin', None)
    headers.pop('cookie', None)
    return headers


def get_origin_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    origin = parsed_url.scheme + "://" + parsed_url.netloc
    return origin


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("proxy_port", 8001), reload=False)
