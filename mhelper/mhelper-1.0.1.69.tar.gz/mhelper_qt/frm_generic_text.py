from typing import Callable, Union

import PyQt5.QtWidgets as qt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption
from mhelper_qt.qt_gui_helper import exceptToGui


class FrmGenericText( qt.QDialog ):
    """
    A generic text box, similar to Notepad.
    
    ```
    +------------------------------+
    + title                      X + 
    +------------------------------+
    | +--------------------------+ | 
    | | text                     | |
    | |                          | |
    | |                          | |
    | |                          | |
    | +--------------------------+ | 
    |                 [ok][cancel] |
    +------------------------------+
    ```
    """
    
    
    def __init__( self,
                  parent: qt.QWidget,
                  *,
                  title: str = None,
                  text: str = None,
                  message: str = None,
                  caption: str = None,
                  confirm: bool = False,
                  editable: bool = False,
                  continuous: bool = False,
                  test: Callable[[str], object] = None,
                  details: str = None ):
        """
        CONSTRUCTOR
        
        :param parent:        Parent window. 
        :param title:         Window title. `None` inherits parent. 
        :param text:          Edit text.
                              `None` shows no edit box, unless `editable` is set.
        :param message:       Message label (top). `None` shows no message. 
        :param caption:       Caption label (bottom). `None` shows no caption. 
        :param editable:      Editable.
                              `True` enables the `text` editor (if present).
                              `False` ensures any `text` editor present is read-only.
        :param confirm:       Whether to show Ok|Cancel buttons.
                              This is implicit if "editable" is set.
        :param continuous:    Assert text as it is being typed, rather than when the user clicks `ok`.
        :param test:          Function for asserting the validity of the text. See `on_try_accept`.
        :param details:       Details button text. `None` hides the details button.
        """
        qt.QDialog.__init__( self, parent )
        self.editable = editable
        self.fn_try_accept = test
        
        # Defaults
        if editable:
            text = text or ""
            confirm = True
        
        # TITLE
        if title is None:
            title = parent.windowTitle()
        
        self.setWindowTitle( title )
        
        # LAYOUT
        self.layout = qt.QVBoxLayout()
        self.setLayout( self.layout )
        
        # TOP-LABEL
        if message is not None:
            self.message_label = qt.QLabel()
            self.message_label.setText( message )
            self.message_label.setWordWrap( True )
            self.layout.addWidget( self.message_label )
        
        # TEXT EDIT 
        if text is not None:
            self.persistent_checking = continuous
            self.text_edit = qt.QTextEdit()
            self.text_edit.setText( text )
            self.text_edit.setReadOnly( not editable )
            self.text_edit.setWordWrapMode( QTextOption.WrapAtWordBoundaryOrAnywhere )
            self.text_edit.setSizePolicy( qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding )
            self.layout.addWidget( self.text_edit )
        else:
            self.persistent_checking = False
            
        self.has_editable_text = editable
        
        if editable and continuous:
            self.text_edit.textChanged.connect( self.__on_textChanged )
        
        # TOP-LABEL
        if caption is not None:
            self.caption_label = qt.QLabel()
            self.caption_label.setText( caption )
            self.caption_label.setWordWrap( True )
            self.layout.addWidget( self.caption_label )
        
        # ERROR-LABEL
        if self.persistent_checking:
            self.error_label = qt.QLabel()
            self.error_label.setWordWrap( True )
            self.error_label.setVisible( False )
            self.error_label.setStyleSheet( "color:red;" )
            self.layout.addWidget( self.error_label )
        
        # BUTTONS
        self.button_box = qt.QDialogButtonBox()
        self.button_box.setOrientation( Qt.Horizontal )
        self.button_box.accepted.connect( self.__on_button_box_accepted )
        btn = qt.QDialogButtonBox.Ok
        
        if confirm:
            btn |= qt.QDialogButtonBox.Cancel
            self.button_box.rejected.connect( self.__on_button_box_rejected )
        
        self.button_box.setStandardButtons( btn )
        
        if details:
            self.details = details
            button = self.button_box.addButton( "Details...", qt.QDialogButtonBox.ActionRole )
            button.clicked[bool].connect( self.__on_information_clicked )
        
        self.layout.addWidget( self.button_box )
    
    
    def __on_information_clicked( self ):
        self.request( parent = self,
                      text = self.details )
    
    
    @staticmethod
    def request( *args, **kwargs ) -> Union[None, bool, str]:
        frm = FrmGenericText( *args, **kwargs )
        return frm.exec_()
    
    
    def exec_( self ) -> Union[None, bool, str]:
        """
        Executes the form.
        
        Result:
        
               | EDITABLE  |           | NOT-EDITABLE |
        -------|-----------|-----------|--------------|------------ 
               | TEXT      | NO-TEXT   | TEXT         | NO-TEXT
        OK     | `text`    | `True`    | Undefined*   | Undefined*
        CANCEL | `None`    | `False`   | N/A          | N/A
        
        *Currently `True`
        """
        if super().exec_():
            if self.has_editable_text:
                return self.text_edit.toPlainText()
            else:
                return True
        else:
            if self.has_editable_text:
                return None
            else:
                return False
    
    
    def on_try_accept( self, text: str ) -> None:
        """
        A derived class may override this to assert input before continuing.
        If the form is not editable, or has no edit text, this is not called.
        
        If the derived class objects to the text, it should raise an exception.
        Any return value, if present, is ignored.
        
        If not overridden, the `test` value passed into the constructor is called,
        if present. 
        """
        if self.fn_try_accept is not None:
            self.fn_try_accept( text )
    
    
    @exceptToGui()
    def __on_button_box_accepted( self ) -> None:
        if self.has_editable_text:
            self.try_accept()
        
        self.accept()
    
    
    def try_accept( self ):
        self.on_try_accept( self.text_edit.toPlainText() )
    
    
    def __on_textChanged( self ) -> bool:
        try:
            self.try_accept()
        except Exception as ex:
            self.error_label.setText( str( ex ) )
            self.error_label.setVisible( True )
            return False
        else:
            self.error_label.setVisible( False )
            return True
    
    
    @exceptToGui()
    def __on_button_box_rejected( self ) -> None:
        self.reject()
