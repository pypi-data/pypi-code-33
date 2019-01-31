from pyRoControl.control import Control
import asyncio
import time


host = '192.168.0.214'
port = 55555

sdk = Control((host, port))
time.sleep(0.0001)

s = sdk.robot.speak('Hello World')
s = sdk.motion.move_head(0, 25, 1)


async def delay_release(delay, future):
    await asyncio.sleep(delay)
    print("delay for release")
    return future()


loop = asyncio.get_event_loop()
e = loop.run_until_complete(delay_release(3, sdk.release))
print(e)
