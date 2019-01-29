"""
Contains the `BasicCommand` class, as well as the related decorator `command`.
"""
import warnings
from typing import List, Optional, Union
from mhelper import FunctionInspector, IFunction, NotFoundError, override

from intermake.engine import Application, Command, Visibility


def command( *args, **kwargs ):
    """
    This is a convenience function which wraps to `Application.LAST.command`.
    
    `command` and `register` are synonymous for legacy reasons.
    """
    warnings.warn( "This function is deprecated. Please use `<your app>.command()` instead.", DeprecationWarning )
    return Application.LAST.command( *args, **kwargs )


def register( *args, **kwargs ):
    """
    Same as `command`.
    """
    warnings.warn( "This function is deprecated. Please use `<your app>.command()` instead.", DeprecationWarning )
    return Application.LAST.command( *args, **kwargs )


class BasicCommand( Command ):
    """
    Wraps a Python function into a `Command` object.
    """
    COMMAND_TAG = "BasicCommand"
    
    
    def __init__( self,
                  *,
                  function: IFunction,
                  true_function = None,
                  names: Optional[Union[str, List[str]]] = None,
                  description: Optional[str] = None,
                  visibility: Optional[Visibility] = None,
                  highlight: bool = False,
                  folder: Optional[str] = None ):
        """
        CONSTRUCTOR
        
        See `Command.__init__` for argument descriptions.
        
        Note that several of the arguments get defaults from the function via reflection, if not provided.
        
        :param function:        Function to call.
                                Command arguments are constructed via reflection, hence this must be a fully annotated function.
                                Any argument named `self` is ignored.
        
        :param true_function:   Function to call. `function` is then only used for the reflection stage. If `None`, `function` is used for reflection and calling.
        :param names:           As `Command.__init__`, but a default name (the function name) is used if this is `None`.
        :param description:     As `Command.__init__`, but a default description (the function documentation) is used if this is `None`.
        :param visibility:      As `Command.__init__`.
        :param highlight:       As `Command.__init__`.
        :param folder:          As `Command.__init__`.
        """
        self.function_info = FunctionInspector( function ) if function is not None else None
        
        if function is not None:
            if not names:
                names = []
            
            if function.__name__ not in names:
                names = list( names ) + [function.__name__.strip( "_" )]
        elif not names:
            raise ValueError( "If `function` is not provided then `names` must be." )
        
        args = []
        
        for arg in (self.function_info.args if function is not None else ()):
            if arg.name != "self":
                args.append( arg )
        
        if not description:
            if function is not None:
                description = self.function_info.description
            
            if not description:
                description = ""
        
        super().__init__( names = names,
                          documentation = description,
                          highlight = highlight,
                          visibility = visibility,
                          folder = folder,
                          args = args )
        
        self.function = true_function if true_function is not None else function
        setattr( self.function, self.COMMAND_TAG, self )
        
        assert self.function is not None and hasattr( self.function, "__call__" ), (
            "A `{}` requires a callable object or `None` as its `function`, but this object «{}» : «{}» is not callable."
                .format( BasicCommand.__name__,
                         type( self.function ),
                         self.function ))
    
    
    def __eq__( self, other ):
        return self is other or self.function is other
    
    
    def __hash__( self ):
        return object.__hash__( self )
    
    
    @classmethod
    def retrieve( cls, function ) -> Command:
        """
        If an `BasicCommand` was created from a function, returns the `BasicCommand` object.
        """
        if hasattr( function, cls.COMMAND_TAG ) and isinstance( getattr( function, cls.COMMAND_TAG ), Command ):
            return getattr( function, cls.COMMAND_TAG )
        
        raise NotFoundError( "The specified object «{}» has no `.{}` tag. "
                             " Check the object is a function and has been bound to a `{}`, for instance using the `@{}.{}` decorator."
                             .format( function,
                                      cls.COMMAND_TAG,
                                      Command.__name__,
                                      Application.__name__,
                                      Application.command.__name__ ) )
    
    
    @override
    def on_run( self, *args, **kwargs ) -> Optional[object]:
        """
        INHERITED
        """
        if self.function is None:
            raise NotImplementedError( "Cannot call `on_run` on a BasicCommand «{}» with `function = None`. `on_run` should be overridden for such commands.".format( self ) )
        
        return self.function( *args, **kwargs )
