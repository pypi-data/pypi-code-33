''' A ScheduleProvider Service Provider '''
from masonite.provider import ServiceProvider
from ..commands.ScheduleRunCommand import ScheduleRunCommand
from ..commands.CreateTaskCommand import CreateTaskCommand

class ScheduleProvider(ServiceProvider):

    def register(self):
        self.app.bind('ScheduleCommand', ScheduleRunCommand())
        self.app.bind('CreateTaskCommand', CreateTaskCommand())

    def boot(self):
        pass
