import unittest
from enum import Enum

from mhelper import Documentation
from mhelper.documentation_helper import get_enum_documentation, get_basic_documentation


class MyEnum( Enum ):
    """
    My enum.
    
    :cvar ALPHA: Hello once
    :cvar BETA: Hello twice
    """
    ALPHA = 1
    BETA = 2


class documentation_tests( unittest.TestCase ):
    def test_documentation( self ):
        text = """
        This is the documentation string.
        
        .. note::
        
            This is the notes string
        
        :param one:     One text line one
                        One text line two
                        One text line three
        :param two:     Two text line one
                            Two text line two indented.
                            Two text line three indented.
        :exception three: Value
                          Value
        """
        
        doc = Documentation( text )
        
        print( "********** doc.root.root **********\n{}\n**********".format( doc[""][""] ) )
        print( "********** doc.notes.root **********\n{}\n**********".format( doc["notes"][""] ) )
        print( "********** doc.param.one **********\n{}\n**********".format( doc["param"]["one"] ) )
        print( "********** doc.param.one **********\n{}\n**********".format( doc["param"]["two"] ) )
        
        print( "********** MyEnum **********\n{}\n**********".format( get_basic_documentation( MyEnum ) ) )
        print( "********** MyEnum.ALPHA **********\n{}\n**********".format( get_enum_documentation( MyEnum.ALPHA ) ) )
        
        
        
