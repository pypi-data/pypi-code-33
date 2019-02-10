from ..commander import QueueCommand
from ..commander import Commander


class GetCommand(QueueCommand):

    command = 'get'

    def execute_on_queue(self, parsed, queue):
        if parsed.criteria:
            message = ("The `get` command only returns the top item - "
                       "repeat without criteria")
            raise RuntimeError(message)
        else:
            return str(queue.get() or '')


Commander.register(GetCommand)
