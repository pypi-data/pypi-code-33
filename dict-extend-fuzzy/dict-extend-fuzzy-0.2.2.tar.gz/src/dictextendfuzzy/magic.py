import ctypes

# src: https://stackoverflow.com/questions/24497316/set-a-read-only-attribute-in-python/24498525#24498525
def magic_get_dict(o):
    # find address of dict whose offset is stored in the type
    dict_addr = id(o) + type(o).__dictoffset__
    # retrieve the dict object itself
    dict_ptr = ctypes.cast(dict_addr, ctypes.POINTER(ctypes.py_object))
    return dict_ptr.contents.value

def magic_flush_mro_cache():
    ctypes.PyDLL(None).PyType_Modified(ctypes.cast(id(object), ctypes.py_object))
