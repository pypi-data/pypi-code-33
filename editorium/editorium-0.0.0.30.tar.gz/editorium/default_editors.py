import sip
from typing import Dict, Iterable, List, Optional, Sequence, cast, Tuple

import stringcoercion
from editorium.bases import AbstractEditor, EditorInfo, EBoolDisplay
# noinspection PyPackageRequirements
from flags import Flags
from mhelper import EFileMode, isFilename, isReadonly, SwitchError, abstract, ignore, override, sealed, virtual, isPassword, array_helper, exception_helper, isDirname, AnnotationInspector, Documentation, markdown_helper
import mhelper_qt as qt
from stringcoercion import AbstractEnumCoercer


def __combine( x: Dict[Flags, qt.QCheckBox] ) -> Flags:
    t = next( iter( x.keys() ) )
    # noinspection PyUnresolvedReferences
    value = t.__no_flags__
    
    for k, v in x:
        if v.isChecked():
            value |= k
    
    return value


class NullableEditor( AbstractEditor ):
    """
    Edits: Optional[T] (as a fallback for editors of `T` not supporting `None` as an option)
    """
    
    
    @classmethod
    def on_get_priority( cls ) -> int:
        # Anything that handles optionals itself should go first
        return cls.Priority.LOW
    
    
    def __init__( self, info: EditorInfo ):
        # Read the options
        self.option_hide = info.messages.hide
        self.option_show_text, self.option_hide_text = info.messages.hide_text
        self.option_align_left = self.option_hide and info.messages.keep_left
        
        # Editor and checkbox live in a frame
        layout = qt.QVBoxLayout()
        layout.setContentsMargins( qt.QMargins( 0, 0, 0, 0 ) )
        self.editor = qt.QFrame()
        self.editor.setLayout( layout )
        
        # Create the checkbox
        self.checkbox = qt.QCheckBox()
        self.checkbox.stateChanged[int].connect( self.__on_checkbox_toggled )
        self.checkbox.setSizePolicy( qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed )
        self.checkbox.setText( "(TEXT GOES HERE)" )
        
        layout.addWidget( self.checkbox )
        
        # Create the sub-editor
        underlying_type = info.annotation.optional_value
        self.sub_editor = info.editorium.get_editor( underlying_type, messages = info.messages )
        self.sub_editor.editor.setSizePolicy( qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed )
        layout.addWidget( self.sub_editor.editor )
        
        # Left align everything? 
        if self.option_align_left:
            self.non_editor = qt.QLabel()  # use a label so we can hide it
            self.non_editor.setText( "" )
            self.non_editor.setSizePolicy( qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed )
            layout.addWidget( self.non_editor )
        
        # Update the display
        self.__on_checkbox_toggled( self.checkbox.isChecked() )
        
        # Call the base class
        super().__init__( info, self.editor )
    
    
    @qt.exceptToGui()
    def __on_checkbox_toggled( self, _: int ):
        state = self.checkbox.checkState() == qt.Qt.Checked
        
        if self.option_hide:
            self.sub_editor.editor.setVisible( state )
        else:
            self.sub_editor.editor.setEnabled( state )
        
        if self.option_align_left:
            self.non_editor.setVisible( not state )
        
        if state:
            self.checkbox.setText( self.option_show_text )
        else:
            self.checkbox.setText( self.option_hide_text )
    
    
    def on_get_value( self ) -> Optional[object]:
        if self.checkbox.isChecked():
            return self.sub_editor.get_value()
        else:
            return None
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_optional
    
    
    def on_set_value( self, value: Optional[object] ) -> None:
        self.checkbox.setChecked( value is not None )
        self.__on_checkbox_toggled( self.checkbox.isChecked() )
        
        if value is not None:
            self.sub_editor.set_value( value )


class StringEditor( AbstractEditor ):
    """
    Edits: str
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = qt.QLineEdit()
        
        super().handle_changes( self.editor.textChanged[str] )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ):
        return info.annotation.is_direct_subclass_of( str )
    
    
    def on_set_value( self, value: str ):
        if value is None:
            value = ""
        
        exception_helper.safe_cast( "value", value, str )
        self.editor.setText( value )
    
    
    def on_get_value( self ) -> str:
        return self.editor.text()


class PasswordEditor( AbstractEditor ):
    """
    Edits: Password
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = qt.QLineEdit()
        self.editor.setEchoMode( qt.QLineEdit.Password )
        super().handle_changes( self.editor.textChanged[str] )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ):
        return info.annotation.is_mannotation_of( isPassword )
    
    
    def on_set_value( self, value: str ):
        if value is None:
            value = ""
        
        self.editor.setText( value )
    
    
    def on_get_value( self ) -> str:
        return self.editor.text()
    
    
    @classmethod
    def on_get_priority( cls ):
        return cls.Priority.HIGH


class AnnotationEditor( AbstractEditor ):
    @classmethod
    def on_get_priority( cls ) -> int:
        # We're pulling out annotations, so make way for anything else, apart from the fallback
        return cls.Priority.LAST
    
    
    def __init__( self, info: EditorInfo ):
        self.delegate = info.editorium.get_editor( info.annotation.mannotation_arg, messages = info.messages )
        
        super().__init__( info, self.delegate.editor )
    
    
    def on_set_value( self, value: Optional[object] ):
        self.delegate.set_value( value )
    
    
    def on_get_value( self ) -> Optional[object]:
        return self.delegate.get_value()
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_mannotation


class ListTEditor( AbstractEditor ):
    """
    Edits: `Sequence[T]`
    
    (Always outputs as `List[T]`)
    """
    
    
    @classmethod
    def on_get_priority( cls ) -> int:
        # We're handling generic lists, so make way for something more specific
        return cls.Priority.LOW
    
    
    def __init__( self, info: EditorInfo ):
        self.list_type: type = info.annotation.generic_arg
        
        self.layout = qt.QGridLayout()
        self.layout.setContentsMargins( qt.QMargins( 0, 0, 0, 0 ) )
        
        self.label = qt.QLabel()
        self.label.setText( "Item count" )
        self.layout.addWidget( self.label, 0, 0 )
        
        self.spinner = qt.QSpinBox()
        self.spinner.setValue( 0 )
        self.spinner.valueChanged.connect( self.__valueChanged )
        self.spinner.setButtonSymbols( qt.QAbstractSpinBox.UpDownArrows )
        self.spinner.setSizePolicy( qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed )
        self.layout.addWidget( self.spinner, 0, 1 )
        
        self.editor = qt.QFrame()
        self.editor.setLayout( self.layout )
        
        self.editors: List[Tuple[qt.QLabel, AbstractEditor]] = []
        
        super().__init__( info, self.editor )
        
        # self.__add_editor()
    
    
    @qt.exceptToGui()
    def __valueChanged( self, num_editors: int ):
        while len( self.editors ) > num_editors:
            self.__remove_editor()
        
        while len( self.editors ) < num_editors:
            self.__add_editor()
    
    
    def __add_editor( self ) -> None:
        row = len( self.editors ) + 1
        label = qt.QLabel()
        label.setText( "Item {}.".format( row ) )
        self.layout.addWidget( label, row, 0 )
        
        editor: AbstractEditor = self.info.editorium.get_editor( self.list_type )
        self.layout.addWidget( editor.editor, row, 1 )
        
        self.editors.append( (label, editor) )
    
    
    def __remove_editor( self ) -> None:
        label, editor = self.editors.pop()
        self.layout.removeWidget( label )
        self.layout.removeWidget( editor.editor )
        sip.delete( label )
        sip.delete( editor.editor )
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_generic_sequence
    
    
    def on_set_value( self, value: Sequence[object] ) -> None:
        if value is None:
            value = []
        
        self.spinner.setValue( len( value ) )
        
        for i, x in enumerate( value ):
            label, editor = self.editors[i]
            editor.set_value( x )
    
    
    def on_get_value( self ) -> Sequence[object]:
        r = []
        
        for label, editor in self.editors:
            v = editor.get_value()
            r.append( v )
        
        return r


class FallbackEditor( AbstractEditor ):
    """
    Fallback editor that displays an error
    
    Edits: object
    """
    
    
    @classmethod
    def on_get_priority( cls ) -> int:
        # We're a last resort, so make way for anything else
        return cls.Priority.FALLBACK
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.value = None
        self.has_value = False
        self.editor = qt.QPushButton()
        self.editor.setStyleSheet( "QAbstractButton { padding: 4px; font-family: monospace; color: #202040; text-align: left; background: white; border: 1px outset silver; } QAbstractButton:hover { border: 1px outset blue; } QAbstractButton:pressed { border: 1px inset silver; } " )
        self.editor.setText( "(set)" )
        self.editor.clicked[bool].connect( self.on_clicked )
        super().__init__( info, self.editor )
    
    
    def on_clicked( self, _ ):
        window = self.editor.window()
        
        txt = qt.FrmGenericText.request( parent = window,
                                         message = "Specify suitable value of the type '{}'. Click 'details' for more information.".format( self.info.annotation ),
                                         editable = True,
                                         text = "",
                                         continuous = True,
                                         details = markdown_helper.markdown_to_html(
                                                 self.info.messages.coercers.get_descriptive_text( types = self.info.annotation.value ) ),
                                         test = lambda x: stringcoercion.coerce( self.info.annotation.value, x ) )
        
        if txt is None:
            return
        
        try:
            value = stringcoercion.coerce( self.info.annotation.value, txt )
        except Exception as ex:
            qt.show_exception( window, exception = ex )
            return
        
        self.value = value
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return True
    
    
    def on_set_value( self, value: object ) -> None:
        self.editor.setToolTip( repr( value ) )
        self.editor.setText( str( value ) )
        self.value = value
        self.has_value = True
    
    
    def on_get_value( self ) -> str:
        if not self.has_value:
            raise ValueError( "No value selected and no default value provided." )
        
        return self.value


class AbstractEnumEditor( AbstractEditor ):
    """
    Base class for enumerative edits (things with combo boxes)
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = qt.QComboBox()
        self.items: List[object] = self.get_options( info )
        
        if not array_helper.is_simple_sequence( self.items ):
            raise exception_helper.type_error( "self.get_options", self.items, Sequence )
        
        if info.annotation.is_optional:
            self.items: Sequence[object] = cast( List[object], [None] ) + self.items
        
        self.names: List[str] = [self.get_option_name( info, x ) for x in self.items]
        self.editor.setEditable( self.get_accepts_user_options() )
        self.editor.addItems( self.names )
        
        super().handle_changes( self.editor.currentTextChanged )
        
        super().__init__( info, self.editor )
        
        self.on_set_value( None )
    
    
    def get_accepts_user_options( self ) -> bool:
        return self.on_get_accepts_user_options()
    
    
    def on_get_accepts_user_options( self ) -> bool:
        return False
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        raise NotImplementedError( "still abstract" )
    
    
    def on_set_value( self, value: object ):
        if value is None:
            if not self.info.annotation.is_optional:
                self.editor.setCurrentIndex( 0 )
                return
        
        try:
            index = self.items.index( value )
        except ValueError:
            if self.editor.isEditable():
                self.editor.setCurrentText( self.get_option_name( self.info, value ) )
        else:
            self.editor.setCurrentIndex( index )
    
    
    def on_get_value( self ) -> object:
        if self.editor.currentIndex() == -1:
            raise ValueError( "A selection must be made." )
        
        index = self.editor.currentIndex()
        
        if self.get_option_name( self.info, self.items[index] ) == self.editor.currentText():
            return self.items[index]
        
        if self.editor.isEditable():
            return self.get_option_from_name( self.editor.currentText() )
    
    
    @virtual
    def get_option_from_name( self, text: str ):
        raise ValueError( "Not supported because `get_accepts_user_options` is not set" )
    
    
    @virtual
    def get_none_name( self, info: EditorInfo ) -> str:
        return info.messages.enum_none
    
    
    def get_options( self, info: EditorInfo ) -> List[object]:
        return array_helper.as_sequence( self.on_get_options( info ), cast = list )
    
    
    @abstract
    def on_get_options( self, info: EditorInfo ) -> Iterable[object]:
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def get_option_name( self, info: EditorInfo, item: object ) -> str:
        ignore( info )
        
        if item is None:
            return self.get_none_name()
        
        return str( item )


class StringCoercionEnumEditor( AbstractEnumEditor ):
    """
    Edits:  Anything handled by a `stringcoercion.AbstractEnumCoercer`.
            This includes enums.
    """
    
    
    @classmethod
    def on_get_priority( cls ) -> int:
        # We're handling generic enums, so make way for something more specific
        return cls.Priority.LOW - 1
    
    
    def __init__( self, info: EditorInfo ):
        x = self.__get_coercer( info )
        self.coercer_info: stringcoercion.CoercionInfo = x[0]
        self.coercer: AbstractEnumCoercer = x[1]
        super().__init__( info )
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return cls.__get_coercer( info ) is not None
    
    
    @classmethod
    def __get_coercer( cls, info: EditorInfo ) -> Optional[Tuple[stringcoercion.CoercionInfo, AbstractEnumCoercer]]:
        dc = info.messages.coercers
        an = AnnotationInspector( info.annotation.value_or_optional_value )
        ci = stringcoercion.CoercionInfo( an, dc, None )
        
        for coercer in dc:
            if isinstance( coercer, stringcoercion.AbstractEnumCoercer ):
                if coercer.can_handle( ci ):
                    return ci, coercer
        
        return None
    
    
    def on_get_accepts_user_options( self ):
        return self.coercer.get_accepts_user_options()
    
    
    def get_option_from_name( self, text: str ):
        return self.coercer.coerce( stringcoercion.CoercionInfo( self.info.annotation, None, text ) )
    
    
    def get_option_name( self, info: EditorInfo, item: object ):
        return self.coercer.get_option_name( item )
    
    
    def on_get_options( self, info: EditorInfo ) -> Iterable[object]:
        return self.coercer.get_options( self.coercer_info )


@abstract
class AbstractBrowserEditor( AbstractEditor ):
    """
    ABSTRACT CLASS
    
    Displays a text-box and button.
    
    The derived class should override the `@abstract` decorated methods, and optionally the `@virtual` ones, prefixed `on_`.
    """
    
    
    def __init__( self, info: EditorInfo ):
        """
        CONSTRUCTOR
        :param info:        As base class 
        """
        self.validated_value = None
        
        layout = qt.QHBoxLayout()
        layout.setContentsMargins( qt.QMargins( 0, 0, 0, 0 ) )
        
        editor = qt.QFrame()
        editor.setLayout( layout )
        
        self.line_edit = qt.QLineEdit()
        self.line_edit.setSizePolicy( qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed )
        self.line_edit.setPlaceholderText( "" )
        
        layout.addWidget( self.line_edit )
        
        edit_btn = qt.QToolButton()
        edit_btn.setText( "BROWSE" )
        edit_btn.clicked[bool].connect( self.__btn_clicked )
        layout.addWidget( edit_btn )
        
        if info.annotation.is_optional:
            clear_btn = qt.QToolButton()
            clear_btn.setText( "CLEAR" )
            clear_btn.clicked[bool].connect( self.__btn_clear_clicked )
            layout.addWidget( clear_btn )
        
        super().__init__( info, editor )
        
        self.on_set_value( None )
    
    
    @classmethod
    @abstract
    @override
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        """
        ABSTRACT - as base class.
        
        The derived class should:
        * Return a value according to the base class definition.
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def on_convert_from_text( self, text: str ) -> object:
        """
        Converts the specified object from text
        
        The derived class should:
        * Convert the text to its representative value.
        
        The default implementation returns the text, and is thus only suitable if the handled type is `str`-like.
        
        :param text:        Text, which is never empty or None.
        :return:            The object.
        :except ValueError: The derived class should raise a suitable and descriptive exception if conversion fails. 
        """
        return text
    
    
    @virtual
    def on_convert_to_text( self, value: object ) -> str:
        """
        Converts the specified object from text
        
        The derived class should:
        * Convert the value to a reversible string accurately representing it.
        
        The default implementation uses `__str__`.
        
        :param value:   A value, which is never `None`.
        """
        return str( value )
    
    
    @virtual
    def on_browse( self, value: Optional[object] ) -> Optional[str]:
        """
        Shows the browse dialogue.
        
        The derived class should:
        * Present the user with a browser displaying the available values.
        
        :param value:   The currently selected value, which may be `None` if the current selection is invalid. 
        :return:        The newly selected value, which may be `None` if the user cancels.
        """
        raise NotImplementedError( "abstract" )
    
    
    @sealed
    def on_set_value( self, value: Optional[object] ):
        if value is None:
            text = ""
        else:
            text = self.on_convert_to_text( value )
        
        self.line_edit.setText( text )
    
    
    @sealed
    def on_get_value( self ) -> Optional[object]:
        text = self.line_edit.text()
        
        if text == "":
            return None
        else:
            return self.on_convert_from_text( text )
    
    
    @qt.exceptToGui()
    def __btn_clear_clicked( self, _ ) -> None:
        self.on_set_value( None )
    
    
    @qt.exceptToGui()
    def __btn_clicked( self, _ ) -> None:
        text = self.line_edit.text()
        
        if text == "":
            value = None
        else:
            try:
                value = self.on_convert_from_text( text )
            except Exception:
                # ignore the exception, just cancel the section and move on
                value = None
        
        result = self.on_browse( value )
        
        if result is not None:
            self.on_set_value( result )


class FilenameEditor( AbstractBrowserEditor ):
    """
    Edits:  Filename[T, U] 
            Optional[Filename[T, U]]
    """
    
    
    def on_get_default_value( self ) -> object:
        return ""
    
    
    def on_convert_from_text( self, text ) -> Optional[str]:
        return text
    
    
    def on_convert_to_text( self, value: isFilename ) -> str:
        return cast( str, value )
    
    
    def __init__( self, info: EditorInfo ):
        super().__init__( info )
    
    
    def on_browse( self, value: isFilename ) -> str:
        d = qt.QFileDialog()
        
        if self.info.annotation.is_mannotation_of( isDirname ):
            d.setFileMode( qt.QFileDialog.Directory )
        else:
            t: isFilename = self.info.annotation.mannotation
            
            if t.extension is not None:
                d.setNameFilters( ["{} files (*{})".format( t.extension[1:].upper(), t.extension ), "All files (*.*)"] )
            
            if t.mode == EFileMode.READ:
                d.setFileMode( qt.QFileDialog.ExistingFile )
            else:
                d.setFileMode( qt.QFileDialog.AnyFile )
        
        d.selectFile( value )
        
        if d.exec_():
            file_name = d.selectedFiles()[0]
            return file_name
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_mannotation_of( isFilename ) or info.annotation.is_mannotation_of( isDirname )


class AbstractFlagsEditor( AbstractEditor ):
    PROPERTY_NAME = "Editor_EnumerativeMultiBase_Value"
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = qt.QFrame()
        layout = qt.QHBoxLayout()
        layout.setContentsMargins( qt.QMargins( 0, 0, 0, 0 ) )
        self.editor.setLayout( layout )
        self.items = list( self.get_items( info ) )
        control_lookup = { }
        self.sub_editors = []
        
        for item in self.items:
            sub_editor = qt.QCheckBox()
            sub_editor.setProperty( self.PROPERTY_NAME, item )
            
            doc = self.get_documentation( item )
            sub_editor.setToolTip( doc )
            sub_editor.setWhatsThis( doc )
            layout.addWidget( sub_editor )
            sub_editor.setText( self.get_name( info, item ) )
            control_lookup[item] = sub_editor
            self.sub_editors.append( sub_editor )
        
        spacerItem = qt.QSpacerItem( 20, 40, qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum )
        layout.addItem( spacerItem )
        
        super().__init__( info, self.editor )
    
    
    @virtual
    def get_documentation( self, item: object ) -> str:
        ignore( item )
        return ""
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        raise NotImplementedError( "abstract" )
    
    
    def on_set_value( self, value: Flags ) -> None:
        for x in self.sub_editors:
            if self.is_set( self.info, x.property( self.PROPERTY_NAME ), value ):
                x.setChecked( True )
            else:
                x.setChecked( False )
    
    
    def is_set( self, info: EditorInfo, query: object, value: object ) -> bool:
        raise NotImplementedError( "abstract" )
    
    
    def on_get_value( self ) -> object:
        values = []
        for x in self.sub_editors:
            if x.isChecked():
                values.append( x.property( self.PROPERTY_NAME ) )
        
        return self.translate( self.info, values )
    
    
    def get_items( self, info: EditorInfo ) -> Iterable[object]:
        raise NotImplementedError( "abstract" )
    
    
    def get_name( self, info: EditorInfo, item: object ) -> str:
        raise NotImplementedError( "abstract" )
    
    
    def translate( self, info: EditorInfo, values: List[object] ) -> object:
        raise NotImplementedError( "abstract" )


class FlagsEditor( AbstractFlagsEditor ):
    """
    Edits: Flags
    """
    
    
    def get_documentation( self, item: Flags ):
        return Documentation( item.__doc__ )["cvar", item.name]
    
    
    @classmethod
    def on_get_priority( cls ) -> int:
        # We're generic flags, so make way for something more specific
        return cls.Priority.LOW
    
    
    def translate( self, info: EditorInfo, values: List[Flags] ) -> Flags:
        type_ = info.annotation.value
        
        result = type_( 0 )
        
        for value in values:
            result |= value
        
        return result
    
    
    def is_set( self, info: EditorInfo, query: Flags, value: Flags ) -> bool:
        return (value & query) == query
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_direct_subclass_of( Flags )
    
    
    def get_items( self, info: EditorInfo ) -> Iterable[object]:
        return cast( Iterable[Flags], info.annotation.value_or_optional_value )
    
    
    def get_name( self, info: EditorInfo, item: Flags ) -> str:
        return item.name


class BoolEditor( AbstractEditor ):
    """
    Edits:  bool
            Optional[bool]
    """
    
    
    def __init__( self, info: EditorInfo ):
        obd = info.messages.boolean_display
        
        self.option_align_left = info.messages.keep_left
        self.option_radio = obd == EBoolDisplay.RADIO_BUTTONS
        self.option_combo = obd == EBoolDisplay.COMBOBOX
        self.option_check = obd is None
        self.option_yes_text, self.option_no_text, self.option_none_text = list( info.messages.boolean_texts )
        
        if not self.option_check:
            self.option_yes_text = self.option_yes_text or "True"
            self.option_no_text = self.option_no_text or "False"
            self.option_none_text = self.option_none_text or "None"
        
        # Create frame
        layout = qt.QHBoxLayout()
        layout.setContentsMargins( qt.QMargins( 0, 0, 0, 0 ) )
        self.editor = qt.QFrame()
        self.editor.setLayout( layout )
        
        if self.option_radio:
            self.radio_yes = qt.QRadioButton()
            self.radio_yes.setText( self.option_yes_text )
            self.radio_no = qt.QRadioButton()
            self.radio_no.setText( self.option_no_text )
            editors = [self.radio_yes, self.radio_no]
            
            if info.annotation.is_optional:
                self.radio_neither = qt.QRadioButton()
                self.radio_neither.setText( self.option_none_text )
                editors.append( self.radio_neither )
            else:
                self.radio_neither = None
        elif self.option_combo:
            self.combo_box = qt.QComboBox()
            self.combo_box.currentIndexChanged[int].connect( self.__on_checkbox_stateChanged )
            
            if info.annotation.is_optional:
                self.combo_box.addItem( self.option_none_text )  # None
            
            self.combo_box.addItem( self.option_yes_text )  # Yes
            self.combo_box.addItem( self.option_no_text )  # No
            
            editors = (self.combo_box,)
        else:
            self.check_box = qt.QCheckBox()
            self.check_box.stateChanged[int].connect( self.__on_checkbox_stateChanged )
            
            if info.annotation.is_optional:
                self.check_box.setTristate( True )
            
            editors = (self.check_box,)
        
        for editor in editors:
            layout.addWidget( editor )
            
            if not self.option_align_left:
                editor.setSizePolicy( qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed )
        
        if self.option_align_left:
            layout.addItem( qt.QSpacerItem( 1, 1, qt.QSizePolicy.Expanding, qt.QSizePolicy.Ignored ) )
        
        super().__init__( info, self.editor )
        
        self.on_set_value( None )
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ):
        return info.annotation.is_direct_subclass_of_or_optional( bool )
    
    
    @qt.exceptToGui()
    def __on_checkbox_stateChanged( self, state: int ):
        if self.option_radio:
            pass
        elif self.option_combo:
            pass
        else:
            if state == qt.Qt.PartiallyChecked:
                self.check_box.setText( self.option_none_text )
            elif state == qt.Qt.Checked:
                self.check_box.setText( self.option_yes_text )
            else:
                self.check_box.setText( self.option_no_text )
    
    
    def on_set_value( self, value: Optional[object] ) -> None:
        if self.option_radio:
            if value is None:
                if self.radio_neither is not None:
                    self.radio_neither.setChecked( True )
                else:
                    self.radio_yes.setChecked( False )
                    self.radio_no.setChecked( True )
            elif value:
                self.radio_yes.setChecked( True )
            else:
                self.radio_no.setChecked( True )
        elif self.option_combo:
            if self.info.annotation.is_optional:
                if value is None:
                    self.combo_box.setCurrentIndex( 0 )
                elif value:
                    self.combo_box.setCurrentIndex( 1 )
                else:
                    self.combo_box.setCurrentIndex( 2 )
            else:
                if value is None:
                    self.combo_box.setCurrentIndex( -1 )
                elif value:
                    self.combo_box.setCurrentIndex( 0 )
                else:
                    self.combo_box.setCurrentIndex( 1 )
        else:
            if value is None:
                if self.info.annotation.is_optional:
                    self.check_box.setCheckState( qt.Qt.PartiallyChecked )
                else:
                    self.check_box.setChecked( qt.Qt.Unchecked )
            elif value:
                self.check_box.setChecked( qt.Qt.Checked )
            else:
                self.check_box.setChecked( qt.Qt.Unchecked )
            
            self.__on_checkbox_stateChanged( self.check_box.checkState() )
    
    
    def on_get_value( self ) -> Optional[bool]:
        if self.option_radio:
            if self.radio_yes.isChecked():
                return True
            elif self.radio_no.isChecked():
                return False
            elif self.info.annotation.is_optional:
                return None
            else:
                raise ValueError( "A selection must be made." )
        elif self.option_combo:
            if self.info.annotation.is_optional:
                if self.combo_box.currentIndex() == 0:
                    return None
                elif self.combo_box.currentIndex() == 1:
                    return True
                elif self.combo_box.currentIndex() == 2:
                    return False
            else:
                if self.combo_box.currentIndex() == 0:
                    return True
                elif self.combo_box.currentIndex() == 1:
                    return False
            
            raise ValueError( "A selection must be made." )
        else:
            x = self.check_box.checkState()
            
            if x == qt.Qt.PartiallyChecked:
                return None
            elif x == qt.Qt.Checked:
                return True
            elif x == qt.Qt.Unchecked:
                return False
            else:
                raise SwitchError( "self.editor.checkState()", x )
    
    
    @classmethod
    def on_get_priority( cls ):
        return cls.Priority.HIGH


class FloatEditor( AbstractEditor ):
    """
    Edits:  float
    """
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ):
        return info.annotation.value is float
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = qt.QLineEdit()
        self.editor.setPlaceholderText( "0" )
        self.editor.setValidator( qt.QDoubleValidator() )
        super().handle_changes( self.editor.textChanged[str] )
        super().__init__( info, self.editor, )
        self.on_set_value( None )
    
    
    def on_set_value( self, value: Optional[float] ) -> None:
        self.editor.setText( str( value ) if value else "0" )
    
    
    def on_get_value( self ) -> Optional[float]:
        text = self.editor.text()
        
        if not text:
            return 0
        
        return float( text )


class IntEditor( AbstractEditor ):
    """
    Edits:  int
    """
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.editor = qt.QSpinBox()
        self.editor.setMinimum( -2147483648 )
        self.editor.setMaximum( 2147483647 )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ):
        return info.annotation.is_direct_subclass_of( int )
    
    
    def on_set_value( self, value: int ) -> None:
        if value is None:
            value = 0
        
        self.editor.setValue( value )
    
    
    def on_get_value( self ) -> int:
        return self.editor.value()


class NoneEditor( AbstractEditor ):
    
    def __init__( self, info: EditorInfo ):
        editor = qt.QWidget()
        super().__init__( info, editor )
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.value is None
    
    
    def on_get_value( self ) -> Optional[object]:
        return None
    
    
    def on_set_value( self, value: Optional[object] ):
        pass


class ReadonlyEditor( AbstractEditor ):
    """
    Edits:  flags.READ_ONLY
    """
    
    
    @classmethod
    def on_get_priority( cls ) -> int:
        # Its important we "readonly" anything else.
        return cls.Priority.FIRST
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.editor = qt.QLineEdit()
        self.editor.setReadOnly( True )
        super().__init__( info, self.editor )
        self.value = None
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_mannotation_of( isReadonly )
    
    
    def on_set_value( self, value: object ) -> None:
        self.value = value
        self.editor.setText( str( value ) )
    
    
    def on_get_value( self ) -> object:
        return self.value


class UnionEditor( AbstractEditor ):
    """
    Edits: Union[T, U, V, ...]
    """
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_union
    
    
    @classmethod
    def on_get_priority( cls ) -> int:
        # Anything taking the type directly should get first dibs
        return cls.Priority.VERY_LOW
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.frame = qt.QWidget()
        self.layout = qt.QHBoxLayout()
        self.layout.setContentsMargins( qt.QMargins( 0, 0, 0, 0 ) )
        self.frame.setLayout( self.layout )
        self.under_editor: AbstractEditor = None
        self.combo = qt.ComboBoxWrapper( qt.QComboBox(),
                                         options = [x for x in info.annotation.union_args],
                                         namer = lambda x: str( AnnotationInspector( x ) ) )
        self.combo.box.setStyleSheet( "QComboBox { font-family:Consolas,monospace; }" )
        self.layout.addWidget( self.combo.box )
        self.combo.box.currentIndexChanged[int].connect( self.__on_currentIndexChanged )
        self.combo.box.setSizePolicy( qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed )
        
        super().__init__( info, self.frame )
    
    
    def __create_editor( self ):
        if self.under_editor:
            self.under_editor.editor.setParent( None )
        
        t = self.combo.selected
        self.under_editor = self.info.editorium.get_editor( t )
        self.layout.addWidget( self.under_editor.editor )
    
    
    @qt.exceptToGui()
    def __on_currentIndexChanged( self, _: int ):
        self.__create_editor()
    
    
    def on_set_value( self, value: Optional[object] ):
        if self.under_editor is None:
            self.__create_editor()
        
        if value is not None:
            t = type( value )
            self.combo.force_selected( t )
        
        self.under_editor.set_value( value )
    
    
    def on_get_value( self ):
        return self.under_editor.get_value()
