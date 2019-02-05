import inspect
from typing import Iterable, List, Optional, Union, Callable, cast
from mhelper import array_helper, exception_helper, override, string_helper, reflection_helper, ArgInspector, Documentation, ArgCollection


_DPredicate = Callable[[], bool]
_TPredicate = "Optional[Union[bool, DPredicate]]"


class Command:
    """
    ABSTRACT
    
    Commands visible in the UI that can be run by the user.
    
    The derived class should implement `on_run`.
    
    To run the command as if the user had executed it, use `intermake.acquire().run( command )`.
    This will run the command in the manner set by current host, for instance
    `GuiController` creates a "please wait" window and runs the command asynchronously.
    
    .. note::
    
        Commands should no longer be run synchronously, this is not exposed by `Command`.
        Execute the function instead, e.g. `BasicCommand.function()`.
    
    :ivar names:            MUTABLE.    Names of the command. The first in the list is the `name`, with others
                                        suggesting aliases or alternatives if there is a conflict.
    :ivar visibility_class: READONLY.   The `Visibility` set of the command.
    :ivar folder:           READONLY.   Name of an arbitrary set that can be used to organise commands in the UI.
    """
    
    
    def __init__( self,
                  *,
                  names: Optional[Union[str, List[str]]] = None,
                  documentation: Optional[str] = None,
                  visibility: Optional["Visibility"] = None,
                  highlight: bool = False,
                  folder: Optional[str] = None,
                  args: Iterable[ArgInspector] = None ):
        """
        CONSTRUCTOR
        
        :param names:           Name or names of the command.
                                * `str`: Name
                                * `Sequence`: List of names, with subsequent names acting as aliases.
        :param documentation:   Description of the command.
                                * `None`: `__doc__` is used.
                                * Dynamic documentation may also be specified via `on_get_documentation`.
        :param visibility:      A `Visibility` denoting the command's visibility.
                                * `None`: implies the command is always visible.
        :param highlight:       Whether to highlight the command in lists.
        :param folder:          Optional folder where the command resides.
                                * `None`: uses the name of the calling module.
        :param args:            Arguments accepted by` on_run`.
                                * `None`: assumes no arguments
                                * Dynamic arguments may also be specified via `on_get_args`.
        """
        
        #
        # NAME
        #
        # - Mandatory 
        names = array_helper.as_sequence( names or None, cast = list )
        
        if not names:
            raise ValueError( "An `Command` must have at least one name." )
        
        self.names: List[str] = names
        
        #
        # VISIBILITY
        #
        # - Defaults to `COMMON`
        if visibility is None:
            from intermake.commands import visibilities
            visibility = visibilities.COMMON
        elif not isinstance( visibility, Visibility ):
            raise exception_helper.type_error( "visibility", visibility, Visibility )
        
        self.visibility_class: Visibility = visibility
        
        #
        # DOCUMENTATION
        #
        # - Defaults to class __doc__, unless it falls back to the base
        if documentation is None:
            documentation = self.__doc__
            
            if documentation is None:
                documentation = ""
            elif documentation is Command.__doc__:
                documentation = ""
            else:
                documentation = Documentation( cast( str, documentation ) )
                documentation = documentation[""][""]
        
        exception_helper.assert_instance( "documentation", documentation, str )
        
        self.__documentation = string_helper.fix_indents( documentation )
        
        #
        # FOLDER
        #
        if folder is None:
            frame = inspect.currentframe()
            
            while True:
                frame = frame.f_back
                module = inspect.getmodule( frame )
                folder = module.__name__ if module else "?"
                
                if not folder.startswith( "intermake." ):
                    break
            
            if "." in folder:
                folder = folder.rsplit( ".", 1 )[1]
        
        self.folder: str = folder
        
        #
        # ARGUMENTS
        #
        self.__args = ArgCollection( args )
        
        #
        # HIGHLIGHT
        #
        self.__highlight: bool = highlight
    
    
    @property
    def name( self ) -> str:
        return self.names[0]
    
    
    @property
    def is_visible( self ) -> bool:
        return self.visibility_class.is_visible
    
    
    @property
    def is_highlighted( self ) -> bool:
        return self.__highlight
    
    
    @property
    def args( self ) -> ArgCollection:
        """
        Returns the set of arguments for this command. See `ArgInspector`.
        """
        return self.on_get_args()
    
    
    @property
    def documentation( self ) -> str:
        """
        Documentation of the command.
        """
        return self.on_get_documentation()
    
    
    def args_to_kwargs( self, *args ):
        """
        Given a set of arguments appearing in the same order as the arguments for this executable, produces
        a kwargs dictionary compatible with Command.run(), Command.modify(), Command.copy() etc.
        """
        result = { }
        
        if not args:
            return result
        
        arg_list = list( self.args )
        
        if len( args ) > len( arg_list ):
            raise KeyError( "Cannot convert a positional argument list of length {0} to a key-value argument list of length {1}.".format( len( args ), len( arg_list ) ) )
        
        for i, v in enumerate( args ):
            if v is not None:
                result[arg_list[i].name] = v
        
        return result
    
    
    @override
    def __str__( self ) -> str:
        """
        FINAL OVERRIDE
        
        String representation
        """
        return self.name
    
    
    @override
    def __repr__( self ):
        """
        FINAL OVERRIDE
        """
        return "{}({})".format( type( self ).__name__, repr( self.name ) )
    
    
    def on_get_documentation( self ) -> str:
        """
        VIRTUAL
        
        The base class returns the documentation passed into the constructor.
        Derived classes may override this to provide a dynamic documentation.
        """
        return self.__documentation
    
    
    def on_get_args( self ) -> ArgCollection:
        """
        VIRTUAL
        
        The derived class should return the description of arguments sent to `on_run`.
        The base class returns the set of arguments passed into the constructor, but this can be overridden.
        """
        return self.__args
    
    
    def on_run( self, *args, **kwargs ) -> Optional[object]:
        """
        ABSTRACT
        
        The derived class should perform the actual command.
        
        :return: A command specific value.
                 
                 This is not presented in the UI, values may be:
                 * function-bound-commands to return values meaningful if executed from Python.
                 * the result to be something that the host (GUI or CLI) can understand
        """
        raise NotImplementedError( "Abstract" )


class Visibility:
    """
    Defines whether a set of `Command`s is visible to the user.
    
    :ivar name:             READONLY. Name of the set. 
    :ivar comment:          READONLY. Description of the set.    
    :ivar user_override:    When not `None`, overrides `is_visible`.
    """
    
    
    def __init__( self, *, name: str, is_useful: _TPredicate = None, is_visible: _TPredicate = None, comment = None, parents = None ):
        """
        CONSTRUCTOR
        :param *: 
        :param name:            Name of the class
        :param is_useful:       Whether this set of commands is functional.
                                Non-useful commands are never shown to the user.
        :param is_visible:      Whether this set of commands is visible to the user by default.
        """
        if is_useful is None:
            is_useful = True
        
        if is_visible is None:
            is_visible = is_useful
        
        self.name: str = name
        self.user_override: Optional[bool] = None
        self.comment: str = comment or ""
        
        self.parents = parents
        self.__fn_is_visible_by_default: _DPredicate = reflection_helper.enfunction( is_visible )
        self.__fn_is_functional: _DPredicate = reflection_helper.enfunction( is_useful )
    
    
    @property
    def is_useful( self ):
        """
        Whether this set of commands is functional.
        Non-useful commands are never shown to the user.
        """
        return self.__fn_is_functional()
    
    
    @property
    def is_visible_by_default( self ):
        """
        The default value of `is_visible`, before the user changed it.
        """
        return self.__fn_is_visible_by_default()
    
    
    @property
    def is_visible( self ):
        """
        Whether this set of commands is visible to the user.
        """
        if self.user_override is True:
            return True
        elif self.user_override is False:
            return False
        
        return self.is_visible_by_default
    
    
    def __and__( self, other ):
        """
        Combines two visibility classes together using `&`.
        """
        return Visibility( name = self.name + " & " + other.name,
                           is_useful = False,  # The result is not considered "useful" so won't show up in lists, but remains dependent on the parents.
                           is_visible = lambda: self.is_visible and other.is_visible,
                           parents = (self, other) )
    
    
    def __str__( self ) -> str:
        return "{} is {}".format( self.name, "visible" if self.user_override else "hidden" )
