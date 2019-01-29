import inspect
import warnings
from typing import Dict, Iterable, Iterator, List, Tuple, cast

from intermake.engine.abstract_command import Command
from intermake.helpers import printing as pr
from mhelper import isOptional, array_helper, SimpleProxy, ArgInspector, Documentation, ArgCollection, string_helper


class SetterCommand( Command ):
    """
    A `Command` possessing an `on_run` method which uses the parameters passed
    in to modify a set of fields on various objects.
    """
    
    
    def __get_targets( self ) -> Iterator[Tuple[str, object]]:
        for item in self.on_get_targets():
            if isinstance( item, tuple ):
                yield item
            else:
                yield str( id( item ) ), item
    
    
    def __get_fields( self ) -> "FieldToArgCollection":
        """
        Given the `key` property, returns the name of the associated parameter, or `None` if the parameter should be hidden.
        The default implementation returns the key verbatim.
        """
        
        result = FieldToArgCollection()
        
        for key, target in self.__get_targets():
            if type( target ) in (dict, list):
                continue
            
            result.read( target, key )
        
        return result
    
    
    def on_get_args( self ) -> ArgCollection:
        """
        FINAL OVERRIDE
        """
        return self.__get_fields().get_arguments()
    
    
    def on_get_targets( self ) -> Iterator[Tuple[str, object]]:
        """
        ABSTRACT
        
        Derived class must provide the target(s) to be modified.
        Yield the name of the target, and the target.
        """
        raise NotImplementedError( "abstract" )
    
    
    def on_set_target( self, name: str, target: object ):
        """
        VIRTUAL
        
        After modification, the derived class may save the target.
        """
        pass
    
    
    def on_run( self, **kwargs ):
        """
        FINAL OVERRIDE
        
        Sets the specified value(s).
        """
        
        #
        # Apply all the specified setting changes
        #
        r = []
        map: FieldToArgCollection = self.__get_fields()
        modified_keys = { }
        
        for arg_name, arg_value in kwargs.items():
            if arg_value is None:
                continue
            
            accessor = map.get_field( arg_name )
            existing = accessor.get_value()
            
            if existing == arg_value:
                continue
            
            accessor.set_value( arg_value )
            
            modified_keys[accessor.target_name] = accessor.target_object
            
            r.append( pr.fmt( "<key>{}</key> = <value>{}</value>", arg_name, arg_value ) )
        
        if modified_keys:
            for data_key, data_target in modified_keys.items():
                self.on_set_target( data_key, data_target )
            
            pr.printx( "\n".join( r ) )
            return
        
        #
        # Nothing changed - print the current values instead
        #
        last = None
        
        for arg in sorted( map.iter_fields(), key = lambda x: x.target_name ):
            t = arg.target_name.partition( "." )[0]
            
            if t != last:
                if last:
                    r.append( "</section>" )
                
                r.append( pr.fmt( "<section name='{}'>", t ) )
                last = t
            
            try:
                text = arg.get_value()
            except AttributeError as ex:
                text = repr( ex )
            
            if array_helper.is_simple_iterable( text ):
                text = "List of {} items: {}".format( len( text ), string_helper.format_array( text, format = repr ) )
            elif isinstance( text, str ):
                text = repr( text )
            else:
                text = str( text )
            
            text = string_helper.max_width( text, 80 )
            
            r.append( pr.fmt( "<key>{}</key> = <value>{}</value>", arg.argument.name, text ) )
        
        r.append( "</section>" )
        
        pr.printx( "\n".join( r ) )


class FieldToArg:
    """
    Maps an argument (passed to a `SetterCommand`) to the field which it is intended to modify.
    """
    
    
    def __init__( self, argument: ArgInspector, field_name: str, target_object: object, target_name: str ):
        """
        CONSTRUCTOR
        
        :param argument:            Argument passed to the command 
        :param field_name:          Name of field to modify 
        :param target_object:       Object on which the field exists 
        :param target_name:         Name of the `target_object` for display purposes. 
        """
        self.argument = argument
        self.field_name = field_name
        self.target_object = target_object
        self.target_name = target_name
    
    
    def get_value( self ):
        return getattr( self.target_object, self.field_name )
    
    
    def set_value( self, value ):
        setattr( self.target_object, self.field_name, value )


class FieldToArgCollection:
    """
    A collection of `FieldToArg` objects.
    """
    
    
    def __init__( self ):
        self.__arguments: List[ArgInspector] = []
        self.__contents: Dict[str, FieldToArg] = { }
    
    
    def get_field( self, arg_name: str ):
        return self.__contents[arg_name]
    
    
    def get_arguments( self ) -> ArgCollection:
        return ArgCollection( self.__arguments )
    
    
    def add_arg( self, arg: ArgInspector ):
        self.__arguments.append( arg )
    
    
    def iter_fields( self ) -> Iterable[FieldToArg]:
        return self.__contents.values()
    
    
    def read( self, target: object, target_name: str = "unnamed" ):
        """
        Extracts arguments from an object's fields.
         
        :param target: 
        :param target_name: 
        :return: Iterator of:
                    N: Tuple of:
                        0: Argument, as an `ArgInspector`
                        1: Python name of the field
        """
        
        if target is None:
            return
        
        documentation_dict = { }
        
        t = type( target )
        
        if t is SimpleProxy:
            t = type( SimpleProxy.get_source( cast( SimpleProxy, target ) ) )
        
        for x in inspect.getmro( t ):
            documentation_dict.update( Documentation( x.__doc__ )["ivar"] )
        
        for field_name, field_value in target.__dict__.items():
            if field_name.startswith( "_" ):
                continue
            
            argument_name = "{}_{}".format( target_name, field_name )
            
            if not argument_name:
                continue
            
            documentation = documentation_dict.get( field_name )
            
            if documentation is None:
                msg = "This field is no longer used or is not documented: {}().{}"
                warnings.warn( msg.format( type( target ).__name__, field_name ), UserWarning )
                documentation = "(This field is not documented or has been removed)"
            
            if type( field_value ) in (str, int, float, bool):
                default = field_value
                annotation = type( field_value )
            else:
                default = None
                annotation = isOptional[type( field_value )]
            
            ai = ArgInspector( argument_name, annotation, default, documentation )
            self.__arguments.append( ai )
            self.__contents[argument_name] = FieldToArg( ai, field_name, target, target_name )
