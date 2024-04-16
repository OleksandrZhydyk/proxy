import os
import uvicorn

from fastapi import FastAPI, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from starlette.requests import Request

from req_types.get_req import get_req
from req_types.post_csrf import proxy_post_csrf
from req_types.simple_ws import proxy_simple_ws
from req_types.login import proxy_login

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
async def get(request: Request, request_url: str) -> Response:
    return await get_req(request, request_url, default_cookies)


@app.post("/http/{request_url:path}")
async def post(request: Request, request_url: str) -> Response:
    return await proxy_post_csrf(request, request_url)


@app.websocket("/ws/{request_url:path}")
async def websocket_proxy(websocket: WebSocket, request_url: str):
    await proxy_simple_ws(websocket, request_url)


@app.post("/login/{request_url:path}")
async def post(request: Request, request_url: str) -> Response:
    return await proxy_login(request, request_url)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
