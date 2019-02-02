import json

EXT = "json"


def viewIndex(**data):
    # if "doc" in data.keys():
    #     del (data["doc"])
    #     del (data["blog"])
    # del (data["cards"])
    # print(data)

    return json.dumps(data).encode()


def viewTags(**data):
    # if "doc" in data.keys():
    #     del (data["doc"])
    #     del (data["blog"])
    # print(data)

    return json.dumps(data).encode()


def viewPage(**data):
    # temporary until object handled
    # if "doc" in data.keys():
    #     del (data["doc"])
    #     del (data["blog"])
    # print(data)

    return json.dumps(data).encode()
