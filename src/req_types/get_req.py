import httpx

from typing import Dict
from fastapi import Response, Request
from utils import get_request_headers, set_cookie_to_response


async def get_req(request: Request, request_url: str, default_cookies: Dict[str, str]) -> Response:
    cookies = request.cookies
    headers = get_request_headers(request, request_url)

    async with httpx.AsyncClient() as client:
        resp = await client.get(request_url, cookies=cookies, headers=headers)

    content_type = resp.headers.get("content-type")
    content = resp.content
    response = Response(content, media_type=content_type, headers=resp.headers, status_code=resp.status_code)
    return set_cookie_to_response(resp, response)
