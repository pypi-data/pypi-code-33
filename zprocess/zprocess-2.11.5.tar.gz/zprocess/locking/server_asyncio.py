import threading
import asyncio
import zmq
import zmq.asyncio

MAX_RESPONSE_TIME = 1  # second
MAX_ABSENT_TIME = 1  # second

INVALID_NUMBERS = {float('nan'), float('inf'), float('-inf')}

# Requires PYZMQ 17

# async def acquire(foo):
#     # try to acquire the lock now:
#     if lock.acquire():
#         return
#     # Otherwise wait up to MAX_RESPONSE_TIME for it to be acquired.
#     # Create a Future, put it in a registry, wait on the Future. Other guys can set it done.
#     lock_acquired = asyncio.Future()
#     self.acquisition_futures[key, client_id] = lock_acquired
#     result = await asyncio.wait(lock_acquired timout=MAX_RESPONSE_TIME)

DEBUG = True
if DEBUG:
    import logging
    logging.getLogger('asyncio').setLevel(logging.DEBUG)


class ZMQLockServer(object):
    def __init__(self, port=None, bind_address='tcp://0.0.0.0'):
        self.port = port
        self._initial_port = port
        self.bind_address = bind_address
        self.context = None
        self.router = None
        self.active_locks = {}

        self.run_thread = None
        self.stopping = False
        self.started = threading.Event()
        self.event_loop = None
        self.pending_requests = {}

    def get_lock(self, key):
        """Return the lock object with the given key if it already exists, else make
        a new instance"""
        if key in self.active_locks:
            return self.active_locks[key]
        else:
            lock = Lock(key, self.active_locks)
            self.active_locks[key] = lock
            return lock

    async def server_loop(self):
        # print('starting')
        while True:
            # Wait until we receive a request:
            request = await self.router.recv_multipart()
            print('received:', request)
            if len(request) < 3 or request[1] != b'':
                # Not well formed as [routing_id, '', command, ...]
                continue
            routing_id, command, args = request[0], request[2], request[3:]
            if command == b'hello':
                await self.send(routing_id, b'hello')
            elif command == b'acquire':
                await self.acquire_request(routing_id, args)
            elif command == b'release':
                await self.release_request(routing_id, args)
            elif command == b'stop' and self.stopping:
                await self.send(routing_id, b'ok')
                return
            else:
                self.send(routing_id, b'error: invalid command')

    def run(self):
        """Start the event loop and begin serving requests. Blocks until stop() is
        called"""
        self.event_loop = asyncio.new_event_loop()
        self.event_loop.set_debug(DEBUG)
        asyncio.set_event_loop(self.event_loop)
        self.context = zmq.asyncio.Context.instance()
        self.router = self.context.socket(zmq.ROUTER)
        if self.port is not None:
            self.router.bind('%s:%d' % (self.bind_address, self.port))
        else:
            self.port = self.router.bind_to_random_port(self.bind_address)
        self.started.set()
        try:
            self.event_loop.run_until_complete(self.server_loop())
        finally:
            self.router.close()
            self.router = None
            self.context = None
            self.port = self._initial_port
            self.started.clear()
            self.event_loop.close()
            self.event_loop = None

    def run_in_thread(self):
        """Run the event loop in a separate thread, returning immediately"""
        self.run_thread = threading.Thread(target=self.run)
        self.run_thread.daemon = True
        self.run_thread.start()
        self.started.wait()

    def stop(self):
        """Stop the event loop"""
        self.stopping = True
        context = zmq.Context.instance()
        sock = context.socket(zmq.REQ)
        sock.connect('tcp://127.0.0.1:%d' % self.port)
        sock.send(b'stop')
        assert sock.recv() == b'ok'
        sock.close()
        if self.run_thread is not None:
            self.run_thread.join()
        self.stopping = False

    async def send(self, routing_id, message):
        """Send a message to a client with the given routing_id"""
        print('sending:', [routing_id, b'', message])
        await self.router.send_multipart([routing_id, b'', message])

    async def acquire_request(self, routing_id, args):
        """Validate an acquire request, reply to client about errors. If the request is
        valid, queue up self.acquire() to run in the event loop"""
        if not 3 <= len(args) <= 4:
            await self.send(routing_id, b'error: wrong number of arguments')
            return
        key, client_id, timeout = args[:3]
        try:
            timeout = float(timeout)
        except ValueError:
            await self.send(routing_id, b'error: timeout %s not a valid number' % timeout)
            return
        if timeout in INVALID_NUMBERS:
            await self.send(
                routing_id,
                b'error: timeout %s not a valid number' % str(timeout).encode(),
            )
            return
        if len(args) == 4:
            if args[3] != b'read_only':
                await self.send(routing_id, b"error: expected 'read_only', got %s" % args[3])
                return
            read_only = True
        else:
            read_only = False
        if (key, client_id) in self.pending_requests:
            msg = b'error: multiple concurrent requests with same key and client_id'
            await self.send(routing_id, msg)
            return
        # if Python 3.7:
        # asyncio.create_task(
        #     self.acquire(routing_id, key, client_id, timeout, read_only)
        # )
        asyncio.ensure_future(
            self.acquire(routing_id, key, client_id, timeout, read_only)
        )

    async def release_request(self, routing_id, args):
        if not len(args) == 2:
            await self.send(routing_id, b'error: wrong number of arguments')
            return
        key, client_id = args
        # Python 3.7: asyncio.create_task( self.release(routing_id, key, client_id))
        asyncio.ensure_future(self.release(routing_id, key, client_id))

    async def acquire(self, routing_id, key, client_id, timeout, read_only):
        await self.send(routing_id, b'ok')

    async def release(self, routing_id, key, client_id):
        await self.send(routing_id, b'ok')


if __name__ == '__main__':
    port = 7339
    server = ZMQLockServer(port)
    server.run()


# sock = ctx.socket(zmq.ROUTER)
# sock.bind('tcp://127.0.0.1:7339')

# async def server_loop():
#     while True:
#         # wait for a message
#         msg = await sock.recv_multipart()
#         print(msg)

# if acquire:
# if coroutine already exists, send data to it by settings the Future done or
# settings its result or something. Otherwise make a new coroutine to run_soon I
# think.
# if release:
#     run the release function. It might send data to the acquire coroutines.

# make a task based on this message
# handle = event_loop.call_soon(acquire, msg)
# tell the event loop to run the task - can we run it right now until it awaits?


# loop = asyncio.get_event_loop()
# # Schedule a call to hello_world()
# try:
#     loop.run_until_complete(server_loop())
# except KeyboardInterrupt:
#     sock.close()
