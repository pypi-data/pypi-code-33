import logging
from datetime import datetime
import inspect
import asyncio
from aiohttp.web_request import Request, BaseRequest
import linecache
from traceback import walk_tb

class OMSHandler(logging.Handler):
    """OMS Logging Handler
    """

    def __init__(self, oms_client=None, app_dir='/app/', *args, **kwargs):
        self.oms_client = oms_client
        self.app_dir = app_dir
        super().__init__(*args, **kwargs)

    def emit(self, record=None):
        self.format(record)
        request = None
        frames = inspect.stack()
        for frame in [frames[i].frame for i in range(len(frames)-1, 0, -1)]:
            if ('request' in frame.f_locals.keys() 
                and type(frame.f_locals.get('request')) == Request 
                and type(frame.f_locals.get('request')) != BaseRequest
                ):
                request = frame.f_locals.get('request')
                break

        if record.exc_info:
            # exception
            offending_frame_stack = [(f,l) for f,l in walk_tb(record.exc_info[2])]
            last_app_frame, last_app_line_no = offending_frame_stack[-1]
            for frame, line_no in [offending_frame_stack[i] for i in range(len(offending_frame_stack)-1, 0, -1)]:
                if self.app_dir in frame.f_code.co_filename:
                    last_app_frame, last_app_line_no = frame, line_no
                    break
            module = inspect.getmodule(last_app_frame)
            if module:
                module = module.__name__
            record_data = {
                'function': last_app_frame.f_code.co_name,
                'lineno': last_app_line_no,
                'line': linecache.getline(last_app_frame.f_code.co_filename, last_app_line_no).strip(),
                'module': module,
                'file': last_app_frame.f_code.co_filename,
                'message': record.getMessage(),
                'traceback': record.exc_text
            }
        else:
            # regular log
            record_data = {
                'function': record.funcName,
                'line': record.lineno,
                'module': record.module,
                'message': record.getMessage(),
                'file': record.pathname,
            }
        try:
            asyncio.ensure_future(self.oms_client.create_event(
                    log_type="serverLog",
                    name=record.levelname,
                    request=request,
                    event_data=record_data,
                    event_time=datetime.strptime(record.asctime, '%Y-%m-%d %H:%M:%S,%f')))
        except Exception as e:
            print("OMSHandler exc: {0}".format(str(e)))
 