import inspect


class SimpleTestCollection:
    def __init__( self ):
        self.tests = []
    
    
    def __call__( self, fn ):
        import mhelper.file_helper
        f = inspect.stack()[1].filename
        m = mhelper.file_helper.get_filename_without_extension( f ) + "/" + fn.__qualname__
        m = m.replace( "_tests", "" )
        m = m.replace( "test_", "" )
        self.tests.append( (m, fn) )
        return fn
    
    
    def list( self ):
        r = []
        for m, x in self.tests:
            r.append( "{}".format( m ) )
        return r
    
    
    def execute( self ):
        for m, x in self.tests:
            print( "EXECUTE {}".format( m ) )
            try:
                x()
            except Exception as ex:
                from mhelper import ansi_format_helper
                ansi_format_helper.print_traceback( ex )
                return
    
    
    def testing( self, a ):
        return Testing( a )


class Testing:
    def __init__( self, v ):
        self.v = v
    
    
    def __repr__( self ):
        return ""
    
    
    def ISINSTANCE( self, expected_type ):
        actual = self.v
        
        assert isinstance( actual, expected_type )
    
    
    def SEQUALS( self, expected ):
        assert_equals( set( self.v ), set( expected ) )
    
    
    def TRUE( self ):
        assert_equals( self.v, True )
    
    
    def FALSE( self ):
        assert_equals( self.v, False )
    
    
    def EQUALS( self, expected ):
        assert_equals( self.v, expected )
    
    
    def ERRORS( self, t = Exception ):
        try:
            self.v()
        except t:
            pass
        else:
            assert False, "Expected error"


def assert_equals( actual, expected ):
    if expected is None or expected is True or expected is False:
        assert actual is expected
    assert actual == expected
