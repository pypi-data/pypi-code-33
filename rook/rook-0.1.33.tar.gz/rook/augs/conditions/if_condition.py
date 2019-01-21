from rook.processor.paths.arithmetic_path import ArithmeticPath


class IfCondition(object):
    NAME = 'if'

    def __init__(self, configuration, factory):
        path_config = {
            'name': 'calc',
            'path': configuration['path']
        }

        self.path = ArithmeticPath(path_config, factory)

    def evaluate(self, namespace, extracted):
        obj = self.path.read_from(namespace).obj

        return isinstance(obj, bool) and obj
