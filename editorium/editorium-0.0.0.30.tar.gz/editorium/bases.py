import warnings

import stringcoercion
import copy
from typing import Optional, List, Tuple

from mhelper import AnnotationInspector, array_helper, MEnum
from mhelper_qt import exceptToGui


class EBoolDisplay( MEnum ):
    CHECKBOX = 0
    RADIO_BUTTONS = 1
    COMBOBOX = 2


class EditMessages:
    """
    Messages passed to Editorium that control editor behaviour.
    
    The value `None` for all fields uses the default value, if present.
    
    .. note::
    
        The default instance vars, specified in `__init__`, control the standard editor set only, custom fields in
        addition to these _can_ be specified in order to control non-standard editors.
    
    :ivar keep_left:        Controls `NullableEditor` and `Editor_Boolean`.
                            Setting this to `True` will align the checkbox left, when the editor is hidden.
                            Only useful when :ivar:`hide` is set.
    
    :ivar hide:             Setting this to a `True` value will hide, rather than disable, editors when they are not in use.
                            Default: False
    
    :ivar boolean_display:  Controls Editor_Boolean.
                            Setting this to a value will present an editor rather than checkboxes for booleans.
                            Unlike checkboxes these editors require text, hence if :ivar:`boolean_texts` is not
                            specified, the default boolean "empty texts" are substituted for ('true','false','none')
    
    :ivar boolean_texts:    Controls Editor_Boolean.
                            Set this to a tuple of 3: yes text, no text, indeterminate text.
                            Default: ('','','').
    
    :ivar enum_none:        Sets the EnumEditor 'none' text.
    
    :ivar hide_text:        Controls the text displayed in the checkbox when an editor is not shown or not shown.
                            Set this to a tuple of 2: show text, hide text
                            Default: "", "" if :ivar:`hide` is set, else ":", ":"
    """
    
    
    def __init__( self, *, default: bool = False ):
        self.keep_left: bool = False
        self.hide: bool = False
        self.boolean_display: EBoolDisplay = EBoolDisplay.CHECKBOX
        self.boolean_texts: Tuple[str, str, str] = ("", "", "")
        self.enum_none: str = "None"
        self.hide_text: Tuple[str, str] = ("", "")
        self.coercers: stringcoercion.CoercerCollection = stringcoercion.get_default_collection()
        
        if not default:
            for k in list( self.__dict__ ):
                self.__dict__[k] = None
    
    
    def copy( self ) -> "EditMessages":
        return copy.copy( self )
    
    
    def update( self, other: "EditMessages" ):
        for k, v in other.__dict__.items():
            if not k.startswith( "_" ) and v is not None:
                self.__dict__[k] = v


class EditorInfo:
    def __init__( self, editorium: "Editorium", type_, messages: EditMessages ) -> None:
        self.editorium = editorium
        self.annotation: AnnotationInspector = AnnotationInspector( type_ )
        self.messages: EditMessages = messages
    
    
    def __str__( self ):
        return str( self.annotation )


class AbstractEditorType( type ):
    class Priority:
        FALLBACK = 200
        LAST = 100
        VERY_LOW = 75
        LOW = 50
        DEFAULT = 0
        HIGH = -50
        FIRST = -100
    
    
    def can_handle( cls, info: EditorInfo ) -> bool:
        """
        Determines if this type can handle editing this type.
        
        :param info: Contains the type information
        """
        raise NotImplementedError( "abstract" )
    
    
    def get_priority( cls ) -> int:
        """
        Priority of this editor
        """
        raise NotImplementedError( "abstract" )
    
    
    def __str__( self ):
        return "AbstractEditorType(name = {}, priority = {})".format( repr( self.__name__ ), self.get_priority() )


class AbstractEditor( metaclass = AbstractEditorType ):
    """
    Base editor class
    """
    
    
    def __init__( self, info: EditorInfo, editor ):
        """
        CONSTRUCTOR
        :param info:        `info` passed to derived class constructor 
        :param editor:      Editor widget created by derived class 
        """
        from PyQt5.QtWidgets import QWidget
        assert isinstance( editor, QWidget )
        self.info = info
        self.editor: QWidget = editor
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        """
        Determines if this type can handle editing this type.
        
        :param info: Contains the type information
        """
        return cls.on_can_handle( info )
    
    
    @classmethod
    def get_priority( cls ) -> int:
        """
        Priority of this editor
        """
        return cls.on_get_priority()
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        """
        The derived class should perform the `can_handle` logic.
        """
        raise NotImplementedError( "abstract" )
    
    
    def get_value( self ) -> Optional[object]:
        """
        Obtains the value stored in the editor.
        This method should generally return the correct type, though this is not guaranteed.
        This method may raise an exception if the user has made an invalid selection.
        
        :except Exception: Invalid selection 
        """
        return self.on_get_value()
    
    
    def set_value( self, value: Optional[object] ):
        """
        Sets the value of the editor.
        
        :param value:   A value that commutes with `self.info`.
                        The value `None` should also always be accepted as a default.
        """
        return self.on_set_value( value )
    
    
    def handle_changes( self, signal ) -> None:
        """
        Connects the specified `signal` to the __change_occurred handler.
        """
        signal.connect( self.__change_occurred )
    
    
    @classmethod
    def on_get_priority( cls ) -> int:
        """
        The derived class should perform the `get_priority` logic.
        """
        return cls.Priority.DEFAULT
    
    
    def on_get_value( self ) -> Optional[object]:
        """
        The derived class should perform the `get_value` logic.
        """
        raise NotImplementedError( "abstract" )
    
    
    def on_set_value( self, value: Optional[object] ):
        """
        The derived class should perform the `set_value` logic.
        """
        raise NotImplementedError( "abstract" )
    
    
    # noinspection PyUnusedLocal
    @exceptToGui()
    def __change_occurred( self, *args, **kwargs ) -> None:
        """
        Handles changes to the editor.
        """
        pass


class Editorium:
    """
    Holds the set of editors.
    
    :ivar editors:              Array of editor types.
    :ivar default_messages:     Always appended to `messages`. 
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.editors: List[AbstractEditorType] = []
        self.default_messages = EditMessages( default = True )
    
    
    def can_handle( self, type_: type, priority = AbstractEditor.Priority.FALLBACK ) -> bool:
        """
        Returns if any editor is capable of handling this type.
        
        :param type_:       Type to check 
        :param priority:    Minimum accepted priority, the default, `FALLBACK`, excludes the Fallback editor (which accepts all `type`s). 
        """
        ei = EditorInfo( self, type_, self.default_messages )
        
        for x in self.editors:
            if x.get_priority() < priority:
                if x.can_handle( ei ):
                    return True
        
        return False
    
    
    def register( self, editor: AbstractEditorType ):
        """
        Registers an editor with this Editorium.
        """
        array_helper.ordered_insert( self.editors, editor, key = lambda x: x.get_priority() )
    
    
    def get_editor( self, type_: type, *, messages: EditMessages = None ) -> AbstractEditor:
        """
        Constructs a suitable editor for this type.
        :param messages:    Optional messages to pass to the editors. 
        :param type_:       Type of value to create editor for. Basic types, as well as most of `typing` and `mhelper.special_types` should be handled.
        :return: 
        """
        messages_d: EditMessages = self.default_messages.copy()
        
        if messages is not None:
            messages_d.update( messages )
        
        info = EditorInfo( self, type_, messages_d )
        
        can_handle = []
        
        for x in self.editors:
            if x.can_handle( info ):
                can_handle.append( x )
        
        if not can_handle:
            raise ValueError( "No suitable editor found for «{}». "
                              "This is an internal error and suggests that a working fallback "
                              "editor has not been provided. "
                              "The list of editors follows: {}"
                              .format( type_, self.editors ) )
        
        can_handle = sorted( can_handle, key = lambda x: x.get_priority() )
        
        if len( can_handle ) >= 2 and can_handle[0].get_priority() == can_handle[1].get_priority():
            warnings.warn( "At least two editors are capable of handling this "
                           "type and have the same priority ({}): {}, {}"
                           .format( can_handle[0].get_priority(), can_handle[0], can_handle[1] ) )
        
        r = can_handle[0]( info )
        assert hasattr( r, "editor" ) and r.editor is not None, "«{}» didn't call the base class constructor.".format( x )
        return r
