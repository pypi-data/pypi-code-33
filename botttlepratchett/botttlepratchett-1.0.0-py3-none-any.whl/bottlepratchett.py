import bottle

def wrap(callback):
    def wrapper(*args, **kwargs):
        body = callback(*args, **kwargs)
        bottle.response.headers['X-Clacks-Overhead'] = 'GNU Terry Pratchett'
        return body
    return wrapper
