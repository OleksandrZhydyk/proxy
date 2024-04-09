from typing import Dict

import httpx
import re

from fastapi import Request, Response

from utils import get_request_headers, get_origin_from_url, set_cookie_to_response


async def proxy_post_csrf(request: Request, request_url: str, default_cookies: Dict[str, str]) -> Response:
    cookies = request.cookies
    cookies.update(default_cookies)
    headers = get_request_headers(request, get_origin_from_url(request_url))
    xcsrf = await get_form_xcsrf(request_url, cookies, headers)
    headers['X-Csrftoken'] = xcsrf

    body = await request.body()

    async with httpx.AsyncClient() as client:
        resp = await client.post(request_url, cookies=cookies, headers=headers, data=body)
    content_type = resp.headers.get("content-type")
    content = resp.content
    response = Response(content, media_type=content_type, headers=resp.headers, status_code=resp.status_code)
    return set_cookie_to_response(resp, response)


async def get_form_xcsrf(request_url, cookies, headers) -> str:
    headers.pop('content-length')
    async with httpx.AsyncClient() as client:
        resp = await client.get(get_origin_from_url(request_url), cookies=cookies, headers=headers)
    pattern = r'name=\'csrfmiddlewaretoken\'\svalue=\'([^\']+)\''
    return re.search(pattern, resp.text).group(1)
