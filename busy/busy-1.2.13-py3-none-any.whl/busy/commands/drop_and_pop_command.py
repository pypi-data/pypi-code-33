from ..commander import QueueCommand
from ..commander import Commander


class DropCommand(QueueCommand):

    command = 'drop'


Commander.register(DropCommand)


class PopCommand(QueueCommand):

    command = 'pop'


Commander.register(PopCommand)
