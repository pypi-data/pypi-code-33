# ----------------------------------------------------------------------------
#    Copyright 2018 MonaLabs.io
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# ----------------------------------------------------------------------------
"""
The main Mona python client module. Exposes all functions relevant for client
handling, mainly including context configuration and exporting mechanism.
"""
# TODO(itai): Consider adding capability for several context ids in parallel,
# allowing exporting to several ARCs.

import atexit
import collections
import json
import os
import sys
import uuid
from contextlib import contextmanager

import pkg_resources
from fluent import asyncsender as sender
from werkzeug.local import Local, LocalManager

from .logger import LOGGER

from .mona_configuration import configuration

CONTEXT_SEPARATOR = '.'

# Configuration variables

MONA_HOST = os.environ.get('MONA_HOST') or '127.0.0.1'
MONA_PORT = os.environ.get('MONA_PORT') or 24224
MONA_PORT = int(MONA_PORT)
# MONA_USER_ID is a unique identifier that should be supplied to you by Mona.
MONA_USER_ID = os.environ.get('MONA_USER_ID') or 'EMPTY'
MONA_QUEUE_SIZE = os.environ.get('MONA_QUEUE_SIZE') or 20
MONA_QUEUE_SIZE = int(MONA_QUEUE_SIZE)

ARC_CLASS_FIELD_NAME = "MONA_ARC_CLASS"

# Init global fluentd sender for future message exports.

sender.setup(
    'mona.client',
    host=MONA_HOST,
    port=MONA_PORT,
    queue_circular=True,  # This makes sure the sender will never block.
    # This limits the amount of messages mona saves.
    queue_maxsize=MONA_QUEUE_SIZE,
    use_ssl=True,
    ssl_server_hostname="raw.monalabs.io")

_GLOBAL_SENDER = sender.get_global_sender()

# TODO(itai): Also support asyncio with context variables. This only handles
# threads and greenlets.
_LOCAL = Local()
_LOCAL_MANAGER = LocalManager([_LOCAL])
_LOCAL.contexts = []
"""
List of all currently active context and subcontexts.
"""

_LOCAL.protected_contexts = []
"""
List of sub_contexts indices (to map to LOCAL.contexts) currently opened with a
context manager and that should therefore never be manually closed.

This is done to assure that if you are in a "with" block, you can be certain
that the context you opened in the "with" statement is still open.
"""

_global_init_message = {}
"""A message to be sent on each new main context after init."""


def _get_local_list_attr(name):
    return getattr(_LOCAL, name, [])


def _get_protected_contexts():
    return _get_local_list_attr('protected_contexts')


def _get_contexts():
    return _get_local_list_attr('contexts')


def _set_protected_contexts(new_id):
    amount_of_contexts = new_id.count(CONTEXT_SEPARATOR) + 1
    start_from_index = len(_LOCAL.contexts) - amount_of_contexts
    _LOCAL.protected_contexts = _get_protected_contexts() + list(
        range(start_from_index, start_from_index + amount_of_contexts))
    return amount_of_contexts


def _export_arc_class(arc_class=None):
    if arc_class:
        _inner_export({ARC_CLASS_FIELD_NAME: arc_class})


def _on_disable(return_value='', should_yield=False):
    def real_decorator(func):
        if should_yield:

            def generator_wrapper(*args, **kwargs):
                if configuration['disable_all']:
                    yield return_value
                    return
                yield from func(*args, **kwargs)
                return

            return generator_wrapper

        def wrapper(*args, **kwargs):
            if configuration['disable_all']:
                return return_value
            return func(*args, **kwargs)

        return wrapper

    return real_decorator


@contextmanager
@_on_disable(should_yield=True)
def new_mona_context(arc_class=None, context_id=''):
    """
    Returns a new context manager for a head context. This is usually the first
    function you should call in this module. Use with a "with" statement to
    make sure the context is closed when you're done using it.

    Parameters - see init() docs.
    """
    if _get_protected_contexts():
        LOGGER.error(
            'Tried to init inside a context manager. Keeping same context.')
        yield get_full_context_id()
        return

    reset()
    context_id = init(arc_class, context_id)

    _set_protected_contexts(context_id)

    try:
        yield context_id

    finally:
        _LOCAL.contexts = []
        _LOCAL.protected_contexts = []


@contextmanager
@_on_disable(should_yield=True)
def new_mona_sub_context(arc_class=None, sub_context_id=''):
    """
    Returns a new context manager for a sub_context. Sub contexts are used as
    syntactic separators between different parts of an algorithm's run, but
    currently don't hold any real semantic value.
    
    This is the same as new_mona_context but should only be used inside an
    existing context.
    """
    context_id = init_sub_context(arc_class, sub_context_id)
    if not context_id:
        yield ''
        return

    _set_protected_contexts(context_id)

    try:
        yield context_id

    finally:
        # Remove this sub-context and all its sub-contexts from protected
        first_sub_context = _get_split_contexts(context_id)[0]
        sub_context_index = _LOCAL.contexts.index(first_sub_context)
        _LOCAL.protected_contexts = [
            x for x in _get_protected_contexts() if x < sub_context_index
        ]

        # Now close it.
        close_sub_context(context_id.split(CONTEXT_SEPARATOR)[0])


@_on_disable()
def get_full_context_id():
    """
    Returns the full context id for the current ARC. This is a string
    containing the main context id and all the sub context ids delimited by
    CONTEXT_SEPARATOR.
    """
    return CONTEXT_SEPARATOR.join(_get_contexts())


def _get_split_contexts(full_id):
    return full_id.split(CONTEXT_SEPARATOR)


def _set_contexts_from_string(contexts_string):
    """
    Sets the current contexts according to the given string, or using a uuid if
    no string was provided.
    """
    if contexts_string:
        _LOCAL.contexts = _get_split_contexts(contexts_string)
    else:
        _LOCAL.contexts = [str(uuid.uuid1())]


@_on_disable()
def init(arc_class=None, context_id=''):
    """
    Inits the current context with a new context, completely forgetting the old
    contexts (like when using reset()).
    
    NOTE: Considered part of the advanced API. Use new_mona_context unless you
    know what you are doing.

    Parameters
    ----------
    arc_class : string
        The class of this context. Use this to separate between runs of
        different algorithms. Classes are used by Mona to know which ARCS and
        sub-ARCs to compare against eachother.
    context_id : string
        The full context id (using CONTEXT_SEPARATOR to separate sub-contexts)
        to init this new context. Should usually be left empty.
    """
    if _get_protected_contexts():
        LOGGER.error(
            'Tried to init inside a context manager. Keeping same context.')
        return get_full_context_id()

    _set_contexts_from_string(context_id)
    LOGGER.info('Mona context after initing: %s', get_full_context_id())

    _export_arc_class(arc_class)
    if _global_init_message:
        export(_global_init_message)

    return get_full_context_id()


@_on_disable()
def init_sub_context(arc_class=None, sub_context_id=''):
    """
    Inits a new sub context, with the given name if provided, or a uuid if not.
    
    NOTE: Considered part of the advanced API. Use new_mona_sub_context unless
    you know what you are doing.

    Parameters
    ----------
    arc_class : string
        The class of this sub-context. Use this to separate between runs of
        different parts of the algorithm. Classes are used by Mona to know
        which ARCS and sub-ARCs to compare against eachother.
    sub_context_id : string
        The full sub-context id (using CONTEXT_SEPARATOR to separate
        sub-contexts) to init this new sub-context. Should usually be left
        empty.
    """
    if not _LOCAL.contexts:
        LOGGER.error('Tried to create subcontext before init')
        return ''

    sub_context_id = sub_context_id or str(uuid.uuid1())
    _LOCAL.contexts = _get_contexts() + _get_split_contexts(sub_context_id)
    LOGGER.info('Mona context after initing sub context: %s',
                get_full_context_id())
    _export_arc_class(arc_class)
    return sub_context_id


@_on_disable()
def close_sub_context(sub_context_id=''):
    """
    Closes the given sub context, or the last one if none is provided.
    
    NOTE: Considered part of the advanced API. Use new_mona_sub_context unless
    you know what you are doing.
    """
    sub_context_index = _LOCAL.contexts.index(
        sub_context_id) if sub_context_id else len(_LOCAL.contexts) - 1
    if sub_context_index < 1:
        LOGGER.error('Tried to close non-existing subcontext')
        return get_full_context_id()

    if sub_context_index <= max(_get_protected_contexts()):
        LOGGER.warning(
            """Tried to close sub context from within it's own context. \
            When using a context manager ('with statement') close is \
            triggered implicitly...""")
        return get_full_context_id()

    _LOCAL.contexts = _LOCAL.contexts[:sub_context_index]

    LOGGER.info('Mona context after closing sub context: %s',
                get_full_context_id())

    return get_full_context_id()


def _is_jsonable(message):
    try:
        json.dumps(message)
        return True
    except:
        return False


def _check_message(message):
    if not isinstance(message, collections.Mapping):
        LOGGER.error('Tried to send non-dict message to mona')
        return False

    if not _is_jsonable(message):
        LOGGER.error('Tried to send non-json message to mona')
        return False

    return True


@_on_disable(return_value=None)
def _inner_export(message):
    if not _LOCAL.contexts:
        LOGGER.error('Tried to export out of context')
        return

    if not _check_message(message):
        return

    try:
        _GLOBAL_SENDER.emit(
            'message', {
                'user_id': MONA_USER_ID,
                'context': get_full_context_id(),
                'message': message
            })
    except Exception:
        LOGGER.warning("Couldn't send message to mona: %s", sys.exc_info())


@_on_disable(return_value=None)
def export(message):
    """
    This funciton holds the main funtionality of the client. Using any json
    message as the input parameter, this function will send out the message to
    Mona's systems.

    Parameters
    ----------
    message : dict
        A dict to be parsed as json and sent to mona servers.
        NOTE: Don't use field names with "MONA_" as their prefix. Mona uses
        this pattern internally. If you do that, these fields will be discarded
        before being emitted to Mona.
    """
    if not _check_message(message):
        return

    message_copy = dict(message)

    for key in message:
        if key.startswith('MONA_'):
            del message_copy[key]

    if message_copy:
        return _inner_export(message_copy)


@_on_disable(return_value=None)
def reset():
    """
    Resets the client to hold no context.
    
    NOTE: Considered part of the advanced API. Use new_mona_context unless you
    know what you are doing.
    """
    LOGGER.info('reseting mona context to empty')
    _LOCAL.contexts = []


@_on_disable(return_value=None)
def set_global_init_message(message):
    """
    Sets a message to be exported to mona for every inited main context. This
    is useful, for example, for sending mona environment data, such as telling
    mona all ARCs created are of the testing environment.

    Parameters
    ----------
    message : dict
        A dict to be parsed as json and sent to mona servers on each new init.
    """
    if not _check_message(message):
        return

    global _global_init_message
    _global_init_message = message


atexit.register(sender.close)
