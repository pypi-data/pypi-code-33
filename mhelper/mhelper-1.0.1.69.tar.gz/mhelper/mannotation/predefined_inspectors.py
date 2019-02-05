import warnings
from collections.__init__ import OrderedDict
from typing import Union, Callable, Optional, Iterator, Iterable, Dict, Tuple, List

from mhelper.mannotation.inspector import AnnotationInspector
from mhelper.special_types import NOT_PROVIDED
from mhelper.documentation_helper import Documentation
from mhelper import string_helper, exception_helper


class ICode:
    """
    Interface for code object (for Intellisense only)
    """
    
    
    def __init__( self ):
        self.__class__ = None
        self.__delattr__ = None
        self.__dir__ = None
        self.__doc__ = None
        self.__eq__ = None
        self.__format__ = None
        self.__ge__ = None
        self.__getattribute__ = None
        self.__gt__ = None
        self.__hash__ = None
        self.__init__ = None
        self.__le__ = None
        self.__lt__ = None
        self.__ne__ = None
        self.__new__ = None
        self.__reduce__ = None
        self.__reduce_ex__ = None
        self.__repr__ = None
        self.__setattr__ = None
        self.__sizeof__ = None
        self.__str__ = None
        self.__subclasshook__ = None
        self.co_argcount = None
        self.co_cellvars = None
        self.co_code = None
        self.co_consts = None
        self.co_filename = None
        self.co_firstlineno = None
        self.co_flags = None
        self.co_freevars = None
        self.co_kwonlyargcount = None
        self.co_lnotab = None
        self.co_name = None
        self.co_names = None
        self.co_nlocals = None
        self.co_stacksize = None
        self.co_varnames = None
        raise NotImplementedError( "type hinting only - not intended for construction" )


class IFunctionBase:
    """
    Interface for function object (for Intellisense only)
    """
    
    
    def __init__( self ):
        self.__annotations__ = None
        self.__call__ = None
        self.__class__ = None
        self.__closure__ = None
        self.__code__ = ICode()
        self.__defaults__ = None
        self.__delattr__ = None
        self.__dict__ = None
        self.__dir__ = None
        self.__doc__ = None
        self.__eq__ = None
        self.__format__ = None
        self.__ge__ = None
        self.__get__ = None
        self.__getattribute__ = None
        self.__globals__ = None
        self.__gt__ = None
        self.__hash__ = None
        self.__init__ = None
        self.__kwdefaults__ = None
        self.__le__ = None
        self.__lt__ = None
        self.__module__ = None
        self.__name__ = None
        self.__ne__ = None
        self.__new__ = None
        self.__qualname__ = None
        self.__reduce__ = None
        self.__reduce_ex__ = None
        self.__repr__ = None
        self.__setattr__ = None
        self.__sizeof__ = None
        self.__str__ = None
        self.__subclasshook__ = None
        raise NotImplementedError( "type hinting only - not intended for construction" )
    
    
    def __call__( self, *args, **kwargs ):
        raise NotImplementedError( "type hinting only - not intended for calling" )


IFunction = Union[IFunctionBase, Callable]


class ArgInspector:
    """
    Function argument details
    
    Please see the constructor for attribute descriptions.
    """
    
    
    def __init__( self,
                  name: str,
                  annotation: object,
                  default: Optional[object] = NOT_PROVIDED,
                  description: str = "",
                  is_kwonly: bool = True,
                  index: int = -1 ):
        """
        CONSTRUCTOR
        :param name:                Name of the argument 
        :param annotation:          Annotation of the argument.
                                    May be wrapped in an `AnnotationInspector`, or if not, this will be done.
                                    `None` if the argument is not annotated. 
        :param description:         Description of the argument
                                    `""` if the argument does not appear in the doc-string.
        :param default:             Default value of the argument.
                                    `NOT_PROVIDED` if the argument has no default.
        :param is_kwonly:           `True` if this is a kw-only argument, `False` otherwise. 
        :param index:               Index of the argument within the function's definition.
        """
        if not isinstance( annotation, AnnotationInspector ):
            annotation = AnnotationInspector( annotation )
        
        self.name = name
        self.annotation: AnnotationInspector = annotation
        self.description: str = description or ""
        self.default = default
        self.is_kw_only = is_kwonly
        self.index = index
    
    
    def __repr__( self ):
        return "ArgInspector('{}' : {} = {})".format( self.name, self.annotation, repr( self.default ) )
    
    
    @property
    def type( self ):
        warnings.warn( "Deprecated - use annotation", DeprecationWarning )
        return self.annotation
    
    
    def extract( self, *args, **kwargs ):
        if self.index != -1 and self.index < len( args ):
            return args[self.index]
        
        return kwargs.get( self.name, NOT_PROVIDED )


class ArgCollection:
    def __init__( self, contents = None ):
        self.__contents = OrderedDict()
        self.__order = []  # because OrderedDict doesn't support indexing.
        
        if contents:
            for content in contents:
                self.append( content )
    
    
    def append( self, item: ArgInspector ):
        self.__contents[item.name] = item
        self.__order.append( item )
    
    
    def __iter__( self ) -> Iterator[ArgInspector]:
        return iter( self.__contents.values() )
    
    
    def __len__( self ):
        return len( self.__contents )
    
    
    def by_name( self, name ) -> ArgInspector:
        return self.__contents[name]
    
    
    def by_index( self, index ) -> ArgInspector:
        return self.__order[index]
    
    
    def __getitem__( self, item ):
        if isinstance( item, int ):
            return self.by_index( item )
        elif isinstance( item, str ):
            return self.by_name( item )
        else:
            raise exception_helper.SwitchError( "item", item, instance = True )


class FunctionInspector:
    """
    Class for inspecting a function.
    
    :ivar function:     Absolute function object, an `IFunction`
    :ivar name:         Name of the function
    :ivar args:         Arguments, as an `ArgCollection` object, which can retrieve arguments by name or index. 
    :ivar description:  Function doc-string.
    """
    
    
    def __init__( self, fn: IFunction ):
        self.function: IFunction = fn
        self.name: str = fn.__name__
        self.args = ArgCollection()
        
        # arg_names = inspect.getargs(fn).args
        
        arg_names = fn.__code__.co_varnames[:fn.__code__.co_argcount + fn.__code__.co_kwonlyargcount]
        
        arg_types = { }
        
        self.return_type = None
        
        for k, v in fn.__annotations__.items():
            if k != "return":
                arg_types[k] = v
            else:
                self.return_type = v
        
        doc = fn.__doc__  # type:str
        
        docs = Documentation( doc )
        arg_descriptions: Dict[str, str] = docs["param"]
        
        arg_defaults = { }
        has_args = (fn.__code__.co_flags & 0x4) == 0x4
        has_kwargs = (fn.__code__.co_flags & 0x8) == 0x8
        
        if fn.__defaults__:
            num_defaults = len( fn.__defaults__ )
            default_offset = len( arg_names ) - num_defaults
            
            if has_args:
                default_offset -= 1
            
            if has_kwargs:
                default_offset -= 1
            
            for i, v in enumerate( fn.__defaults__ ):
                name = arg_names[default_offset + i]
                arg_defaults[name] = v
        
        for index, arg_name in enumerate( arg_names ):
            arg_desc = arg_descriptions.get( arg_name, None )
            arg_desc = string_helper.fix_indents( arg_desc )
            arg_type = arg_types.get( arg_name, None )
            arg_default = arg_defaults.get( arg_name, NOT_PROVIDED )
            
            if arg_type is None and arg_default is not NOT_PROVIDED and arg_default is not None:
                arg_type = type( arg_default )
            
            self.args.append( ArgInspector( arg_name,
                                            AnnotationInspector( arg_type ),
                                            arg_default,
                                            arg_desc,
                                            index >= fn.__code__.co_argcount,
                                            index ) )
        
        fn_desc = docs[""][""]
        fn_desc = string_helper.fix_indents( fn_desc )
        
        self.description: str = fn_desc
    
    
    def __str__( self ):
        return str( self.function )
    
    
    def call( self, *args, **kwargs ):
        """
        Calls the function.
        """
        # noinspection PyCallingNonCallable
        return self.function( *args, **kwargs )


class ArgsKwargs:
    EMPTY: "ArgsKwargs" = None
    
    
    def __init__( self, *args, **kwargs ) -> None:
        self.args = args
        self.kwargs = kwargs
    
    
    def __bool__( self ):
        return bool( self.args ) or bool( self.kwargs )
    
    
    def __getitem__( self, item ):
        r = self.get( item[0], item[1] )
        
        if isinstance( r, NOT_PROVIDED ):
            raise KeyError( item )
        
        return r
    
    
    def get( self, index, name, default = NOT_PROVIDED ):
        if 0 <= index < len( self.args ):
            return self.args[index]
        
        if name:
            return self.kwargs.get( name, default )
        
        return default
    
    
    def __repr__( self ):
        r = []
        
        for x in self.args:
            r.append( "{}".format( x ) )
        
        for k, x in self.kwargs.items():
            r.append( "{} = {}".format( k, x ) )
        
        return ", ".join( r )


ArgsKwargs.EMPTY = ArgsKwargs()


class _ArgValue:
    def __init__( self, arg: ArgInspector, value: object ):
        self.arg = arg
        self.__value = value
    
    
    @property
    def value( self ) -> object:
        return self.__value
    
    
    @value.setter
    def value( self, value: object ):
        if not self.arg.annotation.is_viable_instance( value ):
            msg = "Trying to set the value «{}» on the argument «{}» but the value is of type «{}» and the argument takes «{}»."
            raise TypeError( msg.format( value, self.arg.name, type( value ), self.arg.annotation ) )
        
        self.__value = value
    
    
    def __repr__( self ):
        return "{}({} = {})".format( type( self ).__name__, self.arg, repr( self.__value ) )


class ArgValueCollection:
    """
    Manages a set of arguments and their values.
    """
    
    
    def __init__( self, args: Iterable[ArgInspector] = (), *, read: ArgsKwargs = None, coerce = None ):
        """
        CONSTRUCTOR
        :param *: 
        :param read:    Values to apply to the arguments
        """
        self.__values: Dict[str, _ArgValue] = OrderedDict()
        
        for arg in args:
            exception_helper.safe_cast( "arg", arg, ArgInspector )
            self.__values[arg.name] = _ArgValue( arg, arg.default )
        
        if read:
            self.from_argskwargs( read, coerce = coerce )
    
    
    def __getstate__( self ):
        raise ValueError( "Pickling `ArgValueCollection` is probably an error. Did you mean to pickle the arguments instead?" )
    
    
    def __repr__( self ):
        return str( self.__values )
    
    
    def append( self, arg: ArgInspector, value: object = NOT_PROVIDED ):
        v = _ArgValue( arg, arg.default )
        self.__values[arg.name] = v
        
        if value is not NOT_PROVIDED:
            v.value = v
    
    
    def tokwargs( self ) -> Dict[str, object]:
        warnings.warn( "Deprecated - does not permit position-only arguments if required in the future. Please use `to_argskwargs` instead.", DeprecationWarning )
        return self.to_argskwargs().kwargs
    
    
    def to_argskwargs( self ) -> ArgsKwargs:
        """
        Converts these arguments to `ArgsKwargs`.
        """
        result = { }
        
        for arg in self.__values.values():
            if arg.value is not NOT_PROVIDED:
                result[arg.arg.name] = arg.value
        
        return ArgsKwargs( **result )
    
    
    def from_argskwargs( self, provided: ArgsKwargs, *, coerce: Callable[[ArgInspector, object], object] = None ):
        if coerce is None:
            coerce = lambda _, x: x
        
        assert isinstance( provided, ArgsKwargs )
        
        if len( provided.args ) > len( self.__values ):
            raise ValueError( "Attempt to specify {} values but this function takes {}.".format( len( provided.args ), len( self.__values ) ) )
        
        for arg, value in zip( self.__values.values(), provided.args ):
            arg.value = coerce( arg.arg, value )
        
        for key, value in provided.kwargs.items():
            try:
                self.__values[key].value = coerce( self.__values[key].arg, value )
            except KeyError as ex:
                raise KeyError( "There is no argument named «{}».".format( key ) ) from ex
    
    
    def __len__( self ):
        return len( self.__values )
    
    
    def __iter__( self ) -> Iterator[ArgInspector]:
        return iter( x.arg for x in self.__values.values() )
    
    
    def items( self ) -> Iterable[Tuple[ArgInspector, object]]:
        for name, value in self.__values.items():
            yield self.get_arg( name ), value.value
    
    
    def __get_argvalue( self, key: Union[ArgInspector, str] ) -> _ArgValue:
        if isinstance( key, ArgInspector ):
            key = key.name
        
        return self.__values[key]
    
    
    def get_value( self, key: Union[ArgInspector, str] ) -> Optional[object]:
        """
        Equivalent to `get_arg`, but returns the value on the `PluginArgValue`.
        """
        return self.__get_argvalue( key ).value
    
    
    def set_value( self, key: Union[ArgInspector, str], value: Optional[object] ) -> None:
        """
        Sets the value of the argument with the specified key.
        See `PluginArgValue.set_value` for details on accepted values.

        :param key:     A `PluginArg`. Unlike `get` a name is not accepted.
        :param value:   The value to apply.
        """
        self.__get_argvalue( key ).value = value
    
    
    def get_arg( self, key: Union[ArgInspector, str] ) -> "ArgInspector":
        """
        Retrieves the `ArgInspector` from the specified argument name.
        
        :param key: Argument name, or an `ArgInspector` to get the name from.
        :except KeyError:  If the argument does not exist
        :except TypeError: If the argument is not a `ArgInspector` or `str`.
        """
        return self.__get_argvalue( key ).arg
    
    
    def get_incomplete( self ) -> List[str]:
        """
        Returns the set of arguments that require a value to be set before run() is called
        """
        return [x.arg.name for x in self.__values.values() if x.value is NOT_PROVIDED]
