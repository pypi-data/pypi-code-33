import asyncio
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import logging
import traceback
import json

import nats.aio.client
from nats.aio.errors import ErrTimeout

logging.basicConfig(
    format=u'%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO
)

nats.aio.client.DEFAULT_SUB_PENDING_MSGS_LIMIT = 1000000
nats.aio.client.DEFAULT_SUB_PENDING_BYTES_LIMIT = 1024 * 1024 * 64


class WorkerThreadHandler:
    registered = None

    config = {
        "nats": ["nats://127.0.0.1:4222"],
        "max_workers": 2,
        "subjects_to_subscribe": [],
        'unique_name': 'default'
    }

    def __init__(self, **kwargs):
        assert 'worker_function' in kwargs
        self.config.update(kwargs)
        self.nc = nats.aio.client.Client()
        self.tasks_queue = Queue(maxsize=0)
        self.pool = ThreadPoolExecutor(max_workers=self.config['max_workers'])
        self.loop = asyncio.get_event_loop()

    async def _run(self):
        async def disconnected_cb():
            logging.info("Got disconnected!")

        async def reconnected_cb():
            logging.info(f"Got reconnected to {str(self.nc.connected_url.netloc)}")

        async def error_cb(e):
            logging.error(f"There was an error: {traceback.format_exc()}")

        async def closed_cb():
            logging.info("Connection is closed")

        async def connect(options):
            while not self.nc.is_connected:
                try:
                    await self.nc.connect(**options)
                    logging.info(
                        f"Connected to NATS {self.nc.connected_url.netloc} with name {self.config['unique_name']}"
                    )

                    for subj in self.config['subjects_to_subscribe']:
                        await self.nc.subscribe(
                            subj,
                            subj,
                            cb=message_handler_queuer,
                            pending_msgs_limit=1000000,
                        )
                        logging.info(f"Subscribe to channel '{subj}'")
                except nats.aio.client.ErrNoServers:
                    logging.error("Could not connect to any server in cluster.")

        async def send_result(task_data, result, channel='_reporter'):
            data = {
                'task_data': task_data,
                'result': result,
                'module_name': self.config.get("name", None),
                'module_hostname': self.config.get("hostname", None)
            }
            await self.nc.publish(channel, json.dumps(data).encode())

        async def send_error(task_data):
            await send_result(task_data, "ERROR", channel='_error')

        async def message_handler_queuer(msg):
            try:
                task_data = json.loads(msg.data.decode())
                logging.info("Received: %s", task_data)
            except Exception as e:
                logging.error("Receive strange message, from another islands! (Not decode to json)")
                return

            self.tasks_queue.put(task_data)

        def worker_handler(task_data):
            try:
                result = self.config['worker_function'](task_data)
            except Exception:
                logging.error("Exception in worker_function")
                logging.error(traceback.format_exc())
                result = None
            return result

        async def registration():
            try:
                register_data = json.dumps(
                    {"hostname": self.config.get("hostname", None), "name": self.config.get("name", None)})

                register_response = await self.nc.request("_registration", register_data.encode(), 3)
                register_response = json.loads(register_response.data.decode())
                self.config.update(register_response)
                self.registered = True
                logging.info(f"Module registered! Module unique_name is: {self.config['unique_name']}")

                logging.info("Module will be reconnected to change name!")
                await self.nc.close()
            except ErrTimeout:
                logging.warning("Module registration is not possible! The registrar is not responding.")

        options = {
            "servers": self.config['nats'],
            "name": self.config['unique_name'],
            "io_loop": self.loop,
            "max_reconnect_attempts": 8960,
            "reconnect_time_wait": 3,
            "disconnected_cb": disconnected_cb,
            "reconnected_cb": reconnected_cb,
            "error_cb": error_cb,
            "closed_cb": closed_cb,
        }

        while True:
            if not self.nc.is_connected:
                try:
                    await self.nc.close()
                except Exception:
                    pass

                await connect(options)
            if not self.registered:
                await registration()
            while not self.tasks_queue.empty():
                try:
                    task_data = self.tasks_queue.get()
                    result = await self.loop.run_in_executor(self.pool, worker_handler, task_data)
                    if result is None:
                        await send_error(task_data)
                    else:
                        await send_result(task_data, result)
                except Exception as e:
                    logging.error("Error in main logic")
                    logging.error(traceback.format_exc())

            await asyncio.sleep(1, loop=self.loop)

    def run(self):
        self.loop.run_until_complete(self._run())
        self.loop.close()
