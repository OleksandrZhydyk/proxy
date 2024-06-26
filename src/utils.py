from typing import Dict

import httpx

from fastapi import Response, Request
from urllib.parse import urlparse


def get_origin_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    origin = parsed_url.scheme + "://" + parsed_url.netloc
    return origin


def set_cookie_to_response(source_response: httpx.Response, proxy_response: Response) -> Response:
    for cookie in source_response.cookies.items():
        proxy_response.set_cookie(
            key=cookie[0],
            value=cookie[1]
        )
    return proxy_response


def get_request_headers(request: Request, origin: str) -> Dict[str, str]:
    headers = {header: request.headers[header] for header in request.headers}
    headers.pop('host', None)
    headers.pop('cookie', None)
    headers['origin'] = origin
    headers['referer'] = origin
    return headers
