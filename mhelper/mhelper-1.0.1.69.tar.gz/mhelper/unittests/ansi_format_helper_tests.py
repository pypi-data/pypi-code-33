import unittest

from mhelper import ansi_format_helper


class ansi_format_helper_tests( unittest.TestCase ):
    
    def test_traceback( self ):
        try:
            raise ValueError( "Something didn't actually go wrong." )
        except Exception as ex:
            ansi_format_helper.format_traceback_ex( ex )


