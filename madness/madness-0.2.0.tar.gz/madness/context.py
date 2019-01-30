from inspect import isgenerator, getfullargspec

from werkzeug.local import Local, LocalManager, LocalProxy, LocalStack

from .exceptions import MissingContextVariable

__all__ = 'request', 'context', 'local_manager', 'local', 'Context', 'bind'

local = Local()
local_manager = LocalManager([local])
request = local('request')
context = local('context')

class Context(dict):

    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__

    def run(self, func):
        "pass kwargs directly from this context"
        kwargs = {}
        for key in getfullargspec(func).args:
            try:
                value = self[key]
            except KeyError:
                raise MissingContextVariable(key, func)
            else:
                kwargs[key] = value
        return func(**kwargs)



def bind(endpoint, context_decorators):
    """binds the endpoint to the context
    """

    if not context_decorators:
        return endpoint

    def wrapped_endpoint():
        # run context before/after the endpoint
        # context may catch exceptions

        exitstack = []

        try:
            for func in context_decorators:
                gen = context.run(func)
                if isgenerator(gen):
                    try:
                        # context yielded during except handler
                        response = gen.send(None)
                        if response != None:
                            #print(gen, 'except handler returned', response)
                            break
                    except StopIteration:
                        pass
                    else:
                        exitstack.append(gen)
            else:
                # context did not abort the request
                response = context.run(endpoint)

        except Exception as exception:
            # allow context to recover from an error
            current_exception = exception
            response = None
        else:
            current_exception = None

        #print('unstack', repr(current_exception), 'and', response)

        for gen in reversed(exitstack):
            try:
                if current_exception == None:
                    #print('send', response, 'into', gen)
                    new_response = gen.send(response)
                else:
                    #print('throw', repr(current_exception), 'into', gen)
                    new_response = gen.throw(current_exception)
            except StopIteration:
                pass
            except HTTPException as new_response:
                # abort()/raise used to create a new response
                # continue calling exception handlers
                current_exception = new_response
                response = None
            except Exception as exception:
                current_exception = exception
                response = None
            else:
                if new_response != None:
                    #print(gen, 'modified response', repr(response), 'type=', type(response))
                    current_exception = None
                    response = new_response

        if current_exception != None:
            raise current_exception

        return response

    return wrapped_endpoint
