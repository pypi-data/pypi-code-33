from unittest import TestCase
from chibi.atlas import Chibi_atlas


class Test_chibi_atlas( TestCase ):
    def setUp( self ):
        self.simple_dict = Chibi_atlas( a=10, b=20, c=30 )

    def test_can_retrieve_by_attr_and_key( self ):
        self.assertEqual( self.simple_dict.a, self.simple_dict[ 'a' ] )
        self.assertEqual( self.simple_dict.b, self.simple_dict[ 'b' ] )
        self.assertEqual( self.simple_dict.c, self.simple_dict[ 'c' ] )

    def test_retrieve_a_not_exists_attribute_raise_AttributeError( self ):
        with self.assertRaises( AttributeError ):
            self.simple_dict.d

    def test_set_an_attribute_dont_exists_should_be_retrieve_by_key( self ):
        new_value = 40
        self.simple_dict.d = new_value
        self.assertEqual( self.simple_dict.d, new_value )
        self.assertEqual( self.simple_dict[ 'd' ], new_value )

    def test_set_a_key_dont_exists_should_be_retrieve_by_attribute( self ):
        new_value = 40
        self.simple_dict[ 'd' ] = new_value
        self.assertEqual( self.simple_dict[ 'd' ], new_value )
        self.assertEqual( self.simple_dict.d, new_value )
