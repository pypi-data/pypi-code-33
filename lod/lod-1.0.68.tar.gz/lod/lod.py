"""
This is the library that should be used by any program using Python 3.

It is a simple interface that takes care of loading input files and generating output files in the right format.
"""
# this file should be compatible with both Python 2 and Python 3!
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from io import open

import json
import os
import sys

from . import basics
from . import utilities

_initialized = False
_object_manager = None
def _initialize_if_not_done_yet():
    global _initialized
    if _initialized:
        return
    # configure a variable to give any preliminary Identifiers created here an origin
    # which can be used to differentiate those created by the server, by Programs, and by the lod-executor
    _, name, version = get_own_program_details()
    source_name = "Program '%s#%s'" % (name, version,)
    basics.configure_name_for_source_of_preliminary_identifiers(source_name)
    # load the object_manager
    global _object_manager
    _object_manager = basics.parse_object_manager(_get_input()['object_manager'])
    basics._the_object_manager = _object_manager
    # for all FileObjects that get used as an input file here, add a 'file' field that refers to the file.
    for i, input_file_object_identifier in enumerate(_get_input()['input_file_object_identifiers']):
        input_file_object = _object_manager.get_object_for_identifier(basics.parse_identifier(input_file_object_identifier))
        input_file_object.file = os.path.join(PATH_PREFIX, "in_%d" % i)
    # finish initialization
    _initialized = True


##############################################################################################################
# constants
##############################################################################################################


PATH_PREFIX = '/lod'
INPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'in.txt')
OUTPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'out.txt')


##############################################################################################################
# a context manager to take care of logging and error handling
##############################################################################################################


_the_manager = None
class manager:
    """
    A context manager that takes care of logging and error handling.

    It is recommended that you wrap the main function of your project with this context manager. Doing so has several effects:

    * all print() statements or other messages to sys.stdout will be written to a log file.

    * if an exception occurs, the exception is also logged in an error file.
    """
    def __init__(self, suppress_exceptions_after_logging_them=False, redirect_stdout_to_log=True):
        global _the_manager
        if _the_manager is None:
            _the_manager = self
            _initialize_if_not_done_yet()
        else:
            warning = "only one manager of the LOD library should be created!"
            print(warning)
            raise IOException(warning)
        self.suppress_exceptions_after_logging_them = suppress_exceptions_after_logging_them
        self.error_file = os.path.join(PATH_PREFIX, 'error.txt')
        self.log_file = os.path.join(PATH_PREFIX, 'log.txt')
        self.redirect_stdout_to_log = redirect_stdout_to_log
    def __enter__(self):
        self.log_file_stream = utilities.open_with_blackjack_and_hookers(self.log_file)
        self.log_file_stream.__enter__()
        if self.redirect_stdout_to_log:
            self.previous_stdout = sys.stdout
            sys.stdout = self.log_file_stream
        return self
    def __exit__(self, etype, value, exception_traceback):
        try:
            # stop redirecting stdout to the log file
            if self.redirect_stdout_to_log:
                sys.stdout = self.previous_stdout
            # close the log file
            self.log_file_stream.__exit__(etype, value, exception_traceback)
            # save the output to file
            save_output_to_file()
        except Exception:
            if etype is None:
                etype, value, exception_traceback = sys.exc_info()
        finally:
            # log any uncaught exceptions that may have occurred
            if exception_traceback:
                error_message = utilities.get_error_message_details((etype, value, exception_traceback))
                with utilities.open_with_blackjack_and_hookers(self.error_file) as f:
                    f.write(error_message)
                # allow the exception to continue, if required
                return self.suppress_exceptions_after_logging_them
            else:
                # no error, so nothing needs to be done
                pass
    def log(self, message):
        """
        Log a message to the log file.
        This file is available via the Elody website for inspection, but is not available to other programs running in Elody.
        You can also use print() statements or other commands that write to sys.stdout to achieve the same effect.
        """
        self.log_file_stream.write(message)
        self.log_file_stream.write('\n')


def log(message):
    """
    Uses the context manager for logging.
    The manager needs to be created in order to use logging.
    """
    if _the_manager is None:
        raise IOError("the LOD library's manager needs to be created in order to use logging.")
    _the_manager.log(message)


##############################################################################################################
# input
##############################################################################################################


_input = None
def _get_input():
    """
    Parse the input file. This uses a cache, so it only has to be done once.
    """
    global _input
    if _input is None:
        with open(INPUT_FILE_LOCATION, 'r', encoding='utf8') as f:
            _input = json.load(f)
    return _input


def get_object_manager():
    """
    Parse the :class:`lod.basics.ObjectManager` from the input.
    This holds a history of everything that has happened in this scenario so far.
    """
    _initialize_if_not_done_yet()
    return _object_manager


def get_current_step():
    """
    Returns an integer indicating the number of the current step in the scenario.
    """
    _initialize_if_not_done_yet()
    return get_object_manager().get_current_step()


def get_own_program_details():
    """
    Returns a tuple of (identifier, name, version) for the program that is currently being executed.
    """
    identifier = basics.parse_identifier(_get_input()['program_identifier'])
    name, version = identifier.get_program_name_and_version_separately()
    return identifier, name, version


def get_event_of_this_execution():
    """
    Returns the current event.
    """
    _initialize_if_not_done_yet()
    identifier = basics.parse_identifier(_get_input()['event_identifier'])
    res = get_object_manager().get_object_for_identifier(identifier)
    return res


def get_program_arguments():
    """
    Returns a dictionary mapping each argument name to the corresponding object or list of objects that were given to this program.
    """
    _initialize_if_not_done_yet()
    arguments = _get_input()['arguments']
    res = {}
    for name, val in arguments.items():
        if isinstance(val, list):
            res[name] = [get_object_manager().get_object_for_identifier(basics.parse_identifier(a)) for a in val]
        else:
            res[name] = get_object_manager().get_object_for_identifier(basics.parse_identifier(val))
    return res


##############################################################################################################
# output
##############################################################################################################


_output_objects = []


def _add_output_object(obj):
    """
    Add an object to the Execution Environment.
    """
    global _output_objects
    _object_under_constuction_check(0)
    _output_objects.append(obj)
    get_object_manager().add_object(obj)


_object_under_construction_counter = 0
def _object_under_constuction_check(c):
    """
    A helper function to raise an exception if an object is created while a :class:`lod.basics.MessageBuilder` is still unfinished.
    """
    global _object_under_construction_counter
    _object_under_construction_counter += c
    if (c == 0 and _object_under_construction_counter != 0) or (c == 1 and _object_under_construction_counter != 1):
        raise ValueError("Can't create another object while a Message is being constructed! Did you forget to call .finish() on a MessageBuilder?")


_output_files_counter = 0
def file(file_name):
    """
    Creates a new :class:`lod.basics.FileObject`.

    Create an output file, to make the results of this program available to other programs and to the scenario.
    You can create multiple output files, and they will be added in the order in which they were created with this function.

    Note that until the server confirms the creation of this object, it uses a preliminary :class:`lod.basics.Identifier` and some fields that will be automatically filled in by the server are not set until then.
    """
    _initialize_if_not_done_yet()
    global _output_files_counter
    global _output_objects
    identifier = basics.create_preliminary_identifier('file')
    creation_index = _output_files_counter
    creation_step = get_current_step()
    res = basics.FileObject(identifier, file_name, creation_step, creation_index)
    res.file = os.path.join(PATH_PREFIX, "out_%d" % _output_files_counter)
    _output_files_counter += 1
    _add_output_object(res)
    return res


def tag(symbol, comment=None, weight=None, arguments=None, also_create_signal=False):
    """
    Creates a new :class:`lod.basics.Tag`.

    :param str symbol: The symbol of the Tag

    :param str comment: The comment of the Tag

    :param list arguments: A list of arguments, given either as objects or their :class:`lod.basics.Identifier`.

    :param bool also_create_signal: If True, creates an additional Tag with the Symbol !set_signal_weight and the same comment and weight as this Tag (the weight defaults to 1.0 if this Tag has no weight).

    Note that until the server confirms the creation of this object, it uses a preliminary :class:`lod.basics.Identifier` and some fields that will be automatically filled in by the server are not set until then.
    """
    _initialize_if_not_done_yet()
    if arguments is None:
        arguments = []
    res = basics.Tag(basics.create_preliminary_identifier('tag'), arguments, symbol_name=symbol, comment=comment, weight=weight)
    _add_output_object(res)
    # for every object of type TagBuilder that has also_create_signal==True, create an additional output_object
    if also_create_signal:
        signal_weight = 1.0 if res.weight is None else res.weight
        tag('!set_signal_weight', comment=res.comment, weight=signal_weight, arguments=[res])
    return res


def execute_program(program_identifier, **argument_dict):
    """
    Creates `an Event to execute a Program <https://elody.com/tutorial/documentation_objects/#event_execute_program>`_.
    This expects a program as its first argument, and files to use as parameters as the rest.
    The program may be identified as an :class:`lod.basics.Identifier` object,
    as a String displaying the name of the program (in which case the latest version is picked),
    as a String of <name>#<version> (which identifies the version directly),
    or as an integer that is the program's ID (which is unambiguous and includes the version).

    Note that until the server confirms the creation of this object, it uses a preliminary :class:`lod.basics.Identifier` and some fields that will be automatically filled in by the server are not set until then.
    """
    _initialize_if_not_done_yet()
    request = basics.ProgramExecutionRequest().program(program_identifier).arguments(**argument_dict)
    _add_output_object(request)
    return request


def start_message():
    """
    Returns a :class:`lod.basics.MessageBuilder`, which is used for building a :class:`lod.basics.Message` to display to the user. Various options can be added via method-chaining. Don't forget to call finish() on the :class:`lod.basics.MessageBuilder` when you are done.

    Note that until the server confirms the creation of this object, it uses a preliminary :class:`lod.basics.Identifier` and some fields that will be automatically filled in by the server are not set until then.
    """
    _initialize_if_not_done_yet()
    def callback(message_builder):
        # Replace the Identifier of the Message with a newer one.
        # This is done so that the Message can be built piecemeal and can refer to
        # Turn the MessageBuilder into a Message before saving and returning it
        message = basics.parse_message(message_builder.to_json())
        _object_under_constuction_check(-1)
        _add_output_object(message)
        return message
    _object_under_constuction_check(1)
    message_builder = basics.MessageBuilder(callback=callback)
    return message_builder


def option(starting_confidence, name, description, trigger, display, actions, existing_variables=None):
    """
    Creates an :class:`lod.basics.Option` and adds it to the list of objects.

    :param object name, description, trigger, display, actions, existing_variables: See `here <https://elody.com/tutorial/documentation_objects/#option_verifier>`_. Each of these objects should be given as a JSON object, i.e. a nested structure of dictionaries, lists, and primitive values.

    :param float starting_confidence: If this is not None, also creates a !set_option_confidence Tag with this weight and applies it to the Option.

    Note that until the server confirms the creation of this object, it uses a preliminary :class:`lod.basics.Identifier` and some fields that will be automatically filled in by the server are not set until then.
    """
    _initialize_if_not_done_yet()
    if existing_variables is None:
        existing_variables = {}
    option = basics.Option(basics.create_preliminary_identifier('option'), name, description, trigger, display, actions, existing_variables)
    _add_output_object(option)
    if starting_confidence is not None:
        tag('!set_option_confidence', arguments=[option], weight=starting_confidence)
    return option


def save_output_to_file():
    """
    Creates the output file and write all previously added objects to it.
    This function is called automatically when the :class:`manager` closes, but it is possible to call it earlier too.
    """
    global _output_objects
    # add all the output objects to the file
    res = {
        'output_objects' : [a.to_json() for a in _output_objects],
    }
    # To help with detecting errors when an invalid value is added, first json.dumps each individual object to find out where the error occurs
    for a in res['output_objects']:
        try:
            json.dumps(res)
        except:
            error_message = "Failed to convert this object to JSON:\m%s" % a
            raise TypeError(error_message)
    # write to file
    with open(OUTPUT_FILE_LOCATION, 'w', encoding='utf8') as f:
        # get the json as a string, which may or may not be unicode depending on the python version
        s = json.dumps(res, indent=4)
        # make sure it's unicode (important for python 2)
        if isinstance(s, str):
            if hasattr(s, 'decode'):
                s = s.decode('utf-8')
        # write unicode to file
        f.write(s)
