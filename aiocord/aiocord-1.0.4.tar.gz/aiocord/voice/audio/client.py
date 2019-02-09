import asyncio


__all__ = ('Options', 'Client')


class Options:

    frame_length = 20
    sample_rate = 48000
    channels = 2
    sample_size = 2 * channels
    samples_per_frame = sample_rate // 1000 * frame_length
    frame_size = samples_per_frame * sample_size


class Client:

    __all__ = ('_send', '_controls', '_process', '_loop')

    def __init__(self, send, loop = None):

        if not loop:

            loop = asyncio.get_event_loop()

        self._send = send

        self._controls = []

        self._process = None

        self._loop = loop

    @property
    def active(self):

        return (
            self._process
            and (
                self._process.returncode is None
                or not self._process.returncode < 0
            )
        )

    def track(self, control):

        self._controls.append(control)

    async def create(self):

        watcher = asyncio.get_child_watcher()

        watcher.attach_loop(self._loop)

        args = (
            'ffmpeg',
            '-i', '-',
            '-f', 's16le',
            '-ar', Options.sample_rate,
            '-ac', Options.channels,
            '-loglevel', 'fatal',
            'pipe:1',
        )

        self._process = await asyncio.create_subprocess_exec(
            *map(str, args),
            stdin = asyncio.subprocess.PIPE,
            stdout = asyncio.subprocess.PIPE,
            loop = self._loop
        )

    def extend(self, data):

        self._process.stdin.write(data)

    async def start(self, size = Options.frame_size):

        start = loops = None

        def reset():

            nonlocal start, loops

            start = self._loop.time()

            loops = 0

        wait = Options.frame_length / 1000

        reset()

        while self.active:

            data = await self._process.stdout.read(size)

            if len(data) < size and loops:

                break

            for control in self._controls:

                data = await control(data)

            self._send(data)

            while True:

                elapsed = start - self._loop.time()

                fallback = elapsed + wait * loops

                catchup = wait + fallback

                if not loops or catchup > 0:

                    break

                reset()

            delay = max(0, catchup)

            await asyncio.sleep(delay, loop = self._loop)

            loops += 1

    async def destroy(self):

        try:

            self._process.kill()

        except ProcessLookupError:

            return

        await self._process.wait()

    def __repr__(self):

        status = ('active' if self.active else 'inactive')

        return f'<{self.__class__.__name__} [{status}]>'
