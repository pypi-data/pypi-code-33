from aiohttp import web
import uuid
import time
import asyncio
from functools import partial

@web.middleware
async def send_requests_to_oms(request, handler):
    if 'swagger' in request.path:
        response = await handler(request)
    else:
        api = handler
        try:
            while type(api) == partial:
                api = api.keywords['handler']
        except:
            api = handler
        start_time = time.time()
        asyncio.ensure_future(request.app['oms'].create_event(
                    log_type="serverLog",
                    name="REQUEST",
                    request=request))

        response = await handler(request)

        exec_time = time.time() - start_time
        asyncio.ensure_future(request.app['oms'].create_event(
                    log_type="serverLog",
                    name="RESPONSE",
                    request=request,
                    event_data={
                        'execution': exec_time,
                        'status_code': response.status,
                        'api': getattr(api, '__name__', '_ModuleError'),
                        'controller': getattr(api, '__module__', '_ModuleError')
                    }))
    return response
