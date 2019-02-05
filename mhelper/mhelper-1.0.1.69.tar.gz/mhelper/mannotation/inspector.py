from collections import abc
from typing import Tuple, cast, List, Optional, Union, Callable, Generic

from mhelper.mannotation.classes import MAnnotation
from mhelper.mannotation.predefined import isUnion, isOptional


GAlias = type( List )


class AnnotationInspector:
    """
    Class to inspect PEP-484 generics including `MAnnotation` annotations.
    """
    
    
    def __init__( self, annotation: object ):
        """
        CONSTRUCTOR
        :param annotation: `type` to inspect 
        """
        if isinstance( annotation, AnnotationInspector ):
            raise TypeError( "Encompassing an `AnnotationInspector` within an `AnnotationInspector` is probably an error." )
        
        self.value = annotation
    
    
    def _get_generic_info( self ):
        """
        This is the core workhorse of this class.
        
        It should return a tuple of the type and its args.

        =================== =========================== ========================
        Input               Output I                    Output II
        =================== =========================== ========================
        typing.Union        typing.Union                Union arguments
        typing.List         list                        List arguments
        typing.Tuple        tuple                       Tuple arguments
        typing.Sequence     collections.abc.Sequence    Sequence arguments
        MAnnotation         MAnnotation                 MAnnotation arguments
        Generic-base        Generic-base                Generic arguments
        (anything else)     None                        None
        =================== =========================== ========================
        """
        if isinstance( self.value, GAlias ):
            # Union, List, etc.
            return self.value.__origin__, self.value.__args__
        elif isinstance( self.value, type ) and issubclass( self.value, Generic ):
            # Custom generics
            try:
                # Python 3.7 Custom Generics
                ob = getattr( self.value, "__orig_bases__" )[0]
            except:
                # Python 3.6 All + Python 3.7 "GenericAlias" 
                ob = self.value
            
            return ob.__origin__, ob.__args__
        elif isinstance( self.value, MAnnotation ):
            return MAnnotation, self.value.parameters
        else:
            return None, None
    
    
    def is_generic_u( self, u: type ) -> bool:
        """
        If this some sort of generic derived from `U`.
        
        Generics include `GenericAlias`, `Generic` and `MAnnotation`.
        
        For Generic, `u` should be the generic base class. 
        For MAnnotation, `u` should be the base annotation.
        For GenericAlias, `u` should be the bound type (list, tuple, Union, abc.Sequence).
        """
        c, a = self._get_generic_info()
        
        if c is MAnnotation and isinstance( u, MAnnotation ):
            return self.value.is_derived_from( u )
        else:
            return bool( u == c )
    
    
    @classmethod
    def get_type_name( cls, type_: type ) -> str:
        return str( cls( type_ ) )
    
    
    def __str__( self ) -> str:
        """
        Returns the underlying type string
        """
        if isinstance( self.value, type ):
            result = self.value.__name__
        elif isinstance( self.value, MAnnotation ):
            result = str( self.value )
        elif hasattr( self.value, "__forward_arg__" ):  # from typing._ForwardRef
            result = getattr( self.value, "__forward_arg__" )
        else:
            result = "*" + str( self.value )
        
        if result.startswith( "typing." ):
            result = result[7:]
        
        # if self.is_generic:
        #     result += "[" + ", ".join( str( AnnotationInspector( x ) ) for x in self.generic_args ) + "]"
        
        return result
    
    
    @property
    def is_generic( self ):
        """
        Returns if this class is a generic (inherits `GenericMeta`).
        """
        return (isinstance( self.value, GAlias )
                or (isinstance( self.value, type ) and issubclass( self.value, Generic )))
    
    
    @property
    def generic_arg( self ) -> object:
        return self.generic_args[0]
    
    
    @property
    def is_mannotation( self ):
        """
        Is this an instance of `MAnnotation`?
        """
        return isinstance( self.value, MAnnotation )
    
    
    def is_mannotation_of( self, parent: MAnnotation ):
        """
        Is this an instance of `MAnnotation`, specifically a `specific_type` derivative?
        """
        if not self.is_mannotation:
            return False
        
        assert isinstance( self.value, MAnnotation )
        
        return self.value.is_derived_from( parent )
    
    
    @property
    def mannotation( self ) -> MAnnotation:
        """
        Returns the MAnnotation object, if this is an MAnnotation, otherwise raises an error.
        
        :except TypeError: Not an MAnnotation.
        """
        if not self.is_mannotation:
            raise TypeError( "«{}» is not an MAnnotation[T].".format( self ) )
        
        return cast( MAnnotation, self.value )
    
    
    @property
    def mannotation_arg( self ):
        """
        If this is an instance of `MAnnotation`, return the underlying argument 0 (typically the
        type), otherwise, raise an error.
        """
        if not self.is_mannotation:
            raise TypeError( "«{}» is not an MAnnotation[T].".format( self ) )
        
        assert isinstance( self.value, MAnnotation )
        
        if len( self.value.parameters ) >= 2:
            return self.value.parameters[1]
        else:
            return None
    
    
    @property
    def is_generic_list( self ) -> bool:
        """
        Is this a `List[T]`?
        
        (note: this does not include `list` or `List` with no `T`)
        """
        c, a = self._get_generic_info()
        return bool( c == list and a )
    
    
    def is_generic_u_of_t( self, u: type ):
        """
        Is this a generic `U[T]`?
        
        :param u:  `U`, can be anything.
        """
        return bool( self.is_generic_u( u ) and self.generic_args )
    
    
    @property
    def generic_args( self ) -> Tuple[object, ...]:
        """
        If this class is a generic, returns the arguments.
        """
        c, a = self._get_generic_info()
        
        if c is None:
            raise ValueError( "Cannot get `generic_args` because this annotation, «{}» is not a generic.".format( self ) )
        
        return a
    
    
    @property
    def is_generic_sequence( self ) -> bool:
        """
        Is this a `Sequence[T]`?
        
        This does *not* include `List[T]`, `Tuple[T, ...]`, etc.
        """
        c, a = self._get_generic_info()
        return bool( c == abc.Sequence and a )
    
    
    @property
    def generic_list_type( self ) -> type:
        """
        Gets the T in List[T]. Otherwise raises `TypeError`.
        """
        if not self.is_generic_list:
            raise TypeError( "«{}» is not a List[T].".format( self ) )
        
        # noinspection PyUnresolvedReferences
        return self.value.__args__[0]
    
    
    @property
    def is_union( self ) -> bool:
        """
        Determines if this is union-like.
        
        `Union[str, int]`   --> True
        `Optional[str]`     --> True
        `isUnion[str, int]` --> True
        `isOptional[str]`   --> True
        `str`               --> False
        """
        return self.is_typing_union_t or self.is_man_union_t or self.is_man_optional_t
    
    
    @property
    def is_typing_union_t( self ):
        """
        Is Union[T]? 
        """
        return self.is_generic_u_of_t( Union )
    
    
    @property
    def is_man_union_t( self ):
        """
        Is isUnion[T]?
        """
        return self.is_generic_u_of_t( isUnion )
    
    
    @property
    def is_man_optional_t( self ):
        """
        Is isOptional[T]?
        """
        return self.is_generic_u_of_t( isOptional )
    
    
    def is_direct_subclass_of( self, super_class: type ) -> bool:
        """
        As `get_direct_subclass` but returns `True`/`False` instead of `type`/`None`.
        """
        # If BASE and/or DERIVED is not a type then we count only direct equality
        if self.value is super_class:
            return True
        
        if not self.is_type:
            return False
        
        super_inspector = AnnotationInspector( super_class )
        
        if not super_inspector.is_type:
            return False
        
        if super_inspector.is_generic_list:
            super_inspector = AnnotationInspector( list )
        
        if super_inspector.is_union:
            return any( self.is_direct_subclass_of( x ) for x in super_inspector.union_args )
        else:
            try:
                return issubclass( cast( type, self.value ), super_inspector.value )
            except TypeError as ex:
                raise TypeError( "Cannot determine if «{}» is derived from «{}» because `issubclass({}, {})` returned an error.".format( self, super_class, self, super_class ) ) from ex
    
    
    def is_direct_superclass_of( self, sub_class: type ) -> bool:
        """
        As `get_direct_superclass` but returns `True`/`False` instead of `type`/`None`.
        """
        if not self.is_type:
            return False
        
        if self.is_generic_list:
            # Special case for List[T]
            return issubclass( sub_class, list )
        
        try:
            return issubclass( sub_class, cast( type, self.value ) )
        except TypeError as ex:
            raise TypeError( "Cannot determine if «{}» is a base class of «{}» because `issubclass({}, {})` returned an error.".format( self, sub_class, sub_class, self ) ) from ex
    
    
    def is_direct_subclass_of_or_optional( self, super_class: type ):
        """
        As `is_direct_subclass_of` but unwraps any optional annotation first.
        """
        return AnnotationInspector( self.value_or_optional_value ).is_direct_subclass_of( super_class )
    
    
    def get_direct_subclass( self, super_class: type ) -> Optional[type]:
        """
        Checks if this annotation is derived from a `super_class`.
        
        :return: The type of the annotation is returned if this is the case,
                 otherwise `None`.
        """
        if self.is_direct_subclass_of( super_class ):
            return cast( type, self.value )
    
    
    def get_direct_superclass( self, lower_class: type ) -> Optional[type]:
        """
        The counterpart of `get_direct_subclass`, checking if this
        `lower_class` is derived from this annotation..
        """
        if self.is_direct_superclass_of( lower_class ):
            return cast( type, self.value )
    
    
    def is_indirect_subclass_of( self, super_class: type ) -> bool:
        """
        As `get_indirect_subclass` but returns `True`/`False` instead of `type`/`None`. 
        """
        return self.get_indirect_subclass( super_class ) is not None
    
    
    def is_indirectly_superclass_of( self, sub_class: type ) -> bool:
        """
        As `get_indirect_superclass` but returns `True`/`False` instead of `type`/`None`.
        """
        return self.get_indirect_superclass( sub_class ) is not None
    
    
    def get_indirect_superclass( self, sub_class: type ) -> Optional[type]:
        """
        As `get_direct_superclass`, but also checks annotations within the
        annotation (such as `Union`, `Optional`, or `MAnnotation`s with a
        concrete-type such as `isFileName` (`str`)).
        """
        return self.__get_indirectly( sub_class, AnnotationInspector.is_direct_superclass_of )
    
    
    def get_indirect_subclass( self, super_class: type ) -> Optional[type]:
        """
        As `get_direct_subclass`, but also checks annotations within the the
        annotation (such as `Union`, `Optional`, or `MAnnotation`s with
        a concrete-type such as `isFileName` (`str`)).
        """
        return self.__get_indirectly( super_class, AnnotationInspector.is_direct_subclass_of )
    
    
    def __get_indirectly( self, query: type, predicate: "Callable[[AnnotationInspector, type],bool]" ) -> Optional[object]:
        """
        Checks inside all `Unions` and `MAnnotations` until the predicate matches, returning the
        type (`self.value`) when it does.
        """
        if predicate( self, query ):
            return self.value
        
        if self.is_union:
            for arg in self.union_args:
                arg_type = AnnotationInspector( arg ).__get_indirectly( query, predicate )
                
                if arg_type is not None:
                    return arg_type
        
        if self.is_mannotation:
            annotation_type = AnnotationInspector( self.mannotation_arg ).__get_indirectly( query, predicate )
            
            if annotation_type is not None:
                return annotation_type
        
        return None
    
    
    @property
    def union_args( self ) -> List[type]:
        """
        If this is a "union"-type annotation, returns the option list.
        If this is not a "union"-type, return an error.
        
        * `Optional[T]`         --> `[T, NoneType]`
        * `isOptional[T]`       --> *Error*
        * `Union[T, None]`      --> `[T, NoneType]`
        * `Union[T, U, None]`   --> `[T, U, NoneType]`
        * `Union[T]`            --> `[T]`
        * `Union[T, U]`         --> `[T, U]`
        * `isUnion[T, None]`    --> `[T, NoneType]`
        * `isUnion[T, U, None]` --> `[T, U, NoneType]`
        * `isUnion[T]`          --> `[T]`
        * `isUnion[T, U]`       --> `[T, U]`
        * `T`                   --> *Error*
        """
        if not self.is_union:
            raise TypeError( "«{}» is not a Union[T].".format( self ) )
        
        if self.is_mannotation_of( isUnion ):
            return self.value.parameters[1:]  # "1:" = skip name
        elif self.is_mannotation_of( isOptional ):
            return [self.mannotation_arg]
        else:
            return self.value.__args__
    
    
    @property
    def is_optional( self ) -> bool:
        """
        Returns if this is an "optional"-type annotation with a single option.
        
        * `Optional[T]`         --> `True`
        * `isOptional[T]`       --> `True`
        * `Union[T, None]`      --> `True`
        * `Union[T, U, None]`   --> `False`
        * `Union[T]`            --> `False`
        * `Union[T, U]`         --> `False`
        * `T`                   --> `False`
        """
        if self.is_mannotation_of( isOptional ):
            return True
        
        if not self.is_union:
            return False
        
        if len( self.union_args ) == 2 and (type( None ) in self.union_args or None in self.union_args):
            return True
        
        return False
    
    
    @property
    def is_multi_optional( self ) -> bool:
        """
        Returns if this is an "optional"-type annotation.
        
        * `Optional[T]`         --> `True`
        * `isOptional[T]`       --> `True`
        * `Union[T, None]`      --> `True`
        * `Union[T, U, None]`   --> `True`
        * `Union[T]`            --> `False`
        * `Union[T, U]`         --> `False`
        * `T`                   --> `False`
        """
        if self.is_mannotation_of( isOptional ):
            return True
        
        if not self.is_union:
            return False
        
        # Python 3.6 + MAnnotation uses None, Python 3.7 uses NoneType
        if None in self.union_args or type( None ) in self.union_args:
            return True
        
        return False
    
    
    @property
    def optional_types( self ) -> List[type]:
        """
        If this annotation is an optional, obtain the option list, otherwise,
        raise a `TypeError`.
        
        * `Optional[T]`         --> `[T]`
        * `isOptional[T]`       --> `[T]`
        * `Union[T, None]`      --> `[T]`
        * `Union[T, U, None]`   --> `[T, U]`
        """
        if self.is_mannotation_of( isOptional ):
            return [self.mannotation_arg]
        
        if not self.is_union:
            raise TypeError( "«{}» is not a Union[T].".format( self ) )
        
        union_params = list( self.union_args )
        
        if type( None ) in union_params:
            union_params.remove( type( None ) )
        elif None in union_params:
            union_params.remove( None )
        else:
            raise TypeError( "«{}» is not a Union[...] with `None` in `...`.".format( self ) )
        
        return union_params
    
    
    @property
    def optional_value( self ) -> Optional[object]:
        """
        If this annotation is an optional specifying a single type, obtain that
        type, otherwise, just raise a `TypeError`.
        
        * `Optional[T]`     --> `T`
        * `isOptional[T]`   --> `T`
        * `Union[T, None]`  --> `T`
        * `X`               --> `X`
            * Where X is anything else, including `Union[T, U, None]`.
        """
        t = self.optional_types
        
        if len( t ) == 1:
            return t[0]
        else:
            raise TypeError( "«{}» is not a Union[T, None] (i.e. an Optional[T]).".format( self ) )
    
    
    @property
    def value_or_optional_value( self ) -> Optional[object]:
        """
        If this annotation is an optional specifying a single type, obtain that
        type, otherwise, just obtain the annotation verbatim.
        
        * `Optional[T]`     --> `T`
        * `isOptional[T]`   --> `T`
        * `Union[T, None]`  --> `T`
        * `X`               --> `X`
            * Where X is anything else, including `Union[T, U, None]`.
        """
        if self.is_optional:
            return self.optional_value
        else:
            return self.value
    
    
    @property
    def safe_type( self ) -> Optional[type]:
        """
        If this is a `T`, returns `T`, else returns `None`.
        """
        if self.is_type:
            assert isinstance( self.value, type )
            return self.value
        else:
            return None
    
    
    @property
    def is_type( self ):
        """
        Returns if my `type` is an actual `type`, not an annotation object like `Union`.
        """
        return isinstance( self.value, type )
    
    
    @property
    def name( self ):
        """
        Returns the type name
        """
        if not self.is_type:
            raise TypeError( "«{}» is not a <type>.".format( self ) )
        
        return self.value.__name__
    
    
    def is_viable_instance( self, value ):
        """
        Returns `is_viable_subclass` on the value's type.
        """
        if value is None and self.is_optional:
            return True
        
        return self.is_indirectly_superclass_of( type( value ) )
