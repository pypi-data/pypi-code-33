"""
Contains the `_LocalData` class.

"""
import os
import warnings
from os import path
from typing import Optional, TypeVar, Iterator, Tuple, Dict
import mhelper as mh

from intermake.engine import constants
from mhelper import file_helper


_T = TypeVar( "_T" )
_LOG = mh.Logger( "autostore", False )


class _LocalData:
    """
    INTERNAL FINAL
    
    Manages |app_name|'s primary workspace folder and settings therein, usually ``"~/.intermake/|app_name|"``
    """
    __AUTOSTORE_EXTENSION = ".pickle"
    
    
    def __init__( self, app_name: str ) -> None:
        """
        CONSTRUCTOR
        """
        
        if not path.sep in app_name:
            workspace = path.expanduser( path.join( "~", ".intermake", app_name ) )
        else:
            workspace = app_name
        
        redirect_file_name: str = path.join( workspace, "redirect.txt" )
        
        if path.isfile( redirect_file_name ):
            workspace = mh.file_helper.read_all_text( redirect_file_name ).strip()
        
        if not workspace or path.sep not in workspace:
            raise ValueError( "A complete workspace path is required, «{}» is not valid.".format( workspace ) )
        
        self.__redirect_file_name = redirect_file_name
        self.__app_name: str = app_name
        self.workspace: str = path.expanduser( workspace )
        self.__settings_path: str = self.local_folder( constants.FOLDER_SETTINGS )
        self.__settings: Dict[str, _LocalDataValue] = { }
        
        mh.file_helper.create_directory( self.__settings_path )
    
    
    def set_redirect( self, content: Optional[str] ) -> None:
        """
        Sets or clears the workspace redirection.
        
        This takes effect from the next application restart.
        """
        if content:
            mh.file_helper.write_all_text( self.__redirect_file_name, content )
        else:
            mh.file_helper.delete_file( self.__redirect_file_name )
    
    
    def local_folder( self, *args: str ) -> str:
        """
        Obtains the path to a specific folder within the workspace.
        """
        folder_name = path.join( self.workspace, *args )
        mh.file_helper.create_directory( folder_name )
        return folder_name
    
    
    def bind( self, key: str, default: _T ) -> _T:
        """
        Retrieves a proxy to the specified setting that commits values to disk
        when its fields are changed.
        
        Note that only attribute changes are registered, not changes to
        attributes of attributes, etc.
        
        This is only usable with simple classes that have a __dict__, i.e. not
        basic types (int) or complex ones (Enum).
        
        :param key:         Key of setting
        
        :param default:     Default values and type.
                            * Fields present in this object will be copied into the setting
                            * Fields not present in this object will be removed from the setting
                            * If the setting is not of this type, the setting object will be replaced with this object
        """
        v = self.__find( key )
        v.apply_default( default )
        return v.get_proxy()
    
    
    def commit( self, key: object, value: object = None ) -> None:
        """
        Saves a specific setting.
        
        :param key:   Either:
                      * the key
                      * the proxy object returned from `bind`
                      * the setting instance returned from `retrieve`
                      
        :param value: Value to commit.
                      This is only required if the setting was not previously
                      retrieved using `retrieve` or `bind`. Settings instance
                      are fixed once bound, and attempting to change the
                      instance of a setting will result in an error.
        """
        if value is None:
            return self.__find( key ).commit()
        else:
            return self.__find( key ).set_value( value )
    
    
    def retrieve( self, key: str, value: Optional[_T] = None ):
        """
        This method is equivalent to `bind`, but does *not* wrap the result in 
        an auto-committing proxy.  
        """
        v = self.__find( key )
        v.apply_default( value )
        return v.get_value()
    
    
    def __find( self, key: object ) -> "_LocalDataValue":
        """
        Gets the `_AutoStoreValue` for a particular key. 
        """
        if isinstance( key, str ):
            r = self.__settings.get( key )
            
            if r is None:
                file_name = path.join( self.__settings_path, key + self.__AUTOSTORE_EXTENSION )
                r = _LocalDataValue( key, file_name )
                self.__settings[key] = r
            
            return r
        elif isinstance( key, mh.SimpleProxy ):
            return object.__getattribute__( key, _LocalDataValue.KEY_TAG )
        else:
            for value in self.__settings.values():
                if value.get_value() is key:
                    return value
        
        raise ValueError( "This is not a valid accessor for an _AutoStoreValue: {}".format( key ) )
    
    
    def iter_load_all( self, from_file: bool ) -> Iterator[Tuple[str, object]]:
        """
        Returns tuples of keys and instances for all settings that are presently
        known about.
        """
        if from_file:
            keys_1 = set( file_helper.get_filename_without_extension( file ) for file in file_helper.list_dir( self.__settings_path, self.__AUTOSTORE_EXTENSION ) )
        else:
            keys_1 = set()
        
        keys_2 = set( self.__settings.keys() )
        
        for key in sorted( set.union( keys_1, keys_2 ) ):
            value: _LocalDataValue = self.__find( key ).get_value()
            yield key, value
    
    
    def __repr__( self ):
        return "{}({})".format( type( self ).__name__, self.__app_name )


class _LocalDataValue:
    """
    Manages a particular setting.
    These objects are persistent once the setting has been retrieved.
    
    :cvar KEY_TAG:          Tag used to attach the key to the returned proxies.
    
    :ivar key:              Key for the setting
    :ivar file_name:        File for the setting    
    :ivar __value:          The value.
                            If not on disk this is `None` until a default is
                            applied. This is a fixed instance once accessed via
                            `get_value`. 
    :ivar __proxy:          Proxy wrapping `__value`.
                            This is `None` until required.
    :ivar __has_accessed:   Whether `__value` has been accessed and is now fixed to
                            a particular instance. This is a sanity check only.
    """
    KEY_TAG = "_LocalDataValue__key"
    
    
    def __init__( self, key: str, file_name: str ):
        self.key = key
        self.file_name = file_name
        self.__value = mh.io_helper.load_binary( self.file_name, delete_on_fail = True, default = None ) if os.path.isfile( self.file_name ) else None
        self.__proxy = None
        self.__has_accessed = False
    
    
    def get_value( self ):
        self.__has_accessed = self.__value is not None
        return self.__value
    
    
    def set_value( self, value ):
        if self.__has_accessed:
            if value is not self.__value:
                raise ValueError( "For this setting, {}, I cannot change the value instance from ({}) {} to ({}) {} because it has already been accessed.".format( self, type( value ), value, type( self.__value ), self.__value ) )
        
        self.__value = value
        self.commit()
    
    
    def __str__( self ):
        return "VALUE( KEY: {} | FILE: {} | TYPE: {} | VALUE: {} )".format( repr( self.key ), repr( self.file_name ), repr( type( self.__value ).__name__ ), repr( self.__value ) )
    
    
    def apply_default( self, default: object ):
        if default is None:
            return
        
        if self.__value is None:
            self.set_value( default )
            return
        
        if type( default ) is not type( self.__value ):
            warnings.warn( "Recreating setting '{}' because its type has changed from '{}' to '{}' since it was last accessed."
                           .format( self, type( self.__value ).__name__, type( default ).__name__ ) )
            self.set_value( default )
            return
        
        if not hasattr( self.__value, "__dict__" ):
            raise ValueError( "For this setting, {}, I apply a default because it is of a special type.".format( self ) )
        
        set_cur = set( x for x in self.__value.__dict__ if not x.startswith( "_" ) )
        set_def = set( x for x in default.__dict__ if not x.startswith( "_" ) )
        to_add = set_def - set_cur
        to_rem = set_cur - set_def
        changes = to_add.union( to_rem )
        
        if not changes:
            return
        
        for f_name in to_add:
            f_value = default.__dict__[f_name]
            self.__value.__dict__[f_name] = f_value
        
        for f_name in to_rem:
            del self.__value.__dict__[f_name]
        
        warnings.warn( "Updated setting by adding new keys and removing old keys because the class definition has changed since the setting was last accessed.\n"
                       "Setting: {}\n"
                       "Added:   {}\n"
                       "Removed: {}"
                       .format( self, to_add, to_rem ) )
        
        self.set_value( self.__value )
    
    
    def get_proxy( self ):
        if self.__proxy is None:
            value = self.get_value()
            
            if value is None:
                raise ValueError( "For this setting, {}, I cannot get the proxy because there is no value instance to bind to.".format( self ) )
            
            if not hasattr( value, "__dict__" ):
                raise ValueError( "For this setting, {}, I cannot bind a proxy because it is of a special type.".format( self ) )
            
            self.__proxy = mh.SimpleProxy( target = value, on_set_attr = self.__handle_proxy_changed )
            object.__setattr__( self.__proxy, self.KEY_TAG, self )  # sets the field on the proxy, not the underlying object
        
        return self.__proxy
    
    
    def commit( self ) -> None:
        if self.__value is None:
            raise ValueError( "For this setting, {}, there is no value to commit.".format( self ) )
        
        _LOG( "write {}", self.file_name )
        mh.io_helper.save_binary( self.file_name, self.__value )
    
    
    def __handle_proxy_changed( self, _ ):
        self.commit()
