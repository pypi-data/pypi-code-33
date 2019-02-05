from typing import Iterable, Callable, Dict, List, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget, QTreeWidgetItem

from mhelper_qt.qt_gui_helper import exqtSlot
from mhelper_qt.designer import frm_generic_list_designer


class FrmGenericList( QDialog ):
    """
    A generic list selector.
    
    ```
    +------------------------------+
    + title                      X + 
    +------------------------------+
    | [ message ]                  |
    | +--------------------------+ |
    | | list                     | |
    | |                          | |
    | +--------------------------+ |
    |                 [ok][cancel] |
    +------------------------------+
    ```
    """
    
    
    def __init__( self,
                  parent: QWidget,
                  title: str,
                  message: str,
                  options: Iterable,
                  selected: Iterable,
                  multi: bool,
                  format: Callable[[object], str],
                  ) -> None:
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = frm_generic_list_designer.Ui_Dialog( self )
        if title:
            self.setWindowTitle( title )
        else:
            self.setWindowTitle( parent.windowTitle() )
        if message:
            self.ui.LBL_MAIN.setText( message )
        else:
            self.ui.LBL_MAIN.setVisible( False )
        self.map: Dict[object, QTreeWidgetItem] = { }
        self.result: List[object] = None
        
        for option in options:
            item = QTreeWidgetItem()
            item.setText( 0, format( option ) )
            self.ui.TVW_MAIN.addTopLevelItem( item )
            self.map[option] = item
            
            if multi:
                item.setCheckState( 0, Qt.Unchecked )
        
        for option in selected:
            if multi:
                self.map[option].setCheckState( 0, Qt.Checked )
            else:
                self.map[option].setSelected( True )
    
    
    def request( self,
                 parent: QWidget = None,
                 title: str = "",
                 message: str = "",
                 options: Iterable = (),
                 selected: Union[object, Iterable] = None,
                 multi: bool = False,
                 format: Callable[[object], str] = str ) -> Union[List[object], object, None]:
        """
        Shows the form.
        
        :param parent:      Parent window 
        :param title:       Title. Empty uses parent window title.
        :param message:     Message. Empty displays no message. 
        :param options:     Options. 
        :param selected:    Selected item. Iterable for `multi` mode, otherwise one item, or `None` for no selection. 
        :param multi:       `multi` select mode. 
        :param format:      How to format options into strings. 
        :return:            A list of options, for `multi`, a single item otherwise, or `None` if cancelled by user. 
        """
        if selected is None:
            selected = ()
        elif not multi:
            selected = selected,
        
        frm = FrmGenericList( parent, title, message, options, selected, multi, format )
        
        if frm.exec_():
            if multi:
                return frm.result[0]
            else:
                return frm.result
        
        return None
    
    
    @exqtSlot()
    def on_BTNBOX_MAIN_accepted( self ) -> None:
        """
        Signal handler:
        """
        r = []
        
        for option, item in self.map.items():
            if item.checkState( 0 ) == Qt.Checked:
                r.append( item )
        
        self.result = r
    
    
    @exqtSlot()
    def on_BTNBOX_MAIN_rejected( self ) -> None:
        """
        Signal handler:
        """
        pass
