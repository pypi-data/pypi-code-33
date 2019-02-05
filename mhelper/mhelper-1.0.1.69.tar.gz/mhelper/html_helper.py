class HtmlHelper:
    @classmethod
    def begin_body( cls, title ):
        return HtmlHelper( '<html><title>{}</title><body>'.format( title ), "</body></html>" )
    
    
    def __init__( self, opening = "", closing = "" ):
        self.opening = opening
        self.closing = closing
        self.contents = []
    
    
    def __enter__( self ) -> "HtmlHelper":
        return self
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        pass
    
    
    def begin( self, element, **kwargs ):
        r = HtmlHelper( "<{} {}>".format( element,
                                          " ".join( '{}="{}"'.format( k, v ) for k, v in kwargs.items() ) ),
                        "</{}>".format( element ) )
        
        self.contents.append( r )
        return r
    
    
    def add( self, text ):
        self.contents.append( text )
    
    
    def to_html( self ):
        r = []
        r.append( self.opening )
        
        for element in self.contents:
            if isinstance( element, HtmlHelper ):
                r.append( element.to_html() )
            elif isinstance( element, str ):
                r.append( element )
        
        r.append( self.closing )
        
        return "\n".join( r )
