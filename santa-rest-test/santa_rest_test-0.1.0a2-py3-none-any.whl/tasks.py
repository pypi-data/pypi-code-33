import os
import glob

import pyaml
from asyncio import sleep

from santa.task import Task
from santa.loader import load_suite
from santa.context_processor import context_processor_factory

from santa.parser import StringField, ListField, BooleanField, IntField


class Context(Task):
    """
    Update the context
    """
    processors = ListField(item_type=context_processor_factory, is_main=True)

    async def __run__(self, ctx):
        for proc in self.processors:
            await proc(ctx)


class Message(Task):
    """
    Print debug info or context values
    """

    message = StringField(default="", is_main=True)
    context = ListField(default=[], is_main=True)
    debug = BooleanField(default=False)

    async def __run__(self, ctx):
        self._result.log("")
        self._result.log(ctx.render(self.message))
        for var in self.context:
            self._result.log(var + ":", 1)
            ctx_var = ctx
            for part in var.split("."):
                ctx_var = ctx.render(ctx_var[part])
            for line in pyaml.dump(ctx_var).splitlines():
                self._result.log(line, 2)
        self._result.log("")


class Include(Task):
    """
    Include a suite into another
    """
    suite = StringField(is_main=True)

    async def __run__(self, ctx):
        s = await load_suite(self.suite)
        res = await s(ctx)
        self._result["suite"] = res.as_dict()


class Sleep(Task):
    """
    Do nothing for a while. Used to throttle tests on slow test servers
    """
    time = IntField(is_main=True)

    async def __run__(self, ctx):
        await sleep(self.time/1000)


class Require(Task):
    """
    Run a suite only if it wasn't run yet
    """
    suite = StringField(default="", is_main=True)
    reset = StringField(default="")

    async def __run__(self, ctx):
        if self.suite:
            suite = await load_suite(self.suite)
            suitefile = suite.__file__
        else:
            suite = None
            suitefile = ""
        if self.reset:
            reset = ctx.render(self.reset)
            reset = glob.glob(os.path.join("suite", reset) + ".y*ml")
            done = ctx.render(ctx["_suite_done"])
            for s in reset:
                if s == suitefile:
                    continue
                while s in done:
                    done.remove(s)
            ctx["_suite_done"] = done
        if suite is None:
            return
        if suite.__file__ in ctx["_suite_done"]:
            self._result.skipped = "%s already completed" % suite.__file__
            return
        res = await suite(ctx)
        ctx["_suite_done"].append(suite.__file__)
        self._result["suite"] = res.as_dict()


class Fork(Task):
    """
    Run a suite concurrently. A copy of the current context is passed to the new suite
    """
    suite = StringField(is_main=True)

    async def __run__(self, ctx):
        s = await load_suite(self.suite)
        ctx = ctx.copy()
        return s(ctx)
