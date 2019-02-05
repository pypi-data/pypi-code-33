from typing import Generic, TypeVar, List, Optional, Sequence, Tuple, Union

from ._test_base import test, testing
from mhelper import mannotation as X


T = TypeVar( "T" )
U = TypeVar( "U" )


class MyMannotation( X.MAnnotation ):
    pass


class MyGeneric( Generic[T, U] ):
    pass


class MyGenericInst( MyGeneric[int, bool] ):
    pass


class MyOtherGeneric( Generic[T, U] ):
    pass


class MyOtherGenericInst( MyOtherGeneric[int, bool] ):
    pass


class MyAlpha:
    pass


class MyBeta( MyAlpha ):
    pass


class MyGamma( MyBeta ):
    pass


class MyDelta( MyGamma ):
    pass


class MyEpsilon( MyDelta ):
    pass


@test
def is_derived_from():
    x = MyMannotation( int, "hello" )
    y = x["world"]
    z = MyMannotation( int, "spam" )
    testing( y.is_derived_from( x ) ).EQUALS( True )
    testing( z.is_derived_from( x ) ).EQUALS( False )


@test
def predefined():
    def spam( a: X.isOptionList = None,
              b: X.isFilename = None,
              c: X.isDirname = None,
              d: X.isOptional = None,
              e: X.isUnion = None,
              f: X.isReadonly = None,
              g: X.isPassword = None ):
        _ = a, b, c, d, e, f, g
    
    
    spam()


@test
def generic_arg():
    testing( X.AnnotationInspector( MyGenericInst ).generic_arg ).EQUALS( int )


@test
def generic_args():
    x = X.AnnotationInspector( MyGenericInst )
    testing( x.generic_args ).EQUALS( (int, bool) )


@test
def generic_list_type():
    testing( X.AnnotationInspector( List[int] ).generic_list_type ).EQUALS( int )


@test
def get_direct_subclass():
    x = X.AnnotationInspector( MyBeta )
    testing( x.get_direct_subclass( MyAlpha ) ).EQUALS( MyBeta )


@test
def get_direct_superclass():
    x = X.AnnotationInspector( MyBeta )
    testing( x.get_direct_superclass( MyGamma ) ).EQUALS( MyBeta )


@test
def get_indirect_subclass():
    testing( X.AnnotationInspector( MyEpsilon ).get_indirect_subclass( MyBeta ) ).EQUALS( MyEpsilon )


@test
def get_indirect_superclass():
    testing( X.AnnotationInspector( MyEpsilon ).get_indirect_subclass( MyGamma ) ).EQUALS( MyEpsilon )


@test
def get_type_name():
    testing( X.AnnotationInspector.get_type_name( MyEpsilon ) ).EQUALS( "MyEpsilon" )


@test
def is_direct_subclass_of():
    x = X.AnnotationInspector( MyEpsilon )
    testing( x.is_direct_subclass_of( MyBeta ) ).EQUALS( True )


@test
def is_direct_subclass_of_or_optional():
    x = X.AnnotationInspector( MyEpsilon )
    y = X.AnnotationInspector( Optional[MyEpsilon] )
    z = X.AnnotationInspector( X.isOptional[MyEpsilon] )
    testing( x.is_direct_subclass_of_or_optional( MyBeta ) ).EQUALS( True )
    testing( y.is_direct_subclass_of_or_optional( MyBeta ) ).EQUALS( True )
    testing( z.is_direct_subclass_of_or_optional( MyBeta ) ).EQUALS( True )


@test
def is_direct_superclass_of():
    testing( X.AnnotationInspector( MyGamma ).is_direct_superclass_of( MyEpsilon ) ).EQUALS( True )
    testing( X.AnnotationInspector( Optional[MyGamma] ).is_direct_superclass_of( MyEpsilon ) ).EQUALS( False )
    testing( X.AnnotationInspector( X.isOptional[MyGamma] ).is_direct_superclass_of( MyEpsilon ) ).EQUALS( False )


@test
def is_generic():
    testing( X.AnnotationInspector( MyGeneric ).is_generic ).EQUALS( True )
    testing( X.AnnotationInspector( MyGenericInst ).is_generic ).EQUALS( True )
    testing( X.AnnotationInspector( MyAlpha ).is_generic ).EQUALS( False )


@test
def is_generic_list():
    testing( X.AnnotationInspector( MyGeneric ).is_generic_list ).EQUALS( False )
    testing( X.AnnotationInspector( list ).is_generic_list ).EQUALS( False )
    testing( X.AnnotationInspector( tuple ).is_generic_list ).EQUALS( False )
    testing( X.AnnotationInspector( List[str] ).is_generic_list ).EQUALS( True )
    testing( X.AnnotationInspector( Sequence[str] ).is_generic_list ).EQUALS( False )
    testing( X.AnnotationInspector( Tuple[str, ...] ).is_generic_list ).EQUALS( False )


@test
def is_generic_sequence():
    testing( X.AnnotationInspector( MyGeneric ).is_generic_sequence ).EQUALS( False )
    testing( X.AnnotationInspector( list ).is_generic_sequence ).EQUALS( False )
    testing( X.AnnotationInspector( tuple ).is_generic_sequence ).EQUALS( False )
    testing( X.AnnotationInspector( List[str] ).is_generic_sequence ).EQUALS( False )
    testing( X.AnnotationInspector( Sequence[str] ).is_generic_sequence ).EQUALS( True )
    testing( X.AnnotationInspector( Tuple[str, ...] ).is_generic_sequence ).EQUALS( False )


@test
def is_generic_u_of_t():
    testing( X.AnnotationInspector( MyGenericInst ).is_generic_u_of_t( MyGeneric ) ).EQUALS( True )
    testing( X.AnnotationInspector( MyGenericInst ).is_generic_u_of_t( MyOtherGeneric ) ).EQUALS( False )


@test
def is_indirect_subclass_of():
    testing( X.AnnotationInspector( MyDelta ).is_indirect_subclass_of( MyAlpha ) ).EQUALS( True )
    testing( X.AnnotationInspector( Optional[MyDelta] ).is_indirect_subclass_of( MyAlpha ) ).EQUALS( True )
    testing( X.AnnotationInspector( Union[str, MyDelta] ).is_indirect_subclass_of( MyAlpha ) ).EQUALS( True )
    testing( X.AnnotationInspector( MyDelta ).is_indirect_subclass_of( MyEpsilon ) ).EQUALS( False )
    testing( X.AnnotationInspector( Optional[MyDelta] ).is_indirect_subclass_of( MyEpsilon ) ).EQUALS( False )
    testing( X.AnnotationInspector( Union[str, MyDelta] ).is_indirect_subclass_of( MyEpsilon ) ).EQUALS( False )
    testing( X.AnnotationInspector( Union[str, MyDelta] ).is_indirect_subclass_of( int ) ).EQUALS( False )


@test
def is_indirectly_superclass_of():
    testing( X.AnnotationInspector( MyDelta ).is_indirectly_superclass_of( MyAlpha ) ).EQUALS( False )
    testing( X.AnnotationInspector( Optional[MyDelta] ).is_indirectly_superclass_of( MyAlpha ) ).EQUALS( False )
    testing( X.AnnotationInspector( Union[str, MyDelta] ).is_indirectly_superclass_of( MyAlpha ) ).EQUALS( False )
    testing( X.AnnotationInspector( MyDelta ).is_indirectly_superclass_of( MyEpsilon ) ).EQUALS( True )
    testing( X.AnnotationInspector( Optional[MyDelta] ).is_indirectly_superclass_of( MyEpsilon ) ).EQUALS( True )
    testing( X.AnnotationInspector( Union[str, MyDelta] ).is_indirectly_superclass_of( MyEpsilon ) ).EQUALS( True )
    testing( X.AnnotationInspector( Union[str, MyDelta] ).is_indirectly_superclass_of( int ) ).EQUALS( False )


@test
def is_mannotation():
    testing( X.AnnotationInspector( MyDelta ).is_mannotation ).EQUALS( False )
    testing( X.AnnotationInspector( str ).is_mannotation ).EQUALS( False )
    testing( X.AnnotationInspector( X.isFilename ).is_mannotation ).EQUALS( True )
    testing( X.AnnotationInspector( X.isFilename[".csv", "R"] ).is_mannotation ).EQUALS( True )
    testing( X.AnnotationInspector( X.MAnnotation( "foo" ) ).is_mannotation ).EQUALS( True )


@test
def is_mannotation_of():
    testing( X.AnnotationInspector( MyDelta ).is_mannotation_of( X.isFilename ) ).EQUALS( False )
    testing( X.AnnotationInspector( str ).is_mannotation_of( X.isFilename ) ).EQUALS( False )
    testing( X.AnnotationInspector( X.isFilename ).is_mannotation_of( X.isFilename ) ).EQUALS( True )
    testing( X.AnnotationInspector( X.isFilename[".csv", "R"] ).is_mannotation_of( X.isFilename ) ).EQUALS( True )
    testing( X.AnnotationInspector( X.MAnnotation( "foo" ) ).is_mannotation_of( X.isFilename ) ).EQUALS( False )


@test
def is_multi_optional():
    testing( X.AnnotationInspector( Optional[Union[str, int]] ).is_multi_optional ).EQUALS( True )
    testing( X.AnnotationInspector( Union[str, int, None] ).is_multi_optional ).EQUALS( True )
    testing( X.AnnotationInspector( Union[str, int] ).is_multi_optional ).EQUALS( False )
    testing( X.AnnotationInspector( None ).is_multi_optional ).EQUALS( False )
    testing( X.AnnotationInspector( str ).is_multi_optional ).EQUALS( False )


@test
def is_optional():
    testing( X.AnnotationInspector( Optional[str] ).is_optional ).EQUALS( True )
    testing( X.AnnotationInspector( Optional[Union[str, int]] ).is_optional ).EQUALS( False )
    testing( X.AnnotationInspector( Union[str, int, None] ).is_optional ).EQUALS( False )
    testing( X.AnnotationInspector( Union[str, int] ).is_optional ).EQUALS( False )
    testing( X.AnnotationInspector( None ).is_optional ).EQUALS( False )
    testing( X.AnnotationInspector( str ).is_optional ).EQUALS( False )


@test
def is_type():
    testing( X.AnnotationInspector( Optional[Union[str, int]] ).is_type ).EQUALS( False )
    testing( X.AnnotationInspector( Union[str, int, None] ).is_type ).EQUALS( False )
    testing( X.AnnotationInspector( Union[str, int] ).is_type ).EQUALS( False )
    testing( X.AnnotationInspector( List[str] ).is_type ).EQUALS( False )
    testing( X.AnnotationInspector( None ).is_type ).EQUALS( False )
    testing( X.AnnotationInspector( X.isFilename ).is_type ).EQUALS( False )
    testing( X.AnnotationInspector( str ).is_type ).EQUALS( True )


@test
def is_union():
    testing( X.AnnotationInspector( Optional[str] ).is_union ).TRUE()
    testing( X.AnnotationInspector( Optional[Union[str, int]] ).is_union ).TRUE()
    testing( X.AnnotationInspector( Union[str, int, None] ).is_union ).TRUE()
    testing( X.AnnotationInspector( Union[str, int] ).is_union ).TRUE()
    testing( X.AnnotationInspector( X.isUnion[str, int, None] ).is_union ).TRUE()
    testing( X.AnnotationInspector( X.isUnion[str, int] ).is_union ).TRUE()
    testing( X.AnnotationInspector( X.isOptional[str] ).is_union ).TRUE()
    testing( X.AnnotationInspector( None ).is_union ).FALSE()
    testing( X.AnnotationInspector( str ).is_union ).FALSE()


@test
def is_viable_instance():
    testing( X.AnnotationInspector( MyDelta ).is_viable_instance( MyAlpha() ) ).EQUALS( False )
    testing( X.AnnotationInspector( Optional[MyDelta] ).is_viable_instance( MyAlpha() ) ).EQUALS( False )
    testing( X.AnnotationInspector( Union[str, MyDelta] ).is_viable_instance( MyAlpha() ) ).EQUALS( False )
    testing( X.AnnotationInspector( MyDelta ).is_viable_instance( MyEpsilon() ) ).EQUALS( True )
    testing( X.AnnotationInspector( Optional[MyDelta] ).is_viable_instance( MyEpsilon() ) ).EQUALS( True )
    testing( X.AnnotationInspector( Union[str, MyDelta] ).is_viable_instance( MyEpsilon() ) ).EQUALS( True )
    testing( X.AnnotationInspector( Union[str, MyDelta] ).is_viable_instance( 5 ) ).EQUALS( False )


@test
def mannotation():
    testing( X.AnnotationInspector( X.isFilename["foo", "R"] ).mannotation ).ISINSTANCE( X.MAnnotation )


@test
def mannotation_arg():
    testing( X.AnnotationInspector( X.isFilename["foo", "R"] ).mannotation_arg ).EQUALS( str )


@test
def name():
    testing( X.AnnotationInspector( int ).name ).EQUALS( "int" )


@test
def optional_types():
    testing( X.AnnotationInspector( Optional[str] ).optional_types ).EQUALS( [str] )
    testing( X.AnnotationInspector( Optional[Union[str, int]] ).optional_types ).EQUALS( [str, int] )
    testing( X.AnnotationInspector( Union[str, int, None] ).optional_types ).EQUALS( [str, int] )
    testing( lambda: X.AnnotationInspector( Union[str, int] ).optional_types ).ERRORS()
    testing( X.AnnotationInspector( X.isUnion[str, int, None] ).optional_types ).EQUALS( [str, int] )
    testing( lambda: X.AnnotationInspector( X.isUnion[str, int] ).optional_types ).ERRORS()
    testing( lambda: X.AnnotationInspector( None ).optional_types ).ERRORS()
    testing( lambda: X.AnnotationInspector( str ).optional_types ).ERRORS()


@test
def optional_value():
    testing( X.AnnotationInspector( Optional[str] ).optional_value ).EQUALS( str )
    testing( X.AnnotationInspector( X.isOptional[str] ).optional_value ).EQUALS( str )
    testing( lambda: X.AnnotationInspector( Optional[Union[str, int]] ).optional_value ).ERRORS()
    testing( lambda: X.AnnotationInspector( Union[str, int, None] ).optional_value ).ERRORS()
    testing( lambda: X.AnnotationInspector( Union[str, int] ).optional_value ).ERRORS()
    testing( lambda: X.AnnotationInspector( X.isUnion[str, int, None] ).optional_value ).ERRORS()
    testing( lambda: X.AnnotationInspector( X.isUnion[str, int] ).optional_value ).ERRORS()
    testing( lambda: X.AnnotationInspector( None ).optional_value ).ERRORS()
    testing( lambda: X.AnnotationInspector( str ).optional_value ).ERRORS()


@test
def safe_type():
    testing( X.AnnotationInspector( str ).safe_type ).EQUALS( str )
    testing( X.AnnotationInspector( Optional[str] ).safe_type ).EQUALS( None )
    testing( X.AnnotationInspector( 5 ).safe_type ).EQUALS( None )


@test
def union_args():
    testing( X.AnnotationInspector( Optional[str] ).union_args ).SEQUALS( [str, type( None )] )
    testing( X.AnnotationInspector( Optional[Union[str, int]] ).union_args ).SEQUALS( [str, int, type( None )] )
    testing( X.AnnotationInspector( Union[str, int, None] ).union_args ).SEQUALS( [str, int, type( None )] )
    testing( X.AnnotationInspector( Union[str, int] ).union_args ).SEQUALS( [str, int] )
    testing( X.AnnotationInspector( X.isUnion[str, int, None] ).union_args ).SEQUALS( [str, int, None] )
    testing( X.AnnotationInspector( X.isUnion[str, int] ).union_args ).SEQUALS( [str, int] )
    testing( lambda: X.AnnotationInspector( None ).union_args ).ERRORS()
    testing( lambda: X.AnnotationInspector( str ).union_args ).ERRORS()


@test
def value_or_optional_value():
    testing( X.AnnotationInspector( Optional[str] ).value_or_optional_value ).EQUALS( str )
    testing( X.AnnotationInspector( str ).value_or_optional_value ).EQUALS( str )
