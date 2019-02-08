def mergedict(f_arg,**kwargs):
    dictionary = dict(f_arg)
    for x, y in kwargs.items():
        dictionary[x] = y
    return dictionary