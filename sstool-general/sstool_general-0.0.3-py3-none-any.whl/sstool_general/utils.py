import aio_pika
import aiohttp
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient


def check_params_for_board_update(*args, arg_type=str):
    """
        Check if arguments exist and equal to arg_type

        :param args: arguments to check
        :param arg_type: type to check
        :return: True or False
        :rtype: bool
    """
    return all(args) and all(isinstance(x, arg_type) for x in args)


async def create_rabbitmq_connection(loop, user, password, host):
    """
        Create and return a connection to the rabbitmq.
    """
    rabbitmq = await aio_pika.connect_robust(
        "amqp://{0}:{1}@{2}/".format(
            user,
            password,
            host
        ),
        loop=loop
    )
    return rabbitmq


async def close_rabbitmq_connection(rabbitmq):
    """
        Close a connection to the rabbitmq.
    """
    await rabbitmq.close()


async def create_redis_connection(loop, host):
    """
        Create and return a connection to the redis.
    """
    redis = await aioredis.create_redis(
        'redis://{}'.format(host),
        loop=loop
    )
    return redis


async def close_redis_connection(redis):
    """
        Close a connection to the redis and delete all keys.
    """
    keys = await redis.keys("*")
    for key in keys:
        await redis.delete(key)
    redis.close()
    await redis.wait_closed()


async def create_mongodb_connection(loop, host, port, db_name):
    """
        Create and return a connection to the mongo db.
    """
    client = AsyncIOMotorClient(
        host,
        port,
        io_loop=loop
    )
    db = client[db_name]
    return db


async def create_aiohttp_session(loop):
    """
        Create and return an aiohttp_session.
    """
    session = aiohttp.ClientSession(loop=loop)
    return session


async def close_aiohttp_session(session):
    """
        Closean aiohttp_session.
    """
    await session.close()
