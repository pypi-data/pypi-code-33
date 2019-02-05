from mhelper import string_helper, SwitchError
from intermake.helpers import printing


class HelpTopic:
    """
    A help topic for access in an `Intermake`:t: application.
    
    :ivar key:          READONLY.
                        Key that can be used to access the topic.
                        This should be unique and not conflict with any command names either.
                        This defaults to the name if no key is specified.
    :ivar name:         READONLY.
                        Name of the topic.
                        Should be a one line, descriptive name.
    :ivar format:       READONLY.
                        Format of the topic text.
                        Should either be ``"rst"`` for RST or ``"html"`` for HTML/XML.
    :ivar __content:    READONLY.
                        Content of the topic.
                        This may be provided as a dynamic function or a static `str`.
                        This may be formatted as RST or HTML/XML.
                        If HTML, only the subset of HTML defined by the ``sxsxml`` library is
                        supported. 
    """
    
    
    def __init__( self, *args, format = "html" ):
        """
        CONSTRUCTOR
        
        Specify either two (name, content) or three (key, name, content) arguments.
        
        See variable descriptions for argument descriptions.
        """
        self.format = format
        
        if len( args ) == 3:
            self.key, self.name, self.__content = args
        elif len( args ) == 2:
            self.name, self.__content = args
            self.key = self.name
        else:
            raise ValueError( "HelpTopic.__init__ requires 2 or 3 arguments, but {} were provided.".format( len( args ) ) )
    
    
    def to_html( self ):
        """
        Obtains the topic text.
        """
        r = self.__to_str()
        
        if self.format == "rst":
            r = printing.fmt_rst( r )
        elif self.format == "html":
            pass
        else:
            raise SwitchError( "self.format", self.format )
        
        return r
    
    
    def __to_str( self ):
        if isinstance( self.__content, str ):
            r = self.__content
        else:
            r = self.__content()
        return r
    
    
    def __str__( self ):
        return "'{}/{}': '{}'".format( self.key, self.name, string_helper.max_width( string_helper.shrink_space( self.__to_str() ), 30 ) )
    
    
    def __repr__( self ):
        return "{}('{}', '{}', '{}')".format( type( self ).__name__, self.key, self.name, string_helper.max_width( string_helper.shrink_space( self.__to_str() ), 30 ) )
