def split(separator):
    def split_inner(aString):
        return aString.split(separator)

    return split_inner
