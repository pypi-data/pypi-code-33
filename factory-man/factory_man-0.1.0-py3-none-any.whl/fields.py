import factory


class ModelFieldSequence(factory.Sequence):
    def __init__(self, model=None, string: str = None):
        assert not(
            model and string), 'You cannot specify both `model` and `string`, but only oen of them'
        assert not model and string or model and not string, 'You must specify either `model` or `string`'
        self.string = string
        self.model = model

    def __set_name__(self, owner, field_name: str):
        try:
            super().__init__(
                self.fn(f'{self.model._meta.object_name}__{field_name}'), int)
        except:
            super().__init__(self.fn(self.string), int)

    @staticmethod
    def fn(string):
        def inner_fn(n):
            return f'{string}-{n}'
        return inner_fn
