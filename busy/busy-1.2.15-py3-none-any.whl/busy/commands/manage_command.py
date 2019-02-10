from ..commander import QueueCommand
from ..commander import Commander


class ManageCommand(QueueCommand):

    command = 'manage'


Commander.register(ManageCommand)
