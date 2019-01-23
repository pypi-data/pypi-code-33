from aiohttp import web, WSMsgType
from aiohttp import web_exceptions as aio_exc
import os

WS_TOKEN = os.environ.get('WS_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVC9')
METRICS_TOKEN = os.environ.get('METRICS_TOKEN', '8FTrU92m9HE47lmkBGt3I0CJGtGDE')
MEMBER_TOPIC = os.environ.get('MEMBER_TOPIC', 'members')

routes = web.RouteTableDef()
sockets = list()
cache = dict()

@routes.get('/')
async def index(request):
    text = INDEX
    text = text.replace('{{ topic }}', MEMBER_TOPIC)
    text = text.replace('{{ host }}', request.headers.get('Host'))
    return web.Response(text=text, content_type='text/html')

@routes.get('/status')
async def status(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    sockets.append(ws)

    for wsclient in sockets:
        await wsclient.send_json(cache)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                pass
        elif msg.type == WSMsgType.error:
            await ws.close()

    sockets.remove(ws)
    return ws

@routes.get('/push')
async def push(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    auth_msg = await ws.receive()
    if not auth_msg.type == WSMsgType.TEXT:
        raise aio_exc.HTTPForbidden
    if not auth_msg.data == f'Authorization: Token {WS_TOKEN}':
        raise aio_exc.HTTPForbidden

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                key, value = msg.data.split(': ', 1)
                cache[key] = value
                for wsclient in sockets:
                    await wsclient.send_json(cache)
        elif msg.type == WSMsgType.error:
            print(ws.exception())

    return ws

@routes.get('/metrics')
async def metrics(request):
    if not request.headers.get('Authorization', '') == f'Token {WS_TOKEN}':
        raise aio_exc.HTTPForbidden
    _metrics = 'spacewidget_conections: %s' % len(sockets)
    return web.Response(text=_metrics)


with open('spacewidget/index.html') as f:
    INDEX = f.read()
app = web.Application()
app.add_routes(routes)
web.run_app(app)
