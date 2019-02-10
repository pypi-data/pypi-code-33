
import asyncio.events
import asyncio.coroutines


def run_sync(coro):
    if hasattr(asyncio, 'run'):
        return asyncio.run(coro)

    else:
        loop = asyncio.new_event_loop()
        try:
            asyncio.events.set_event_loop(loop)
            return loop.run_until_complete(coro)

        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())

            finally:
                asyncio.events.set_event_loop(None)
                loop.close()
