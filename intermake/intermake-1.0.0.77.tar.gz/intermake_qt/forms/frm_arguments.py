from typing import Optional, Dict, Tuple

from PyQt5.QtWidgets import QDialog, QWidget

from editorium import EditoriumGrid
import intermake as im
from intermake_qt.extensions.gui_controller import GuiController
from intermake_qt.forms.designer.frm_arguments_designer import Ui_Dialog
from intermake_qt.utilities import formatting, gui_command_options
from mhelper import ArgValueCollection, ArgsKwargs, safe_cast
import mhelper_qt as qt
import editorium


class FrmArguments( QDialog ):
    def __init__( self, parent: QWidget, editorium: editorium.Editorium, command: im.Command, defaults: ArgsKwargs, title: str ) -> None:
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        
        self.ui = Ui_Dialog( self )
        self.title = title or formatting.get_nice_name( command.name )
        self.setWindowTitle( "{} - {}".format( parent.windowTitle(), self.title ) )
        
        self.__command = command
        
        self.result: ArgValueCollection = None
        
        self.values = ArgValueCollection( command.args, read = defaults )
        self.editorium_grid = EditoriumGrid( grid = self.ui.GRID_ARGS,
                                             editorium = editorium,
                                             targets = (self.values,),
                                             fn_description = lambda x: x.description.replace( "|app_name|", im.Controller.ACTIVE.app.name ),
                                             fn_name = lambda x: formatting.get_nice_name( x.name ) )
        self.editorium_grid.create_help_button( self.__command.documentation, self.ui.BTN_HELP_MAIN )
        
        self.__init_controls()
        
        self.ui.LBL_APP_NAME.setText( im.Controller.ACTIVE.app.name )
    
    
    @property
    def options( self ):
        controller: GuiController = safe_cast( "im.Controller.ACTIVE", im.Controller.ACTIVE, GuiController )
        return controller.gui_settings
    
    
    def __init_controls( self ):
        self.ui.LBL_PLUGIN_NAME.setText( self.title )
        self.editorium_grid.mode = EditoriumGrid.Layouts.INLINE_HELP if self.options.inline_help else EditoriumGrid.Layouts.NORMAL
        self.editorium_grid.recreate()
        
        if self.editorium_grid.editor_count == 0:
            label = qt.QLabel()
            label.setText( "There are no user-configurable arguments for this command." )
            label.setSizePolicy( qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed )
            label.setEnabled( False )
            self.editorium_grid.grid.addWidget( label, 0, 0 )
            self.editorium_grid.grid.update()
    
    
    @staticmethod
    def query( owner_window: QWidget, editorium: editorium.Editorium, command: im.Command, defaults: ArgsKwargs = None, title: str = None ) -> Optional[ArgValueCollection]:
        """
        As `request` but the command is not run when the form closes.
        """
        if defaults is None:
            defaults = ArgsKwargs()
        
        form = FrmArguments( owner_window, editorium, command, defaults, title )
        
        if form.exec_():
            return form.result
        else:
            return None
    
    
    @qt.exqtSlot()
    def on_pushButton_clicked( self ) -> None:
        """
        Signal handler:
        """
        
        try:
            self.editorium_grid.commit()
            incomplete = self.values.get_incomplete()
            
            if incomplete:
                raise ValueError( "The following arguments have not been provided:\n{}".format( "\n".join( [("    * " + x) for x in incomplete] ) ) )
            
            self.result = self.values
            
            self.accept()
        except Exception as ex:
            qt.show_exception( self, "Error", ex )
            return
    
    
    @qt.exqtSlot()
    def on_BTN_OPTIONS_clicked( self ) -> None:
        """
        Signal handler:
        """
        inline_help = self.options.inline_help
        
        gui_command_options.show_menu( self, self.__command )
        
        if inline_help != self.options.inline_help:
            self.editorium_grid.commit()
            self.__init_controls()
    
    
    def mk_act( self, name: str, acts: Dict[qt.QAction, Tuple[str, str]], menu: qt.QMenu, state: str ):
        a = qt.QAction()
        a.setText( state )
        acts[a] = name, state
        menu.addAction( a )
    
    
    @qt.exqtSlot()
    def on_BTN_HELP_MAIN_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
