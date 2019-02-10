def map_dictionary_keys(d, map_function):
    new = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = map_dictionary_keys(v, map_function)
        if isinstance(v, list):
            new_list = []
            for item in v:
                if isinstance(item, dict):
                    new_list.append(map_dictionary_keys(item, map_function))
                else:
                    new_list.append(item)
            v = new_list
        new[map_function(k)] = v
    return new
