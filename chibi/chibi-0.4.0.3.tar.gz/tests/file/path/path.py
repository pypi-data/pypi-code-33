from unittest import TestCase
from chibi.file.path import Chibi_path
from chibi.file.snippets import ls, join, file_dir
from tests.snippet.files import Test_with_files


class Test_path( Test_with_files ):
    def setUp( self ):
        super().setUp()
        self.path = Chibi_path( self.root_dir )

    def test_can_add_path_and_str( self ):
        dirs = ls( self.root_dir )
        for d in dirs:
            result = self.path + d
            self.assertEqual(
                result, join( str( self.path ), d ) )


class Test_path_with_files( Test_with_files ):
    def test_if_path_is_a_file_should_only_use_the_dir( self ):
        for f in self.files:
            d = file_dir( f )
            p_f = Chibi_path( f )
            self.assertEqual( p_f + "another", join( d, 'another' ) )
