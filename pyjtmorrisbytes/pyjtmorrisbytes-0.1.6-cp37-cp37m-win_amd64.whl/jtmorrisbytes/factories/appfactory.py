"""
    Name: flaskfactory.py
    Author: Jordan Morris

        This module is responsible for handling default configuration
    and creating application instances.

        The primary goal of this application factory is to handle
    configuration code and provide a way for dependants to access
    an application instance without having to create circular
    dependancies or rely on an init.py file.
        The secondary goal of this appliaction factory is to
    reduce the need to copy/paste or rewrite application
    configuration across all the applications that I make.
    I am hoping that I can write such a configuration that
    will allow me to import this code like a 'drop in' module
    and call create_app and the function would handle creating
    all the config defined in config files or environment
    variables.
        The third goal of this application factory class is to
    provide a common interface for the configuration files. I
    was hoping to use this class to help me generate config
    files if I deemed it to be a helpful and neccessary feature

"""
from flask import Flask
import cython
from os import environ


# implementation notes:
#    Find an easy, expressive manner to construct a config object
#  from all these keys. It would be nice if my applications could
#  use an object like this to configure from code as well as access
#  defaults.
#
#    The primary purpose of this object is to provide a way to be
#  able to query the keys without having to remember them all. 
#  The secondary purpose of this object is to provide sane defaults
#  as fallbacks to querying environment variables
#
#    Maybe there could be a way to use this object to generate a
#  config file if none ws found?
class it(type):
    def __iter__(self):
        # Wanna iterate over a class? Then ask that class for iterator.
        return self.classiter()

@cython.cclass
class ConfigKeyIterator:
    __metaclass__ = it # We need that meta class...
    __by_id = {} # Store the stuff here...

    def __init__(self): # new isntance of class
        __by_id = {key:value for (key,value) in self.__class__.__dict__.items()}

    @classmethod
    def classiter(cls): # iterate over class by giving all instances which have been instantiated
        return iter(cls.__by_id.values())




@cython.cclass
class FlaskKeys(ConfigKeyIterator):
    

    
    FLASK_ENV: cython.unicode = 'FLASK_ENV'
    """Tells flask what environment it is in. FLASK_ENV string: 'production', 'development'
        The following keys are set to True If FLASK_ENV=development:
        FLASK_DEBUG [attribute DEBUG]
        JSONIFY_PRETTY_PRINT
        EXPLAIN_TEMPLATE_RELOADING
        PRESERVE_CONTEXT_ON_EXCEPTION
        TRAP_BAD_REQUEST_ERRORS (if unset) 
    """
    FLASK_DEBUG: cython.unicode = 'FLASK_DEBUG'
    """ Turns on Flask DEBUG Mode. FLASK_DEBUG bool: True, False            
                                                                            
        FLASK_DEBUG [attribute DEBUG]                                       
                                                                            
        When FLASK_DEBUG is True, the following are also turned on by default

        JSONIFY_PRETTY_PRINT
        EXPLAIN_TEMPLATE_RELOADING
        PRESERVE_CONTEXT_ON_EXCEPTION
        TRAP_BAD_REQUEST_ERRORS (if unset)

        in addition, Auto reload will also be turned on when FLASK_DEBUG is True
    """
    TESTING: cython.unicode = 'TESTING'
    """ Enables testing mode: Tells flask to reraise exceptions
        instead of catching them with the apps error handlers

        Turning on testing will enable the following:
        PROPAGATE_EXCEPTIONS    
    """
    PROPAGATE_EXCEPTIONS: cython.unicode = 'PROPAGATE_EXCEPTIONS'
    """ Tells flask to reraise exceptions instead of catching them with the app's error handlers"""

    # PRESERVE_CONTEXT_ON_EXCEPTION: cython.unicode = 'PRESERVE_CONTEXT_ON_EXCEPTION'
    TRAP_HTTP_EXCEPTIONS: cython.unicode = 'TRAP_HTTP_EXCEPITONS'
    """ If there is no handler for an HTTPException-type exception,
        re-raise it to be handled by the interactive debugger instead 
        of returning it as a simple error response.
    """
    TRAP_BAD_REQUEST_ERRORS: cython.unicode = 'TRAP_BAD_REQUEST_ERRORS'
    SECRET_KEY: cython.unicode = 'SECRET_KEY'
    SESSION_COOKIE_NAME: cython.unicode = 'SESSION_COOKIE_NAME'
    SESSION_COOKIE_DOMAIN: cython.unicode = 'SESSION_COOKIE_DOMAIN'
    SESSION_COOKIE_PATH: cython.unicode = 'SESSION_COOKIE_PATH'
    SESSION_COOKIE_HTTPONLY: cython.unicode = 'SESSION_COOKIE_HTTPONLY'
    SESSION_COOKIE_SECURE: cython.unicode = 'SESSION_COOKIE_SECURE'
    SESSION_COOKIE_SAMESITE: cython.unicode = 'SESSION_COOKIE_SAMESITE'
    PERMANENT_SESSION_LIFETIME: cython.unicode = 'PERMANENT_SESSION_LIFETIME'
    SESSION_REFRESH_EACH_REQUEST: cython.unicode = 'SESSION_REFRESH_EACH_REQUEST'
    USE_X_SENDFILE: cython.unicode = 'USE_X_SENDFILE'
    SEND_FILE_MAX_AGE_DEFAULT = 'SEND_FILE_MAX_AGE_DEFAULT'
    SERVER_NAME:cython.unicode = 'SERVER_NAME'
    APPLICATION_ROOT: cython.unicode = 'APPLICATION_ROOT'
    PREFERRED_URL_SCHEME: cython.unicode = 'PREFERRED_URL_SCHEME'
    MAX_CONTENT_LENGTH: cython.unicode = 'MAX_CONTENT_LENGTH'
    JSON_AS_ASCII: cython.unicode = 'JSON_AS_ASCII'
    JSON_SORT_KEYS: cython.unicode = 'JSON_SORT_KEYS'
    JSONIFY_PRETTYPRINT_REGULAR: cython.unicode = 'JSONIFY_PRETTYPRINT_REGULAR'
    JSONIFY_MIMETYPE: cython.unicode = 'JSONIFY_MIMETYPE'
    TEMPLATES_AUTO_RELOAD: cython.unicode = 'TEMPLATES_AUTO_RELOAD'
    EXPLAIN_TEMPLATE_LOADING: cython.unicode = 'EXPLAIN_TEMPLATE_LOADING'
    MAX_COOKIE_SIZE: cython.unicode = 'MAX_COOKIE_SIZE'

class HerokuKeys(ConfigKeyIterator):
    ON_HEROKU: cython.unicode = 'ON_HEROKU'
    """ The key used to detect if you are on heroku or not"""
    POSTGRES_DATABASE_URL: cython.unicode = 'DATABASE_URL'
    CLEARDB_DATABASE_URL: cython.unicode = 'CLEARDB_DATABASE_URL'

class Keys(FlaskKeys, HerokuKeys):
    pass

class Config(object):
    def __init__(self):
        # generate a config object from config keys
        # when init is called
        pass
    # keys = Keys()




# Config.keys.TESTING


class HerokuConfig(object):
    # find a way to detect the various addons that might happen and set the keys depending on 
    def __init__(self):
        pass
    class keys(object):
        
        POSTGRES_DATABASE_URL: cython.unicode = 'DATABASE_URL'


# implementation notes:
# consider using **kwargs for the config object


@cython.returns(object)
@cython.ccall
def create_app(name: str, config: dict, debug: bool=False):
    database_url: cython.unicode = environ.get('DATABASE_URL', 'sqlite:///'+name+'testdb')
    PERMANENT_SESSION_LIFETIME: cython.uint = int(environ.get('PERMANENT_SESSION_LIFETIME', 600))
    default_config: dict = dict()
    # SQLALCHEMY_DATABASE_URI retained for backwards compatibillity
    # with flask-sqlalchemy
    default_config['SQLALCHEMY_DATABASE_URI'] = database_url
        
    default_config['DATABASE_URL'] = database_url
    default_config['PERMANENT_SESSION_LIFETIME'] = \
        environ.get('PERMANENT_SESSION_LIFETIME', 600)
    default_config.update(config)
    app = Flask(name)
    app.config.update(default_config)
    return Flask(name)


