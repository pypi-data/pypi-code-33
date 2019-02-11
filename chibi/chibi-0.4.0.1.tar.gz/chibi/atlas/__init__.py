from collections import defaultdict


class Chibi_atlas( dict ):
    """
    Clase para crear dicionarios para que sus keys sean leibles como
    atributos de classes
    """
    def __getattr__( self, name ):
        try:
            return self[ name ]
        except KeyError as e:
            try:
                return super().__getattr__( name )
            except AttributeError as e:
                raise

    def __setattr__( self, name, value ):
        self[ name ] = value


class Chibi_atlas_ignore_case( Chibi_atlas ):
    def __init__( self, *args, **kw ):
        args_clean = []
        for a in args:
            if isinstance( a, dict ) or hasattr( a, 'items' ):
                args_clean.append( { k.lower(): v for k, v in a.items() } )
        kw = { k.lower(): v for k, v in kw.items() }
        super().__init__( *args_clean, **kw )

    def __getattr__( self, name ):
        name = name.lower()
        return super().__getattr__( name )

    def __getitem__( self, key ):
        key = key.lower()
        return super().__getitem__( key )

    def __setattr__( self, name, value ):
        name = name.lower()
        return super().__setattr__( name, value )

    def __setitem__( self, key, value ):
        key = key.lower()
        return super().__setitem__( key, value )


class Chibi_atlas_default( defaultdict, Chibi_atlas ):
    pass
