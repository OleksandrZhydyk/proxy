import json
from typing import Dict

import httpx
import re

from fastapi import Request, Response

from utils import get_request_headers, get_origin_from_url, set_cookie_to_response


async def proxy_login(request: Request, request_url: str,) -> Response:
    cookies = request.cookies
    headers = get_request_headers(request, get_origin_from_url(request_url))
    resp_cookies, xcsrf = await get_form_xcsrf(request_url, cookies, headers)
    cookies.update(resp_cookies)
    if xcsrf:
        headers['X-Csrftoken'] = xcsrf

    body = await request.body()
    async with httpx.AsyncClient() as client:
        resp = await client.post(request_url, cookies=cookies, headers=headers, data=body)
    content_type = resp.headers.get("content-type")
    auth_cookies = dict(resp.cookies.items())
    content = resp.json()
    content["cookies"] = auth_cookies
    resp.headers.pop('content-length')
    response = Response(json.dumps(content), media_type=content_type, headers=resp.headers, status_code=resp.status_code)
    return set_cookie_to_response(resp, response)


async def get_form_xcsrf(request_url: str, cookies: Dict[str, str], headers: Dict[str, str]) -> str | None:
    headers.pop('content-length')
    async with httpx.AsyncClient() as client:
        resp = await client.get(get_origin_from_url(request_url), cookies=cookies, headers=headers)
    pattern = r'name=\'csrfmiddlewaretoken\'\svalue=\'([^\']+)\''
    match = re.search(pattern, resp.text)
    return resp.cookies, match.group(1) if match else None
