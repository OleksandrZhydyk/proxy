## Simple FastAPI proxy server

FastAPI proxy server that support HTTP (GET, POST) requests and WS.

### Quickstart

Build the proxy image
``` shell
docker build -t proxy .
```

Run proxy server 
```shell
docker run -it -d -p 8001:8001 proxy
```

 - Run proxy server with needed auth cookies. 
> Add required `c_` prefix to cookie name

```shell
docker run -it -d -e c_sessionid="by4lxxxxxxxxxxxxx76z6" \
-e c_csrftoken="40ByxxxxxxxxxxxxPUjh" -p 8001:8001 proxy
```

- Run proxy server with needed proxy port
```shell
docker run -it -d -e proxy_port 8080 -p 8080:8080 proxy
```