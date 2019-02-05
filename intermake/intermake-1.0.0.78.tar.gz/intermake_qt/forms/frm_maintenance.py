from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QGuiApplication
from PyQt5.QtWidgets import QDialog, QWidget, QScrollBar
from typing import cast

from intermake_qt.utilities import formatting, gui_command_options
from mhelper_qt.qt_gui_helper import exqtSlot

import time
import pyperclip
import intermake
import sxsxml

from intermake_qt.forms.designer.frm_maintenance_designer import Ui_Dialog
from intermake_qt.forms.designer.resource_files import resources_rc


__author__ = "Martin Rusilowicz"

cast( None, resources_rc )


class FrmMaintenance( QDialog ):
    """
    This is the "please wait" form that shows when a plugin is running.
    """
    
    
    class FinishedParcel:
        def __init__( self, asr, result, exception, traceback, messages ):
            self.asr = asr
            self.result = result
            self.exception = exception
            self.traceback = traceback
            self.messages = messages
    
    
    def __init__( self, parent: QWidget, command: intermake.Command, auto_close: bool ):
        """
        CONSTRUCTOR
        """
        from intermake_qt.extensions.gui_controller import GuiController
        
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        
        ui = cast( GuiController, intermake.Controller.ACTIVE )
        
        # Set our properties
        self.__command = command
        self.__was_cancelled = False
        self.__prefer_auto_close = auto_close
        self.__auto_close_success = ui.gui_settings.read( command, "auto_close_on_success", auto_close )
        self.__auto_close_failure = ui.gui_settings.read( command, "auto_close_on_failure", auto_close )
        self.__auto_scroll_messages = ui.gui_settings.read( command, "auto_scroll_messages", True )
        self.__finished: FrmMaintenance.FinishedParcel = None
        self.__needs_raise = True
        self.__maximise_progress = False
        self.__maximise_output = False
        self.__has_text_messages = False
        self.__start_time = time.time()
        self.__message_formatter = sxsxml.SxsHtmlWriter( self.__handle_message_formatted, scripted = False )
        self.__html = ["<style>" + sxsxml.SxsHtmlWriter.BASIC_CSS + "</style>"]
        self.__bars = { }
        
        # Set up the window
        self.setWindowTitle( formatting.get_nice_name( command.name ) )
        self.setWindowFlags( Qt.Dialog | Qt.Desktop )
        
        # Hide the close button until the command completes
        self.ui.BTN_CLOSE.setVisible( False )
        
        # Show the "please wait" screen until a message is received
        self.ui.PAGER_MAIN.setCurrentIndex( 0 )
    
    
    def handle_message_from_worker( self, info: str ):
        #
        # Add our message to the textbox
        #
        self.__message_formatter.write( info )  # --> __handle_message_formatted
    
    
    def handle_was_cancelled( self ) -> bool:
        return self.__was_cancelled
    
    
    def handle_worker_finished( self, async_result: intermake.Result, result, exception, traceback, messages ):
        #
        # Hold ctrl to prevent auto-close
        #
        keyboard = QGuiApplication.queryKeyboardModifiers()
        
        self.ui.PAGER_MAIN.setCurrentIndex( 1 )
        self.__finished = self.FinishedParcel( async_result, result, exception, traceback, messages )
        
        if exception is not None:
            self.handle_message_from_worker( "Command finished with errors:\n" )
            self.handle_message_from_worker( "<error>{}</error>".format( intermake.pr.escape( exception ) ) )
            # self.handle_message_from_worker( "<traceback>{}</traceback>".format(  intermake.pr.escape( traceback) ) )
            auto_close = self.__auto_close_failure
        else:
            auto_close = self.__auto_close_success
        
        if (keyboard & Qt.ControlModifier) == Qt.ControlModifier:
            auto_close = False
        
        if auto_close:
            self.close()
        else:
            if exception is not None:
                self.handle_message_from_worker( "<system>Your query has completed with errors. You may now close the dialogue.</system>" )
            else:
                self.handle_message_from_worker( "<system>Your query has completed. You may now close the dialogue.</system>" )
            
            self.ui.BTN_CANCEL.setVisible( False )
            self.ui.BTN_CLOSE.setVisible( True )
    
    
    def __handle_message_formatted( self, html: str ):
        #
        # Process progress bars separately
        #
        proggy = self.__handle_progress_bar( html )
        
        if not proggy:
            #
            # Standard HTML - just add it
            #
            self.__html.append( html )
        
        #
        # Update the HTML and scroll into view
        #
        self.ui.TXT_MESSAGES.setHtml( "".join( self.__html ) )
        v: QScrollBar = self.ui.TXT_MESSAGES.verticalScrollBar()
        v.setValue( v.maximum() )
        
        # First message specials
        if self.__needs_raise:
            # Switch to page 1
            self.ui.PAGER_MAIN.setCurrentIndex( 1 )
            
            # Bring the window to the top
            self.activateWindow()
            self.raise_()
            self.__needs_raise = False
    
    
    def __handle_progress_bar( self, html: str ):
        if not html.startswith( sxsxml.SxsHtmlWriter.PROGRESS_PREFIX ):
            return False
        
        html = html[len( sxsxml.SxsHtmlWriter.PROGRESS_PREFIX ):]
        prog, html = html.split( sxsxml.SxsHtmlWriter.PROGRESS_SUFFIX, 1 )
        new, end, id = prog.split( " " )
        html += "<br/>"
        
        if int( new ):
            self.__bars[id] = len( self.__html )
            self.__html.append( html )
        else:
            self.__html[self.__bars[id]] = html
        
        if int( end ):
            del self.__bars[id]
        
        return True
    
    
    def closeEvent( self, event: QCloseEvent ):
        if self.__finished is None:
            event.ignore()
        else:
            # TODO: This fires the callback NOW, ideally we want to do it AFTER the window has fully closed
            f = self.__finished
            
            if f.exception:
                f.asr.set_error( f.exception, f.traceback, f.messages )
            else:
                f.asr.set_result( f.result, f.messages )
    
    
    @exqtSlot()
    def on_BTN_CANCEL_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.handle_message_from_worker( "~~ Cancel requested ~~ - The process will stop during the next iteration" )
        self.ui.BTN_CANCEL.setVisible( False )
        self.__was_cancelled = True
    
    
    @exqtSlot()
    def on_BTN_CLOSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        pyperclip.copy( "\n".join( self.__html ) )
        self.close()
    
    
    @exqtSlot()
    def on_BTN_OPTIONS_clicked( self ) -> None:
        """
        Signal handler:
        """
        gui_command_options.show_menu( self, self.__command )
