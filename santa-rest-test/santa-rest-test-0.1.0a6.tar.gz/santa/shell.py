import os
from subprocess import run
import cmd
from tempfile import mkstemp
import asyncio
from pprint import pformat
import yaml

from jq import jq
import pyaml

from santa.parser import yamlloader_as_yaml
from santa.validator import ValidationError
from santa.task import task_factory
from santa.context import ContextBase, MappingContext


class TaskShell(cmd.Cmd):
    def __init__(self, task, context, *args, **kwargs):
        self.task = task
        self.ctx = context
        self.set_task(task)
        self.orig_task = task
        super().__init__(*args, **kwargs)

    async def cmdloop(self, intro=None):  # pragma: no cover
        """
        Near-vebatim copy of cmd.Cmd.cmdloop() (modulo 1 await) to allow
        calls in commands.
        """

        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = await self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    async def onecmd(self, line):  # pragma: no cover
        """
        Near verbatim copy of cmd.Cmd.onecmd
        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF' :
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)
            if asyncio.iscoroutinefunction(func):
                return await func(arg)
            return func(arg)

    def print(self, msg):
        self.stdout.write(msg)
        self.stdout.write("\n")

    def pprint(self, msg):
        self.stdout.write(pformat(msg))
        self.stdout.write("\n")

    def print_yaml(self, msg):
        yaml.dump(msg, stream=self.stdout)

    @property
    def prompt(self):
        return self.task.name + " > "

    def do_context(self, arg):
        """
        Print current context.

        If the arg ends with "." only the keys of the object are shown

        >>> mytest > context urls.
        www
        backoffice

        >>> mytest > context urls
        www:
            host: example.com
        backoffice:
            host: admin.example.com

        Alias: ctx
        """
        if arg.strip() == "." or not arg:
            for k in self.ctx.data.keys():
                self.print(k)
            return
        if arg.endswith("."):
            var = arg[:-1]
            ctx_var = self.ctx
            for part in var.split("."):
                ctx_var = ctx_var[part]
            if isinstance(ctx_var, (MappingContext, dict)):
                for k in ctx_var.keys():
                    self.print(k)
            else:
                self.print(var + " is not a map.")
            return
        else:
            self.print(arg + ":")
            ctx_var = self.ctx
            for part in arg.split("."):
                ctx_var = ctx_var[part]
            if isinstance(ctx_var, (ContextBase)):
                ctx_var = ctx_var._render()
            for line in pyaml.dump(ctx_var).splitlines():
                self.print("  " + line)
            return

    do_ctx = do_context

    def do_exit(self, arg):
        "Exit the shell and abort the test"
        self.abort = True
        return True

    async def do_run(self, args):
        "Run the current task"
        self.task.interactive = False
        self.task._result.set_context(self.ctx)
        self.task._result.start()
        await self.task.__run__(self.ctx)
        self.task.interactive = True
        self.orig_task._result = self.task._result

    def do_reset(self, args):
        "Reset the task to its original state"
        self.orig_task.__init__()
        self.set_task(self.orig_task)

    def do_edit(self, arg):
        "Open $EDITOR to edit the current task"
        (fd, name) = mkstemp(suffix=".yml", text=True)
        file = os.fdopen(fd, "w")
        yamlloader_as_yaml(self.task, output=file,
                           name=self.task.__yaml_name__)
        file.close()
        run([os.environ.get("EDITOR", "nano"), name])
        with open(name, "r") as f:
            data = yaml.load(f)
        self.set_task(task_factory(data))

    def set_task(self, task):
        task.name = self.task.name
        if hasattr(self.task, "__ctx__"):
            task.__ctx__ = self.task.__ctx__
        self.task = task


class TestShell(TaskShell):
    def set_task(self, task):
        super().set_task(task)
        self.url, self.qs, self.headers, self.json_body = self.task.get_parts(
                self.ctx)
        self.json = None
        self.abort = False

    async def do_run(self, args):
        "Run the current task"
        try:
            await super().do_run(args)
        except ValidationError:
            pass
        self.print_yaml(self.task._result.as_dict())
        self.json = self.task._result["response.json"]

    def do_url(self, arg):
        "Print URL"
        self.print(self.url)

    def do_qs(self, arg):
        "Print query_string"
        self.pprint(self.qs)

    def do_headers(self, arg):
        "Print headers"
        self.pprint(self.headers)

    def do_json_body(self, arg):
        "Print "
        self.pprint(self.json_body)

    def do_jq(self, pattern):
        """
        Run a jq script against the result JSON.
        """
        if self.json is None:
            self.print("No response yet. Call 'run' first.")
            return
        try:
            self.pprint(jq(pattern).transform(self.json))
        except Exception as e:
            self.print(str(e))
