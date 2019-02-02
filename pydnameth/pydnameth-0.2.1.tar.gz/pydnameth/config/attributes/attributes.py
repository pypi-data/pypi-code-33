class Cells:
    def __init__(self,
                 name,
                 types,
                 ):
        self.name = name
        self.types = types

    def __str__(self):
        name = 'cells('
        if isinstance(self.types, list):
            self.types.sort()
            name += '_'.join(self.types)
        elif isinstance(self.types, str):
            name += self.types
        else:
            raise ValueError('Cells.types must be list or str')
        name += ')'
        return name


class Observables:
    def __init__(self,
                 name,
                 types,
                 ):
        self.name = name
        self.types = types

    def __str__(self):
        name = 'observables('
        if isinstance(self.types, dict):
            name += '_'.join([key + '(' + value + ')'
                              for key, value in self.types.items()])
        elif isinstance(self.types, str):
            name += self.types
        else:
            raise ValueError('Observables.types must be dict or str')
        name += ')'
        return name


class Attributes:
    def __init__(self,
                 target,
                 observables,
                 cells,
                 ):
        self.target = target
        self.observables = observables
        self.cells = cells

    def __str__(self):
        name = str(self.target) + '_' + str(self.observables) + '_' + str(self.cells)
        return name


__all__ = ['Cells', 'Observables', 'Attributes']
