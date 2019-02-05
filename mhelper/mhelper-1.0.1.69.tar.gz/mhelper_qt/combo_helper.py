from typing import Callable, Iterable

from PyQt5.QtWidgets import QComboBox


class ComboBoxWrapper:
    def __init__( self, box: QComboBox, options: Iterable = (), namer: Callable[[object], str] = str ):
        """
        :param box:         Combobox. 
        :param options:     Options, any iterable. 
        :param namer:       Method to obtain item names.         
        """
        self.box = box
        self.__source = options
        self.__options = None
        self.namer = namer
        self.populate()
        self.box.currentIndexChanged.connect( self.__on_currentIndexChanged )
        self.__has_forced = False
    
    
    def __on_currentIndexChanged( self, _: int ) -> None:
        self.__remove_forced()
    
    
    def populate( self ):
        self.__options = []
        self.box.clear()
        
        for option in self.__source:
            self.__add_item( option )
    
    
    def __add_item( self, option ):
        self.__options.append( option )
        name = self.namer( option )
        self.box.addItem( name )
    
    
    def __remove_forced( self, even_if_selected = False ):
        if not self.__has_forced:
            return
        
        # Forced is the last item
        i = len( self.__options ) - 1
        
        if self.box.currentIndex() == i and not even_if_selected:
            return
        
        self.box.removeItem( i )
        del self.__options[i]
        self.__has_forced = False
    
    
    @property
    def selected( self ) -> object:
        if self.box.currentIndex() < 0 or self.box.currentIndex() >= len( self.__options ):
            return None
        
        return self.__options[self.box.currentIndex()]
    
    
    @selected.setter
    def selected( self, value ):
        if value is None:
            if None in self.__options:
                index = self.__options.index( value )
            else:
                index = -1
        else:
            index = self.__options.index( value )
        
        self.box.setCurrentIndex( index )
    
    
    def force_selected( self, value ):
        self.__remove_forced( True )
        
        if value is not None and value not in self.__options:
            self.__add_item( value )
            self.__has_forced = True
        
        self.selected = value
    
    
    def __len__( self ):
        return len( self.__options )
    
    
    @property
    def enabled( self ):
        return self.box.isEnabled()
    
    
    @enabled.setter
    def enabled( self, value ):
        self.box.setEnabled( value )
    
    
    def __contains__( self, item ):
        return item in self.__options
    
    
    def append( self, option, select = False ):
        self.__options.append( option )
        self.__add_item( option )
        
        if select:
            self.box.setCurrentIndex( len( self ) - 1 )
