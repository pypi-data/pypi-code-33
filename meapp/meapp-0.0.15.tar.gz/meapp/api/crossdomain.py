

def crossappend(response):
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response[
        "Access-Control-Allow-Headers"] = "Accept,Accept-Language,Content-Language,Content-Type,X-Custom-Header,x-requested-with,origin,authorization,x-csrftoken,token"


def crossdomain(prefix):
    def cross_decorator(f):
        def wrapper(*args, **kw):
            response = f(*args, **kw)
            crossappend(response)
            return response
        return wrapper
    return cross_decorator
