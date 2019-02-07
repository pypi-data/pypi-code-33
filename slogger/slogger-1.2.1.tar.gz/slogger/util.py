
def buildLogContent(title, obj):
    return obj if title == None else "{}--{}".format(title, obj)
