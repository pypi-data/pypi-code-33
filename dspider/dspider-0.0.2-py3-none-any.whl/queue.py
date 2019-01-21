# Standard Library
import asyncio


__all__ = ("Queue", "RedisQueue")
Queue = asyncio.Queue


class RedisQueue:
    pass
