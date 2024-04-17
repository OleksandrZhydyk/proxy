import httpx, re

from typing import Dict
from fastapi import Response, Request
from utils import get_request_headers, set_cookie_to_response, get_origin_from_url, get_form_xcsrf


async def get_req(request: Request, request_url: str) -> Response:
    cookies = dict(request.query_params)
    headers = get_request_headers(request, get_origin_from_url(request_url))
    xcsrf, resp_cookies = await get_form_xcsrf(request_url, cookies, headers)
    if xcsrf:
        headers['X-Csrftoken'] = xcsrf

    async with httpx.AsyncClient() as client:
        resp = await client.get(request_url, cookies=cookies, headers=headers)
    content_type = resp.headers.get("content-type")
    content = resp.content
    response = Response(content, media_type=content_type, headers=resp.headers, status_code=resp.status_code)
    return set_cookie_to_response(resp, response)

