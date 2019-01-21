import sys
import time
from asyncio import iscoroutine
from traceback import format_exception

from santa.parser import YamlLoader, YamlField, StringField, YamlLoaderBase


class TaskBase(YamlLoaderBase):
    type_name = "task"
    registry = {}


class Task(YamlLoader, metaclass=TaskBase):
    __abstract__ = True
    name = StringField(default="")
    with_items = YamlField(default=list)

    def __init__(self, *args, **kwargs):
        YamlLoader.__init__(self, *args, **kwargs)
        self._result = TaskResult(self)

    async def __run__(self, ctx):
        raise NotImplementedError()

    async def __call__(self, ctx):
        self._result.set_context(ctx)
        self._result.start()
        try:
            res = await self.__run__(ctx)
            if iscoroutine(res):
                self._result.stop()
                return res
        except Exception as e:
            self._result.log_exception(e, sys.exc_info()[2])
            self._result.stop()
            raise
        self._result.stop()
        return self._result


task_factory = Task._factory


class TaskResult:
    def __init__(self, task):
        self.result = {}
        self.errors = []
        self.warnings = []
        self.skipped = None
        self.taskname = None
        self.task = task
        self._ctx = None
        self._start = None
        self._stop = None

    @property
    def ctx(self):
        if self._ctx is None:
            raise ValueError("Call set_context(ctx) before using it.")
        return self._ctx

    def set_context(self, ctx):
        self._ctx = ctx

    def log(self, msg, indent=0):
        self.ctx["_out"].write(" " * indent)
        self.ctx["_out"].write(str(msg) + "\n")

    def log_debug(self, msg, indent=0):
        if self.ctx.get("_debug") or self.task.debug:
            self.log(msg, indent)

    def log_error(self, msg):
        self.errors.append(msg)

    def log_warning(self, msg):
        self.warnings.append(msg)

    def log_exception(self, e, tb=None):
        exc = format_exception(e, e, tb)
        for line in exc:
            self.log(line.rstrip())
        self.errors.append(exc)
        return

    def start(self):
        self._start = time.time()

    def stop(self):
        self._stop = time.time()

    def __setitem__(self, key, value):
        path = key.split(".")
        last = path.pop()
        result = self.result
        for k in path:
            result = result.setdefault(k, {})
        result[last] = value

    def __getitem__(self, key):
        path = key.split(".")
        last = path.pop()
        result = self.result
        for k in path:
            result = result[k]
        return result[last]

    @property
    def success(self):
        return not bool(self.errors)

    def as_dict(self):
        if self._start and self._stop:
            duration = self._stop - self._start
        else:
            duration = None
        return dict(
            errors=self.errors,
            warnings=self.warnings,
            skipped=bool(self.skipped),
            result=self.result,
            success=self.success,
            duration=duration,
            task_name=self.taskname,
            type=self.task.__yaml_name__,
        )
