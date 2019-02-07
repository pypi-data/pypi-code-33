# -*- coding: utf-8 -*-
# Copyright 2019 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
""" restible-swagger decorators. """
from __future__ import absolute_import, unicode_literals


from . import util


def responses(resp_def):
    """ Define responses for the given handlers. """
    def decorator(fn):  # pylint: disable=missing-docstring
        fn._api_responses = resp_def
        return fn
    return decorator


def response(status, response_def):
    """ Define a single response for the given handler.

    You can define multiple responses for the given handler by using this
    decorator multiple times.
    """
    def decorator(fn):  # pylint: disable=missing-docstring
        responses = getattr(fn, '_api_responses', {})
        responses[status] = response_def
        fn._api_responses = responses
        return fn
    return decorator


def response_200(description, array=False):
    """ A standard HTTP 200 response

    A quick helper to easily define a standard 200 response where the response
    schema matches the main resource schema for any given restible resource.
    """
    def decorator(fn):  # pylint: disable=missing-docstring
        responses = getattr(fn, '_api_responses', {})
        responses['200'] = {
            "description": description,
            "schema": "__self_array__" if array else "__self__",
        }
        fn._api_responses = responses
        return fn
    return decorator


def response_201(description):
    """ A standard HTTP 201 response

    A quick helper to easily define a standard 201 response where the response
    schema matches the main resource schema for any given restible resource.
    """
    def decorator(fn):  # pylint: disable=missing-docstring
        responses = getattr(fn, '_api_responses', {})
        responses['201'] = {
            "description": description,
            "schema": "__self__",
        }
        fn._api_responses = responses
        return fn
    return decorator


def response_401():
    """ A standard HTTP 401 response

    A quick helper for defining 401 responses. If you're using a custom error
    schema you'll have to build those manually. Otherwise you can use this
    little helper.
    """
    def decorator(fn):  # pylint: disable=missing-docstring
        responses = getattr(fn, '_api_responses', {})
        responses['401'] = util.RESPONSE_401
        fn._api_responses = responses
        return fn
    return decorator


def response_403():
    """ A standard HTTP 403 response

    A quick helper for defining 403 responses. If you're using a custom error
    schema you'll have to build those manually. Otherwise you can use this
    little helper.
    """
    def decorator(fn):  # pylint: disable=missing-docstring
        responses = getattr(fn, '_api_responses', {})
        responses['401'] = util.RESPONSE_401
        fn._api_responses = responses
        return fn
    return decorator


def response_404():
    """ A standard HTTP 404 response

    A quick helper for defining 404 responses. If you're using a custom error
    schema you'll have to build those manually. Otherwise you can use this
    little helper.
    """
    def decorator(fn):  # pylint: disable=missing-docstring
        responses = getattr(fn, '_api_responses', {})
        responses['404'] = util.RESPONSE_404
        fn._api_responses = responses
        return fn
    return decorator
