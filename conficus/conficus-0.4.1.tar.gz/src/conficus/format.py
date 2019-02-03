def _variable_name(parent, name):
    if not parent:
        return name
    return parent + '.' + name


def _format_value(name, value):
    if any([pw in name for pw in ('password', 'passwd', 'pwd')]):
        return '**********'
    return str(value)


def _format_sequence(sequence):
    start, end = '[]' if isinstance(sequence, list) else '()'
    _list = [str(v) for v in sequence]

    _short_list = ', '.join(_list)

    if len(_short_list) + 2 < 80:
        return start + _short_list + end

    _long_list = ['    ' + str(v) for v in _list]

    return start + '\n' + '\n'.join(_long_list) + end


def formatter(cdict, output=None, parent=''):
    if not output:
        output = []
    for key, value in cdict.items():
        full_name = _variable_name(parent, key)
        # print('{}: {}'.format(key, value))
        # print('TYPE: {}'.format(type(value)))
        if not isinstance(value, (dict, list, tuple)):
            _value = _format_value(key, value)
            _output = '[config] {}: {}'.format(full_name, _value)
            output.append(_output)
        elif isinstance(value, (list, tuple)):
            _output = '[config] {}: {}'.format(full_name, _format_sequence(value))
            output.append(_output)
        else:
            formatter(value, output=output, parent=full_name)

    return '\n'.join(output)
