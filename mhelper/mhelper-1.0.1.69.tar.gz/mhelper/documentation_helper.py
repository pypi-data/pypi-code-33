import sys
from typing import Union, Dict, List, Optional
import re
from mhelper import exception_helper


_RX_DIRECTIVE = re.compile( "^ *:(.+) +(.+): *(.+)$" )
"""
_______:blah_____blah:_____blah
        1111     2222      3333
"""

_RX_BARE_DIRECTIVE = re.compile( "^ *:(.+): *(.*)$" )
"""
_______:blah:_____blah
        1111      2222
"""

_RX_DOMAIN = re.compile( "^ *(.+):: *(.*)$" )
"""
________blah::____blah
        1111      2222
"""


class Documentation:
    """
    Class to manage and create a documentation `dict` - see `parse_doc`.
    
    .. code-block::
    
        doc = Documentation( x.__doc__ )
        
        # Root domain
        print( doc[""][""] )
        
        # Bare domain
        print( doc["usage"][""] )
        
        # Domain attribute
        print( doc["param"]["doc"] )
    """
    
    
    def __init__( self, doc: Optional[str] ):
        if doc is None:
            doc = ""
        
        exception_helper.safe_cast( "doc", doc, str )
        
        element = ""
        domain = ""
        content = []
        text_start = 0
        self.data = { }
        
        for line in doc.split( "\n" ):
            rx = _RX_DIRECTIVE.match( line )
            
            if rx:
                self.__add_and_clear( domain, element, content )
                
                domain = rx.group( 1 )
                element = rx.group( 2 )
                text = rx.group( 3 )
                text_start = rx.span( 3 )[0]
            else:
                rx = _RX_BARE_DIRECTIVE.match( line )
                
                if rx:
                    self.__add_and_clear( domain, element, content )
                    
                    domain = rx.group( 1 )
                    element = ""
                    text = rx.group( 2 )
                    text_start = rx.span( 2 )[0]
                else:
                    rx = _RX_DOMAIN.match( line )
                    
                    if rx:
                        self.__add_and_clear( domain, element, content )
                        domain = rx.group( 1 )
                        element = ""
                        text = rx.group( 2 )
                        text_start = rx.span( 2 )[0]
                    else:
                        text = line
                        
                        if not content:
                            text_start = len( text ) - len( text.lstrip() )
                        
                        if all( x == " " for x in line[:text_start] ):
                            text = text[text_start:]
            
            if content or text:
                content.append( text )
        
        self.__add_and_clear( domain, element, content )
    
    
    def get_domain( self, domain: str, default = None ) -> Dict[str, str]:
        """
        Gets the dictionary associated with a domain.
        
        :param domain:      Domain to get 
        :param default:     Default if not found.
                            `object` = Value to return
                            `None` = Empty dict (default)
                            `NOT_PROVIDED` = Raise error 
        :return: 
        """
        return exception_helper.assert_provided( self.data.get( domain, default or { } ), details = (self, domain) )
    
    
    def get_element( self, domain: str, element: str, default = "" ) -> str:
        """
        Gets the content associated with a domain and element.
        
        :param domain:      Domain to get
        :param element:     Element to get
        :param default:     Default if not found.
                            `object` = Value to return
                            `NOT_PROVIDED` = Raise error 
        """
        d = self.data.get( domain, None )
        
        if d is None:
            return exception_helper.assert_provided( default, details = (self, domain) )
        
        return exception_helper.assert_provided( d.get( element, default ), details = (self, domain, element) )
    
    
    def __getitem__( self, item: object ) -> Union[str, Dict[str, str]]:
        """
        Returns `get_domain` or `get_element`.
        
        :param item:    `str` = Calls `get_domain`
                        `tuple` = Calls `get_element`  
        """
        if isinstance( item, str ):
            return self.get_domain( item )
        elif isinstance( item, tuple ):
            return self.get_element( item[0], item[1] )
        else:
            raise exception_helper.type_error( "item", item, Union[str, tuple] )
    
    
    def __add_and_clear( self, domain: str, element: str, content: List[str] ) -> None:
        c = self.data.get( domain )
        
        if c is None:
            c = { }
            self.data[domain] = c
        
        c[element] = "\n".join( content ).rstrip()
        
        content.clear()
    
    
    def debug( self ):
        for k, v in self.data.items():
            sys.__stderr__.write( "(DOC) CATEGORY: " + k + "\n" )
            
            for k2, v2 in v.items():
                sys.__stderr__.write( "(DOC) ++++ NAME: " + k2 + "\n" )
                for line in v2.split("\n"):
                    sys.__stderr__.write( "(DOC) ++++ ++++ " + line + "\n" )


def get_enum_documentation( field ):
    return Documentation( field.__doc__ )["cvar", field.name]


def get_basic_documentation( entity ):
    return Documentation( entity.__doc__ )["", ""]
