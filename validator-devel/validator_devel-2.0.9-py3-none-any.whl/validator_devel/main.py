import os
import asyncio
import logging

from aiohttp import web

from . import templating
from .routes import setup_routes
from .filesystem import start_load, ModuleEventHandler, start_observer

from dynaconf import settings

async def listen_to_filesystem(app):
    """Start the observer on the filesystem."""
    path = settings.get('modules_path')
    start_load(path)
    logging.debug(f"start filesystem watch on {path}")
    try:
        observer = start_observer(path)
    except asyncio.CancelledError:
        observer.stop()
        observer.join()

async def start_background_tasks(app):
    """Start all tasks that are outside of aiohttp handler."""
    app['filesystem_watch'] = app.loop.create_task(listen_to_filesystem(app))
    templating.init()

async def cleanup_background_tasks(app):
    app['filesystem_watch'].cancel()
    await app['filesystem_watch']
    templating.shutdown()


def check():
    """Perform static check before starting the application."""
    paths = [settings.get('modules_path'), settings.get('validator_path')]
    for p in paths:
        if not os.path.exists(p):
            raise ValueError(f"The path: {p} doesn't exists.")

def main():
    check()
    app = web.Application()
    app.on_startup.append(start_background_tasks)
    app.on_shutdown.append(cleanup_background_tasks)

    setup_routes(app)
    web.run_app(app)

if __name__ == '__main__':
    main()
