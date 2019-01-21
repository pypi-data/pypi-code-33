import yaml
import aiohttp
from asyncio import iscoroutine, ensure_future, wait, sleep

from santa.task import Task, task_factory
from santa.parser import ListField


class Suite(Task):
    tasks = ListField(default=list, item_type=task_factory, is_main=True)

    def __init__(self, data):
        super().__init__(tasks=data)
        self._result["tasks"] = []
        self.__file__ = self.__class__.__name__
        self.futures = {}

    def get_items(self, items, ctx):
        if isinstance(items, list):
            return items
        if isinstance(items, str):
            rendered = yaml.load(ctx.render(items))
            if isinstance(rendered, dict):
                rendered = [i for i in rendered.items()]
            if not isinstance(rendered, list):
                raise ValueError("Can't resolve `%s` as a list" % items)
            return rendered

    async def run_task(self, task, ctx):
        if hasattr(task, "name"):
            name = ctx.render(task.name)
        else:
            name = task.__yaml_name__
        name = "%s: %s" % (self.__file__, name)
        # self._result.log(name)
        result = await task(ctx)
        if iscoroutine(result):
            self.futures[ensure_future(result)] = name
        else:
            result.taskname = name
            return self._parse_result(result)
        self._result.log("")
        return True

    async def __run__(self, ctx):
        self._result.taskname = self.__file__
        for task in self.tasks:
            await sleep(0.05)
            if not task.with_items:
                if not await self.run_task(task, ctx):
                    break
            else:
                for item in self.get_items(task.with_items, ctx):
                    ctx["item"] = item
                    if not await self.run_task(task, ctx):
                        break
                else:
                    continue
                break
        if self.futures:
            done, _ = await wait(list(self.futures.keys()))
            if done:
                for d in done:
                    res = d.result()
                    res.taskname = self.futures[d]
                    self._parse_result(res)
        return self._result

    def _parse_result(self, result):
        self._result["tasks"].append(result.as_dict())
        if not result.success:
            msg = "%s: FAIL" % result.taskname
            self._result.log_error(msg)
            self._result.log(msg)
            for error in result.errors:
                self._result.log(error)
        elif result.skipped:
            msg = "%s: SKIPPED" % result.taskname
            self._result.log(msg)
            self._result.log(result.skipped, 2)
        else:
            msg = "%s: OK" % result.taskname
            self._result.log(msg)
        return result.success
