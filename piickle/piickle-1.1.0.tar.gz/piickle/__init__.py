import pickle
from piickle.PickleEnum import PickleEnum

temp_dumps = pickle.dumps
temp_loads = pickle.loads

def dump(object, file):
    encoded_obj = dumps(object)
    file.write(encoded_obj)


def dumps(object):
    byte_object = temp_dumps(object)
    encoded_string = ""
    for byte in byte_object:
        temp = "{0:08b}".format(byte)
        temp = temp.replace("0", PickleEnum.ZERO.value)
        temp = temp.replace("1", PickleEnum.ONE.value)
        encoded_string += temp
    return bytes(encoded_string, "utf-8")


def load(file):
    return loads(file.readline())


def loads(string):
    decoded_string = str(string, "utf-8").replace(PickleEnum.ONE.value, "1")
    decoded_string = decoded_string.replace(PickleEnum.ZERO.value, "0")

    ints_string = []
    for x in range(int((len(decoded_string))/8)):
        ints_string.append(int(decoded_string[8*x:8*x+8], 2))
    return temp_loads(bytes(ints_string))


pickle.dump = dump
pickle.dumps = dumps
pickle.load = load
pickle.loads = loads
