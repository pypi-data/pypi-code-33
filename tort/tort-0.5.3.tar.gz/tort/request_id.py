import contextvars

request_id_var = contextvars.ContextVar('request_id')


def get():
    return request_id_var.get()


def set(value):
    request_id_var.set(value)
