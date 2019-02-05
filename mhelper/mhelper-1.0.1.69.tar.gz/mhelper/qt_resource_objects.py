import warnings


__author__ = "Martin Rusilowicz"


class ResourceIcon:
    """
    References a Qt resource.
    If multiple `ResourceIcon` reference the same cached resource will be used.
    
    .. note::
    
        This class not load or require the Qt library until/unless the :method:`icon` is called.
    """
    
    SEARCH = []
    CACHE = { }
    
    
    @classmethod
    def add_search( cls, text: str ):
        cls.SEARCH.append( text )
    
    
    def __init__( self, path: str ):
        """
        CONSTRUCTOR
        
        :param path: Resource path (e.g. ":/blah.svg") or resource name (eg. "blah").
                     If just a name is specified then :cvar:`SEARCH` will be consulted.
        """
        self._path = path
        self._icon = None
    
    
    @property
    def path( self ):
        return self._path
    
    
    def __repr__( self ):
        return "ResourceIcon('{}' ({}))".format( self._path, "pending" if self._icon else "loaded" )
    
    
    def __call__( self ):
        """
        Calls :method:`icon`.
        """
        return self.icon()
    
    
    def icon( self ):
        """
        Obtains the icon actual.
        """
        from PyQt5.QtGui import QIcon
        
        
        if not self._icon:
            cached = self.CACHE.get( self._path )
            
            if cached is not None:
                self._icon = cached
            else:
                from PyQt5.QtCore import QFile
                
                if ":" not in self._path:
                    final = None
                    for search in type( self ).SEARCH:
                        path = search.replace( "*", self._path )
                        if QFile.exists( path ):
                            final = path
                            break
                    
                    if final is None:
                        warnings.warn( "No such icon as «{}», given searches «{}».".format( self._path, type( self ).SEARCH ), UserWarning )
                        final = self._path
                else:
                    final = self._path
                
                self._icon = QIcon( final )
                self.CACHE[self._path] = self._icon
        
        return self._icon
