from typing import Callable, List, Optional, Sequence, Tuple, Union

import mhelper_qt as qt
from mhelper import Coords, ArgValueCollection, NOT_PROVIDED, ResourceIcon, array_helper, exception_helper, AnnotationInspector, ArgInspector

import editorium as _editorium


_BUTTON_HELP_TAG = "TAG_button_help"


class EditoriumGridCreator:
    def __init__( self, owner: "EditoriumGrid", target: ArgValueCollection, plugin_arg: ArgInspector, coords: Coords ) -> None:
        exception_helper.safe_cast( "target", target, ArgValueCollection )
        exception_helper.safe_cast( "plugin_arg", plugin_arg, ArgInspector )
        
        self.__owner: EditoriumGrid = owner
        self.target = target
        self.arg = plugin_arg
        self.coords = coords
    
    
    def create_help_label( self ) -> qt.QLabel:
        """
        A class method that creates a `QWidget` with the specified `help_text`.
        Also sets the `toolTip` and `whatsThis` text on any specified `controls` to the `help_text`.
        :return: The created `QWidget`
        """
        html = self.get_description()
        
        help_label = qt.QLabel()
        help_label.setProperty( "theme", "helpbox" )
        help_label.setWordWrap( True )
        help_label.setSizePolicy( qt.QSizePolicy.Expanding, qt.QSizePolicy.Preferred )
        help_label.setText( html )
        help_label.setWhatsThis( html )
        
        return help_label
    
    
    def get_name( self ):
        return self.__owner._get_name( self.arg )
    
    
    @property
    def grid( self ) -> qt.QGridLayout:
        return self.__owner.grid
    
    
    def apply_tooltips( self, *controls ) -> None:
        html = self.get_description()
        
        for control in controls:
            control.setToolTip( html )
            control.setWhatsThis( html )
    
    
    def create_help_button( self ) -> qt.QPushButton:
        return self.__owner.create_help_button( self.arg )
    
    
    def get_description( self ) -> str:
        return self.__owner._get_description( self.arg )
    
    
    def create_editor( self ) -> qt.QWidget:
        value = self.target.get_value( self.arg )
        
        messages = _editorium.EditMessages()
        self.__owner.mode.on_get_messages( messages )
        
        editor = self.__owner.editorium.get_editor( self.arg.annotation.value, messages = messages )
        editor.editor.setSizePolicy( qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum )
        
        if value is NOT_PROVIDED:
            value = self.arg.default
        
        if value is NOT_PROVIDED:
            value = None
        
        editor.set_value( value )
        
        self.__owner.editors.append( (self.target, self.arg, editor) )
        return editor.editor
    
    
    def create_name_label( self ) -> qt.QLabel:
        label = qt.QLabel()
        label.setText( self.get_name() )
        label.setWhatsThis( self.get_description() )
        return label


class AbstractEditoriumGridLayout:
    def on_get_messages( self, m: _editorium.EditMessages ):
        pass
    
    
    def on_create( self, e: EditoriumGridCreator ):
        raise NotImplementedError( "abstract" )


class _InlineHelpLayout( AbstractEditoriumGridLayout ):
    def on_get_messages( self, m: _editorium.EditMessages ):
        m.boolean_display = _editorium.EBoolDisplay.RADIO_BUTTONS
    
    
    def on_create( self, e: EditoriumGridCreator ):
        # Groupbox
        parameter_groupbox = qt.QGroupBox()
        parameter_groupbox.setTitle( e.get_name() )
        parameter_groupbox.setMaximumWidth( 768 )
        parameter_groupbox.setSizePolicy( qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum )
        parameter_groupbox.setWhatsThis( str( e.arg.annotation ) )
        
        # Layout
        parameter_layout = qt.QVBoxLayout()
        parameter_groupbox.setLayout( parameter_layout )
        
        # Position
        e.grid.addWidget( parameter_groupbox, e.coords.row, e.coords.col )
        e.coords.row += 1
        
        # Help label
        help_widget = e.create_help_label()
        parameter_layout.addWidget( help_widget )
        editor = e.create_editor()
        
        # Tooltips
        e.apply_tooltips( parameter_groupbox )
        
        parameter_layout.addWidget( editor )


class _CompactLayout( AbstractEditoriumGridLayout ):
    def on_get_messages( self, m: _editorium.EditMessages ):
        m.keep_left = True
    
    
    def on_create( self, e: EditoriumGridCreator ):
        # Help button
        button = e.create_help_button()
        e.grid.addWidget( button, e.coords.row, e.coords.col + 1 )
        
        # Name label
        label = e.create_name_label()
        e.grid.addWidget( label, e.coords.row, e.coords.col + 0 )
        
        # Input
        editor = e.create_editor()
        e.grid.addWidget( editor, e.coords.row, e.coords.col + 2 )
        
        # Tooltips
        e.apply_tooltips( label, editor )
        
        e.coords.row += 1


class _NormalLayout( AbstractEditoriumGridLayout ):
    def on_get_messages( self, m: _editorium.EditMessages ):
        m.keep_left = True
        m.boolean_display = _editorium.EBoolDisplay.COMBOBOX
        m.boolean_texts = "Yes", "No", "Unspecified"
        m.show_text = "Specify:", "Specify:"
    
    
    def on_create( self, e: EditoriumGridCreator ):
        layout = qt.QHBoxLayout()
        layout.setContentsMargins( 0, 0, 0, 0 )
        
        label = e.create_name_label()
        layout.addWidget( label )
        
        help = e.create_help_button()
        layout.addWidget( help )
        
        e.grid.addLayout( layout, e.coords.row, e.coords.col )
        e.coords.row += 1
        
        editor = e.create_editor()
        e.grid.addWidget( editor, e.coords.row, e.coords.col )
        e.coords.row += 1
        
        spacer = qt.QSpacerItem( 8, 8, qt.QSizePolicy.Maximum, qt.QSizePolicy.Maximum )
        e.grid.addItem( spacer )
        e.coords.row += 1
        
        # Tooltips
        e.apply_tooltips( label, editor )


class EditoriumGrid:
    """
    Populates a QGridLayout with a set of controls inferred from the data-types and
    annotations on the objects which they are to edit.
    
    Usage:
        * Construct the object with the appropriate parameters
        * Call `recreate` to create the controls
        * Parameters can be changed again post-construction, call `recreate` to recreate the controls
    """
    ansi_theme = qt.qt_gui_helper.ansi_scheme_light( bg = "#00000000", fg = "#000000" )
    
    
    class Layouts:
        NORMAL = _NormalLayout()
        COMPACT = _CompactLayout()
        INLINE_HELP = _InlineHelpLayout()
        _DEFAULT = NORMAL
    
    
    def __init__( self,
                  grid: Union[qt.QGridLayout, qt.QWidget],
                  editorium : _editorium.Editorium,
                  targets: Optional[Sequence[ArgValueCollection]] = (),
                  mode: AbstractEditoriumGridLayout = None,
                  fn_description: Callable[[ArgInspector], str] = None,
                  fn_name: Callable[[ArgInspector], str] = None, ):
        """
        CONSTRUCTOR
        
        :param grid:            Either a `QGridLayout` to bind to or a control to create the `QGridLayout` within. 
        :param targets:         Targets to create query for 
        :param mode:            Layout mode override.
                                You can define your own `AbstractEditoriumGridLayout` or specify one of the inbuilt `EditoriumGrid.Layouts.*`.
        :param fn_description:  How to obtain descriptions (by default `ArgInspector.description`) 
        """
        if not isinstance( grid, qt.QGridLayout ):
            grid_ = qt.QGridLayout()
            grid.setLayout( grid_ )
            grid = grid_
        
        self.grid: qt.QGridLayout = grid
        self.targets: Sequence[ArgValueCollection] = targets
        self.mode = mode if mode is not None else self.Layouts._DEFAULT
        self.fn_description = fn_description
        self.fn_name = fn_name
        self.fn_arg = None
        self.editors: List[Tuple[ArgValueCollection, ArgInspector, _editorium.AbstractEditor]] = []
        self.editorium = editorium
        
        grid.setSpacing( 0 )
        
        w: qt.QWidget = grid.parentWidget()
        w.setStyleSheet( "QToolTip { font-size: 14px; background: white; color: black; border: 2px solid gray; }" )
    
    
    @property
    def editor_count( self ) -> int:
        return len( self.editors )
    
    
    @property
    def target( self ) -> ArgValueCollection:
        """
        Gets the `ArgValueCollection` to use as the target.
        Attempting to retrieve this value when there are multiple targets results in an error.
        If the `targets` array is empty, `None` is returned.
        """
        return array_helper.single( self.targets, empty = None )
    
    
    @target.setter
    def target( self, value: ArgValueCollection ):
        """
        Sets the `ArgValueCollection` to use as the target.
        If you wish to set multiple targets, set the `targets` field instead.
        Setting this property to `None` clears the `targets` array.
        You must call `recreate` to reflect any changes made.
        """
        if value is None:
            self.targets = ()
        else:
            self.targets = (value,)
    
    
    def recreate( self ):
        qt.layout_helper.delete_children( self.grid )
        self.editors.clear()
        
        coords = Coords( 0, 0 )
        
        for target in self.targets:
            for arg in target:
                if self.fn_arg is not None:
                    arg: ArgInspector = self.fn_arg( arg )
                
                if arg is None:
                    continue
                
                e = EditoriumGridCreator( self, target, arg, coords )
                self.mode.on_create( e )
        
        if self.editor_count:
            self.grid.addItem( qt.QSpacerItem( 1, 1, qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding ) )
    
    
    def commit( self, check: bool = True ) -> List[ArgValueCollection]:
        """
        Commits the changes and returns the modified value collection.
        
        :param check: When `False`, no errors are raised for bad values.
        """
        r = []
        
        for target, plugin_arg, value_fn in self.editors:
            if target not in r:
                r.append( target )
            
            try:
                target.set_value( plugin_arg, value_fn.get_value() )
            except Exception as ex:
                if check:
                    raise ValueError( "The value of the argument «{}» is invalid: ".format( plugin_arg.name ) + str( ex ) ) from ex
        
        return r
    
    
    def create_help_button( self, arg: Union[str, ArgInspector, None] = None, button: Optional[qt.QPushButton] = None ) -> qt.QPushButton:
        """
        Creates (or stylises and handles) a help button.
        
        :param arg:         Argument to provide help for.
                            This does not need to be a real argument. 
        :param button:      Button to stylise, or `None` to create a new button.
        :return:            The button. 
        """
        button = button or qt.QPushButton()
        button.setFlat( True )
        button.setIcon( ResourceIcon( "help" ).icon() )
        button.setIconSize( qt.QSize( 16, 16 ) )
        button.setText( "" )
        button.setMaximumSize( 24, 24 )
        if isinstance( arg, AnnotationInspector ):
            button.setToolTip( "Click to show help for the '{}' argument.".format( arg.name ) )
        elif arg is not None:
            button.setToolTip( "Click to show more information." )
        
        if arg is not None:
            button.setWhatsThis( button.toolTip() )
            button.clicked.connect( self.__on_help_button_clicked )
            setattr( button, _BUTTON_HELP_TAG, arg )
        return button
    
    
    def __on_help_button_clicked( self, _: object ):
        button: qt.QPushButton = self.grid.sender()
        arg: ArgInspector = getattr( button, _BUTTON_HELP_TAG )
        
        if isinstance( arg, ArgInspector ):
            html = self._get_description( arg )
            if arg.annotation.value is not None:
                details = ("Name: '{}'\n"
                           "Type: '{}'\n"
                           "Default: '{}'"
                           .format( arg.name, arg.annotation, arg.default ))
            else:
                details = None
        else:
            html = self.__format_help_text( arg )
            details = None
        
        qt.FrmGenericText.request( parent = button.window(),
                                   text = html,
                                   details = details )
    
    
    def _get_description( self, arg: ArgInspector ) -> str:
        if self.fn_description:
            help_text = self.fn_description( arg )
        else:
            help_text = arg.description
        
        return self.__format_help_text( help_text )
    
    
    def __format_help_text( self, help_text ):
        help_text = help_text.strip()
        html = qt.qt_gui_helper.ansi_to_html( help_text, lookup = self.ansi_theme )
        return html
    
    
    def _get_name( self, arg ) -> str:
        if self.fn_name is None:
            return arg.name
        else:
            return self.fn_name( arg )
