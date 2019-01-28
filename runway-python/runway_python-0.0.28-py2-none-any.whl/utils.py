def to_long_spec(spec):
    long_spec = []
    for key, value in spec.items():
        if type(value) == str:
            value = {'name': key, 'type': value}
        elif type(value) == list:
            value = {'name': key, 'type': {'arrayOf': to_long_spec(value[0])}}
        elif type(value) == dict:
            value = {'name': key, 'type': to_long_spec(value)}
        long_spec.append(value)
    return long_spec
