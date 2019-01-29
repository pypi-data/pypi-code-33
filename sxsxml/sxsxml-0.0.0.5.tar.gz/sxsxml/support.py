from typing import Callable, Tuple, List, Dict


class _DirectedOutput:
    def __init__( self, target ):
        self.target = target
    
    
    def write( self, data ):
        self.target( data )
    
    
    def flush( self ):
        pass


class XsProgress:
    """
    Defines progress on an action.
    """
    
    
    def __init__( self, id: str, value: str, max: str, text: str, elapsed: str ):
        self.id: str = id
        
        try:
            self.value = int( value )
        except ValueError:
            self.value = 0
        
        try:
            self.max = int( max )
        except:
            self.value = 0
        
        self.text = text
        self.elapsed = elapsed
    
    
    @property
    def is_end( self ):
        return self.value == self.max
    
    
    @property
    def percent( self ):
        if self.is_end:
            return 100
        elif self.max:
            return int( (self.value / self.max) * 100 )
        else:
            return 0


class XsElement:
    """
    Represents an element of the form ``'<name attr1="value1" attr2="value2">'``
    """
    
    
    def __init__( self, raw: str, name: str, attr: Dict[str, str] ) -> None:
        self.raw = raw
        self.name = name
        self.attr = attr
    
    
    def get( self, item, default = "" ):
        return self.attr.get( item, default )
    
    
    def __repr__( self ) -> str:
        return "XsElement({}, {})".format( repr( self.name ), repr( self.attr ) )
    
    
    def __str__( self ):
        return "<{} {}>".format( self.name, " ".join( "{} = {}".format( x, y ) for x, y in self.attr.items() ) )


class XsStack:
    """
    Element stacking
    """
    
    
    def __init__( self, target: Callable[[str], None] ):
        super().__init__()
        self.__target = target
        self.__stack: Tuple[XsElement, List[str]] = (None, [])
        self.__stacks: List[Tuple[XsElement, List[str]]] = [self.__stack]
    
    
    def write( self, x: str ) -> None:
        if len( self.__stacks ) == 1:
            self.__target( x )
            return
        
        self.__stack[1].append( x )
    
    
    def push( self, e: XsElement ):
        self.__stack = e, []
        self.__stacks.append( self.__stack )
    
    
    def pop( self, e: XsElement ):
        text = "".join( self.__stack[1] )
        a = self.__stacks.pop()[0]
        
        if a is not e:
            raise ValueError( "Tried to pop the element '{}' from the stack but element at the top of the stack is '{}' (after '{}')."
                              "Check the element was pushed and in the correct order.".format( e, a, ", ".join( str( x[0] ) for x in self.__stacks ) ) )
        
        self.__stack = self.__stacks[-1]
        return text
    
    
    def reset( self ):
        self.__stack = (None, [])
        self.__stacks = [self.__stack]
