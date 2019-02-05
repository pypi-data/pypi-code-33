"""
Main window for GUI
"""

from typing import cast

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QMainWindow, QMessageBox, QScrollArea, QSizePolicy, QSpacerItem, QToolButton

import intermake
from intermake_qt.utilities.interfaces import IGuiMainWindow
from intermake_qt.extensions.gui_controller import GuiController
from intermake_qt.forms.designer.resource_files import resources_rc
from intermake_qt.utilities import formatting
from mhelper import string_helper
from mhelper_qt import exceptToGui, exqtSlot


cast( None, resources_rc )

__author__ = "Martin Rusilowicz"


# noinspection PyAbstractClass


class FrmIntermakeMain( QMainWindow, IGuiMainWindow ):
    """
    Main window
    """
    
    
    def __init__( self, *, app: intermake.Application, controller: GuiController, can_return_to_cli: bool, parent = None ):
        """
        CONSTRUCTOR
        """
        #
        # QT stuff
        #
        QMainWindow.__init__( self, parent )
        
        #
        # My flags
        #
        self.__controller = controller
        self.__ever_in_cli = can_return_to_cli
        self.__return_to_console = False
        
        # UI
        self.setWindowTitle( app.name + " " + app.version )
        
        self.views = []
        
        last_folder = None
        
        # Frame
        scr = QScrollArea()
        self.setCentralWidget( scr )
        scr.setWidgetResizable( True )
        
        frame = QFrame()
        frame.setProperty( "style", "contents" )
        scr.setWidget( frame )
        layout = QGridLayout()
        frame.setLayout( layout )
        col = 0
        row = 0
        NUM_COLS = 5
        
        for command in sorted( (x for x in app.commands if x.visibility_class.is_visible), key = lambda x: x.folder + "/" + x.name ):
            command: intermake.Command = command
            
            if command.folder != last_folder:
                last_folder = command.folder
                label = QLabel()
                label.setText( formatting.get_nice_name( command.folder ) )
                label.setProperty( "style", "heading" )
                row += 1
                col = 0
                layout.addWidget( label, row, col, 1, NUM_COLS )
                row += 1
            
            if col >= NUM_COLS:
                col = 0
                row += 1
            
            btn = QToolButton()
            btn.setProperty( "style", "listbutton" )
            btn.setStyleSheet( "font-size: 16px;" )
            btn.setText( formatting.get_nice_name( command.name ) )
            btn.setToolTip( string_helper.first_line( command.documentation.strip() ) )
            btn.clicked.connect( self.handle_button_clicked )
            # btn.setIcon( resources.command.icon() )
            setattr( btn, "TAG_command", command )
            layout.addWidget( btn, row, col )
            col += 1
        
        col = 0
        row += 1
        layout.addItem( QSpacerItem( 1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding ), row, col )
        layout.addItem( QSpacerItem( 1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum ), row, NUM_COLS )
    
    
    def closeEvent( self, event: QCloseEvent ):
        if self.__ever_in_cli:
            q = QMessageBox.question( self, "Close", "You have closed the GUI. Do you wish to return to the CLI?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel )
            
            if q == QMessageBox.Cancel:
                event.ignore()
                return
            elif q == QMessageBox.Yes:
                self.__return_to_console = True
            else:
                self.__return_to_console = False
    
    
    @exqtSlot()
    def on_ACTION_HELP_ABOUT_triggered( self ) -> None:
        """
        Signal handler: Help -> About
        """
        msg = QMessageBox( self )
        msg.setIcon( QMessageBox.Information )
        msg.setText( "fasta.explorer" )
        msg.setInformativeText( "Version 1" )
        msg.exec_()
    
    
    @exceptToGui()
    def handle_button_clicked( self, _ ) -> None:
        src = self.sender()
        command = getattr( src, "TAG_command" )
        self.__controller.acquire( command, window = self, confirm = True ).run()
    
    
    def command_completed( self, result: intermake.Result ):
        """
        An `Command` has finished - results have been received!
        """
        self.statusBar().showMessage( "(COMMAND COMPLETED) " + str( result ) )
    
    
    def return_to_console( self ):
        return self.__return_to_console


def show_basic_window( parent ):
    """
    Shows the Intermake basic window (as a dialogue rather than as a main window).
    """
    from intermake_qt.extensions.gui_controller import GuiController
    controller: GuiController = intermake.Controller.ACTIVE
    
    assert isinstance( intermake.Controller.ACTIVE, GuiController ), intermake.Controller.ACTIVE
    
    frm: FrmIntermakeMain = FrmIntermakeMain( app = intermake.Controller.ACTIVE.app,
                                              controller = intermake.Controller.ACTIVE,
                                              can_return_to_cli = False,
                                              parent = parent )
    
    orig = controller.owner_window
    controller.owner_window = frm
    frm.setWindowModality( Qt.ApplicationModal )
    frm.show()
    controller.owner_window = orig
