# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Pretty print utilities. These cover use-cases
not supported by the `pprint` module. E.g.,
pretty print dictionaries with keys in the order
they have been added (`pprint` sorts the keys
alphabetically before producing the output).
"""

def print_dict(dictionary, indent0=4, tab=2, to_file=False):
    """
    :param dict dictionary: The dictionary to print.
    :param int indent0: The number of spaces
        to indent the higher-level keys with.
    :param int tab: The space increment to
        add as the method goes one level
        deeper.
    :param bool to_file: If ``True`` prepare printout
        for saving in file.
    :rtype: str or None
    """
    bullets = ['-', '*', '+']
    def rprint(value, depth=0):
        bindex = depth % len(bullets)
        space = (indent0 + (depth+1)*tab) * ' '
        try:
            children = []
            for k, v in value.items():
                to_append = f'{space} {bullets[bindex]} {k}:'
                to_append += rprint(v, depth+1)
                children.append(to_append)
            _fstring = f'\n' + f'\n'.join(children)
        except AttributeError:
            _fstring = f' {value}'
        return _fstring

    lines = []
    for key, value in dictionary.items():
        lines.append(f'  -> {key}: {rprint(value)}')
    printout = '\n'.join(lines)
    if to_file:
        return printout
    else:
        print(printout)
