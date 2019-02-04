from typing import Callable
from types import FunctionType
from functools import wraps

import re, unittest

def tag(name:str):
    def decorator(func):
        if "tags" not in func.__dict__:
            func.__dict__["tags"] = []
        func.__dict__["tags"].append(name)


        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def tags(*tags:str):
    def decorator(func):
        if "tags" not in func.__dict__:
            func.__dict__["tags"] = []

        for tag in tags:    
            func.__dict__["tags"].append(tag)


        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def step(keyword:str, template:str):
    def decorator(func):
        func.__dict__["keyword"] = keyword
        func.__dict__["template"] = template

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def keyword(template:str):
    return step("keyword", template)

def given(template:str):
    return step("given", template)

def when(template:str):
    return step("when", template)

def then(template:str):
    return step("then", template)

def but(template:str):
    return step("but", template)