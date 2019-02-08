from .utils import find_request
import time, datetime
import asyncio
import inspect
from functools import wraps

def log_execution(func, oms, event_name="EXEC"):
    def wrap(*args, **kwargs):
        event_time = datetime.datetime.utcnow()
        exc_start = time.time()
        result = func(*args, **kwargs)
        exec_time = time.time() - exc_start
        req = find_request()
        asyncio.ensure_future(oms.create_event(
            log_type="serverLog",
            name=event_name,
            request=req,
            event_time=event_time,
            event_data={
                'execution': exec_time,
                'api': getattr(func, '__name__', '_ModuleError'),
                'controller': getattr(func, '__module__', '_ModuleError')
            }))
        return result
    async def async_wrap(*args, **kwargs):
        event_time = datetime.datetime.utcnow()
        exc_start = time.time()
        result = await func(*args, **kwargs)
        exec_time = time.time() - exc_start
        req = find_request()
        asyncio.ensure_future(oms.create_event(
            log_type="serverLog",
            name=event_name,
            request=req,
            event_time=event_time,
            event_data={
                'execution': exec_time,
                'api': getattr(func, '__name__', '_ModuleError'),
                'controller': getattr(func, '__module__', '_ModuleError')
            }))
        return result
    return wraps(func)(async_wrap) if inspect.iscoroutinefunction(func) else wraps(func)(wrap)
