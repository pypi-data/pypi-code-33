def mergedict(**kwargs):
    dictionary = { '' : '' }
    for x, y in kwargs.items():
        dictionary[x] = y
    return dictionary