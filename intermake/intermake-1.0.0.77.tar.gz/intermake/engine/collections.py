"""
Houses the PluginManager and PluginFolder classes.
"""
from mhelper import exception_helper
from typing import Iterator, cast, Collection, Optional

import itertools
import warnings

from intermake.engine.abstract_command import Command
from intermake.engine.help import HelpTopic


class _ChainedCollection:
    """
    ABSTRACT
    
    A collection that can inherit a previous set of values.
    """
    
    
    def __init__( self, comment: str, inherit: Optional[Collection] ):
        self.__inherit: Collection = inherit if inherit is not None else ()
        self.__comment = comment
        self.__contents = []
    
    
    def __repr__( self ):
        return "{}({})".format( type( self ).__name__, repr( self.__comment ) )
    
    
    def _append( self, x ):
        self.__contents.append( x )
    
    
    def __len__( self ):
        return len( self.__inherit ) + len( self.__contents )
    
    
    def __iter__( self ):
        return iter( itertools.chain( self.__inherit, self.__contents ) )


class CommandCollection( _ChainedCollection ):
    """
    FINAL OVERRIDE
    
    Manages a set of `Command`s.
    """
    
    
    def __init__( self, comment: str, inherit: Optional[Collection] ):
        super().__init__( comment, inherit )
    
    
    def register( self, command: object = None, **kwargs ) -> object:
        """
        Registers and optionally generates a `Command`
        - OR - 
        creates a decorator capable of doing so.
        
        Example::
        
            @𝑥.register(name = "say_hello")
            def my_command():
                print("hello, world")
                
        Example::
        
            𝑥.register(my_command, name="say_hello")
            
        Example::
        
            cmd = BasicCommand(my_command, name="say_hello")
            𝑥.register(cmd)
                                                   
        :param command:    What to register, one of:
                           `Command`  : registers and returns the specified command
                           `function` : creates and registers a `BasicCommand`, initialised
                                        with the specified `function` and `kwargs`. The
                                        original `function` is returned so that, when used as a
                                        decorator, `register` does not affect the `function` itself.
                           `None`     : returns a decorator equivalent to `register`, but using the
                                        provided `kwargs`. This allows decorators to be built up for
                                        convenience. e.g. `game = register( folder =
                                        "games" )` provides an `game` function which behaves the
                                        same as the `register` function but defaults creating 
                                        commands in the "games" folder.
        :param kwargs:     Arguments used to initialise an `BasicCommand`.
                           These must be blank if an already-prepared `Command` is being specified
                           instead of a `function`. 
        :return:           Dependent upon `command`.
        """
        orig = command
        
        if command is None:
            def __register( command: object = None, **kwargs2 ):
                return self.register( command, **kwargs, **kwargs2 )
            
            
            return __register
        
        if not isinstance( command, Command ):
            from intermake.framework.basic_command import BasicCommand
            command = BasicCommand( function = cast( callable, command ), **kwargs )
        elif kwargs:
            raise ValueError( "The object «{}» is already a `Command` instance (not a plain `callable`). `kwargs` «{}» have been provided to `register` but this doesn't make sense because no `Command` is being created so these arguments won't be used. Please remove the ambiguity in the code that is attempting to register this command.".format( command, kwargs ) )
        
        # 
        # Check the `command` is an `Command`
        #
        exception_helper.safe_cast( "command", command, Command )
        
        # Check that the command isn't already registered
        if command in self:
            raise KeyError( "The command `{0}` is exported more than once. Check that you haven't accidentally re-exported a command.".format( repr( command ) ) )
        
        # Add the command itself
        self._append( command )
        
        # Raise an error for any conflicting names
        for other_command in self:
            if other_command is not command:
                for name in command.names:
                    if name in other_command.names:
                        raise ValueError( "There are two commands with the same name: `{}` - `{}` and `{}`".format( repr( name ), repr( command ), repr( other_command ) ) )
        
        return orig
    
    
    def __iter__( self ) -> "Iterator[Command]":
        return super().__iter__()


class HelpTopicCollection( _ChainedCollection ):
    """
    FINAL OVERRIDE
    
    Maintains a collection of `HelpTopic`s.
    """
    
    
    def add( self, *args, **kwargs ) -> None:
        """
        Adds a help topic.
        
        Provide either:
            * A `HelpTopic` instance.
            * The arguments to be passed to a new `HelpTopic` instance.
            
        If a topic with the same key already exists, the previous topic will be
        renamed and a warning will be issued. The keys `topics` and
        `cmdlist` have special usages.
        """
        if len( args ) == 1 and isinstance( args[0], HelpTopic ):
            topic = args[0]
        else:
            topic = HelpTopic( *args, **kwargs )
        
        for existing in self:
            if existing.key == topic.key:
                n = next( n for n in itertools.count( 2 ) if not any( (x is not existing and x.key == "{} {}".format( existing.key, n )) for x in self ) )
                existing.key = "{} {}".format( existing.key, n )
                
                warnings.warn( "A help topic with the key '{}' already exists. "
                               "The previous topic has been renamed '{}'"
                               .format( topic.key, existing.key ),
                               UserWarning )
        
        self._append( topic )
    
    
    def __iter__( self ) -> Iterator[HelpTopic]:
        return super().__iter__()
