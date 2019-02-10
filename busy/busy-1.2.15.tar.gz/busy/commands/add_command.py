from ..commander import QueueCommand
from ..commander import Commander


class AddCommand(QueueCommand):

    command = 'add'

    @classmethod
    def register(self, parser):
        super().register(parser)
        parser.add_argument('item', nargs='?')

    def execute_on_queue(self, parsed, queue):
        if hasattr(parsed, 'item') and parsed.item:
            item = parsed.item
        else:
            item = input('Item: ')
        queue.add(item)


Commander.register(AddCommand)
