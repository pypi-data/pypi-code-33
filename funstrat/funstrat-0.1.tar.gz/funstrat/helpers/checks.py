from functools import wraps
import inspect




def param_names(func):
    
    def wrapper(one, two, *args, **kwargs):
        frame = inspect.currentframe()
        frame = inspect.getouterframes(frame)[1]
        print(frame)
        string = inspect.getframeinfo(frame[0]).code_context[0].strip()
        print(string)
        args = string[string.find('(') + 1:-1].split(',')
        n = []
        for i in args:
            if i.find('=') != -1:
                n.append(i.split('=')[1].strip())

            else:
                n.append(i)
        
        return func(*args, names=n, **kwargs)
    return wrapper


"""

"""

def checkinst(one, two, is_except=False):
    frame = inspect.currentframe()
    frame = inspect.getouterframes(frame)[1]
    string = inspect.getframeinfo(frame[0]).code_context[0].strip()
    args = string[string.find('(') + 1:-1].split(',')
    n = []
    for i in args:
        if i.find('=') != -1:
            n.append(i.split('=')[1].strip())

        else:
            n.append(i)
    if not isinstance(one, two):
        if is_except:
            raise TypeError(f"{n[0]} is not an instance or type of {n[1]}")
        else:
            return False
    else:
        return True
if __name__ == "__main__":
    checkinst(1, int)