import json
import httpx

from fastapi import Request, Response

from utils import get_request_headers, get_origin_from_url, set_cookie_to_response, get_form_xcsrf


async def proxy_login(request: Request, request_url: str,) -> Response:
    cookies = request.cookies
    headers = get_request_headers(request, get_origin_from_url(request_url))
    xcsrf, resp_cookies = await get_form_xcsrf(request_url, cookies, headers)
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

