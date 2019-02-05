class MAnnotation:
    """
    This class defines an annotation that may be used as a PEP484 style annotation
    on function parameters and return values.
    
    The MAnnotaion is defined by a set of parameters:
    Generally the first parameter is expected to be the name, and the second the type, with further
    parameters being dependent upon the purpose of the annotation itself.
    """
    
    
    def __init__( self, *args, **kwargs ):
        """
        Constructs the annotation with the specified parameters.
        """
        self.parameters = args
    
    
    def __str__( self ) -> str:
        """
        Formats the annotation for display
        """
        return "{}[{}]".format( self.parameters[0], ", ".join( x.__name__ if isinstance( x, type ) else str( x ) for x in self.parameters[1:] ) )
    
    
    def __repr__( self ) -> str:
        """
        Formats the annotation for debugging
        """
        return "{}({})".format( type( self ).__name__, ", ".join( repr( x ) for x in self.parameters ) )
    
    
    def __call__( self, *args, **kwargs ) -> "MAnnotation":
        """
        Calling the annotation creates a copy of this annotation with the specified parameters
        appended to it.
        """
        return type( self )( *self.parameters, *args, **kwargs )
    
    
    def __getitem__( self, item ) -> "MAnnotation":
        """
        __getitem__ is equivalent to __call__ to permit "Generic"-style annotation derivations.
        """
        if isinstance( item, tuple ):
            return self( *item )
        else:
            return self( item )
    
    
    def is_derived_from( self, parent: "MAnnotation" ) -> bool:
        """
        Returns if the current annotation has at least the same set of parameters as
        a parent annotation, i.e. it is the parent annotation or is derived from it.
        """
        assert isinstance(parent, MAnnotation), parent
        np = len( parent.parameters )
        return len( self.parameters ) >= np and self.parameters[:np] == parent.parameters
