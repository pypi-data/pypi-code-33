from ..commander import QueueCommand
from ..commander import Commander


class ListCommand(QueueCommand):

    command = 'list'

    def execute_on_queue(self, parsed, queue):
        itemlist = queue.list(*parsed.criteria)
        return self._list(queue, itemlist)


Commander.register(ListCommand)
