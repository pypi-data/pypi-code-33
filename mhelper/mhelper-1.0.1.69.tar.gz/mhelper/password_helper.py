class ManagedPassword:
    DEFAULT_KEYRING = "python_mhelper"
    
    
    def __init__( self, password, *, key = None, keyring = None, managed = True ):
        if not key:
            import uuid
            key = str( uuid.uuid4() )
        
        self.__key = key
        self.__keyring = keyring
        self.__password = password
        self.__managed = managed
        
        if self.__password and self.__managed:
            import keyring
            keyring.set_password( self.keyring, self.key, self.__password )
    
    
    @property
    def key( self ):
        return self.__key
    
    
    @property
    def keyring( self ):
        return self.__keyring or self.DEFAULT_KEYRING
    
    
    @property
    def password( self ):
        if self.__password is None:
            if self.__managed:
                import keyring
                self.__password = keyring.get_password( self.keyring, self.key )
            else:
                raise ValueError( "Logic error, unmanaged password but no password is specified." )
        
        return self.__password
    
    
    def delete( self ):
        if not self.__key:
            raise ValueError( "Logic error, attempt to delete a password that is already deleted." )
        
        if self.__managed:
            import keyring
            keyring.delete_password( self.keyring, self.key )
        
        self.__key = None
        self.__keyring = None
        self.__password = None
        self.__managed = False
    
    
    def __setstate__( self, state ):
        self.__key = state["key"]
        self.__keyring = state["keyring"]
        self.__password = state["password"]
        self.__managed = state["managed"]
    
    
    def __getstate__( self ):
        return { "key"     : self.__key,
                 "keyring" : self.__keyring,
                 "managed" : self.__managed,
                 "password": self.password if not self.__managed else None }
    
    
    def __repr__( self ):
        return "{}(key={},keyring={})".format( type( self ).__name__, repr( self.__key ), repr( self.__keyring ) )
    
    
    def __str__( self ):
        return "********"
