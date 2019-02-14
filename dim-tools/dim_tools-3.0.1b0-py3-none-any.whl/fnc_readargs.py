# -*- coding:utf-8 -*-
def to_type(tt, data):
    if tt in ['str', 'string']:
        return str(data)
    elif tt in ['int', 'integer']:
        return int(data)
    elif tt in ['list']:
        try:
            return [int(item) for item in data.split(',')]
        except ValueError:
            return data.split(',')
    elif tt in ['dict']:
        return {item.split(':')[0]: item.split(':')[1] for item in data.split(',')}


def main(args, arg_structure):
    res = [arg_structure[i]["default"] for i in range(0, len(arg_structure))]
    keywords = {key: old_key for old_key in arg_structure for key in arg_structure[old_key]['names']}
    options = [word.split('=')[0] for word in args]
    i = 1
    while i < len(options):
        if options[i] in keywords:
            num = keywords[options[i]]
            if arg_structure[num]['paired']:
                arg = args.pop(i)
                res[num] = arg.split('=')[1]
                res[num] = to_type(arg_structure[num]['type'], res[num])
            else:
                args.pop(i)  # removing keyword from the list
                res[num] = True
            options.pop(i)
        else:
            i += 1
    if len(res) == 1:
        return res[0]
    return res
