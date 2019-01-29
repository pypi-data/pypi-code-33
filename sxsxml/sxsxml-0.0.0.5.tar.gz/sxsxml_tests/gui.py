# noinspection PyPackageRequirements
from PyQt5.QtWebEngineWidgets import QWebEngineView

import sxsxml
import re
import sys
import mhelper_qt as qt

from sxsxml_tests import case_parser


class FrmMain( qt.QMainWindow ):
    def __init__( self ):
        super().__init__()
        
        self.lst_inputs = qt.QListWidget()
        self.lst_inputs.itemDoubleClicked.connect( self.itemDoubleClicked )
        self.fra_input = qt.QFrame()
        self.lay_input = qt.QVBoxLayout()
        self.txt_input = qt.QTextEdit()
        self.btn_input = qt.QPushButton()
        self.btn_input.setText( "Render" )
        self.btn_input.clicked.connect( self.clicked )
        self.cmb_input = qt.QComboBox()
        self.cmb_input.addItems( ["ansi", "html", "html+"] )
        self.txt_output = QWebEngineView()
        self.spt_main = qt.QSplitter()
        
        self.spt_main.addWidget( self.lst_inputs )
        self.spt_main.addWidget( self.fra_input )
        self.spt_main.addWidget( self.txt_output )
        
        self.fra_input.setLayout( self.lay_input )
        self.lay_input.addWidget( self.txt_input )
        self.lay_input.addWidget( self.cmb_input )
        self.lay_input.addWidget( self.btn_input )
        
        self.setCentralWidget( self.spt_main )
        
        self.cases = { }
        
        for name, hash, content in case_parser.get_cases( "" ):
            item = qt.QListWidgetItem()
            item.setText( name )
            self.lst_inputs.addItem( item )
            self.cases[name] = "\n".join( content )
    
    
    def itemDoubleClicked( self, item ):
        self.txt_input.setPlainText( self.cases[item.text()] )
    
    
    def clicked( self ):
        rx = re.compile("\033\[[0-9]+m")
        i = self.cmb_input.currentIndex()
        op = []
        
        if i == 0:
            o = sxsxml.SxsAnsiWriter( op.append )
        elif i == 1:
            o = sxsxml.SxsHtmlWriter( op.append, scripted = False )
        elif i == 2:
            o = sxsxml.SxsHtmlWriter( op.append )
        else:
            raise ValueError( "No selection" )
        
        o.write( self.txt_input.toPlainText() )
        
        txt = "\n".join( op )
        
        if i == 0:
            sys.__stderr__.write( txt )
            txt = rx.sub("␛", txt)
            txt = txt.replace( "<", "&lt;" )
            txt = txt.replace( ">", "&gt;" )
            txt = txt.replace( "\033", "␛" )
            txt = txt.replace( "\n", "↲<br/>" )
            txt = txt.replace( "\r", "↞<br/>" )
            txt = txt.replace( " ", "␠" )
            txt = "<code>{}</code>".format( txt )
        
        txt = "<html><head><style>{}</style></head><body>{}</body></html>".format( sxsxml.SxsHtmlWriter.BASIC_CSS, txt )
        
        self.txt_output.setHtml( txt )


def launch():
    application = qt.QApplication( sys.argv )
    window = FrmMain()
    window.show()
    application.exec_()
