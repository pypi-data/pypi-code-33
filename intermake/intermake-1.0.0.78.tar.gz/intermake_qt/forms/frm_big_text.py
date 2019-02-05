from PyQt5.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox
from mhelper_qt import exceptToGui, exqtSlot
from intermake_qt.forms.designer import frm_big_text_designer


class FrmBigText( QDialog ):
    """
    Generic dialogue that shows text.
    
    See :method:`FrmBigText.request`
    """
    
    @exceptToGui()
    def __init__( self, parent, title, text, buttons ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_big_text_designer.Ui_Dialog( self )
        self.setWindowTitle( title )
        self.ui.TXT_MAIN.setText( text )
        self.ui.BTNBOX_MAIN.setStandardButtons( buttons )
        self.ui.BTNBOX_MAIN.clicked[QAbstractButton].connect( self.__on_BTNBOX_MAIN_clicked )
    
    
    @staticmethod
    def request( parent, title, text, buttons = QDialogButtonBox.NoButton ):
        frm = FrmBigText( parent, title, text, buttons )
        return frm.exec_()
    
    
    @exceptToGui()
    def __on_BTNBOX_MAIN_clicked( self, button: QAbstractButton ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTNBOX_MAIN_accepted( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTNBOX_MAIN_rejected( self ) -> None:
        """
        Signal handler:
        """
        pass
