'''

    kabaret.flow.relations

    Defines the relations classes used to bind objects together:
        Parent:     Returns the parent of the object.
                    If the nb_levels argument is more than 1, a grand parent
                    is returned: 
                        1 -> parent
                        2 -> parent's parent
                        3 -> parent's parent's parent
                        etc...

        Child:      Declares a Child in the Object. The Object will be the parent
                    of the created child.

        Param:      Declares a Child Value in the Object.
                    The default_value and value_type arguments control the initial data
                    returned by the child Value and the type of the child Value.
                    (a subclass of kabaret.flow.values.Value())
        
        SessionParam: Declare a Child SessionValue in the Object.
                    This value will be reset to its default at each session and
                    is not shared with other sessions.

        IntParam
        FloatParam
        StringParam
        DictParam
        OrderedStringSetParam
        HashParam:  Declares as Child the corresponding Value subclass.

        Separator:
                    A pre-configured Param acting as a separator in GUI

        Computed:   Declares a Child ComputedValue in the Object. 
                    See kabaret.flow.values.ComputedValue().

        Connection: Declares a Child Ref in the Object.
                    The ref being a Value returning another Object, this relations
                    is used to define dependencies between Objects.
                    See kabaret.flow.values.Ref()

'''
import logging
from .exceptions import WIPException

from .object import _Relation
from .values import (
    Value, SessionValue,
    IntValue, BoolValue, FloatValue, StringValue, DictValue,
    OrderedStringSetValue, HashValue,
    ComputedValue, Ref
)


class Parent(_Relation):
    '''
    The Parent relation give access to the related object's parent or grand-parents.
    '''
    _RELATION_TYPE_NAME = 'Parent'

    def __init__(self, nb_levels=1):
        super(Parent, self).__init__(None)
        self.nb_levels = nb_levels

    def __get__(self, o, t=None):
        if o is None:
            return self
        parent = o
        for i in range(self.nb_levels):
            if parent is None:
                raise Exception(
                    'Could not find a parent at level %d for %r' % (i, o._mng.oid()))
            parent = parent._mng.parent
        return parent


class Child(_Relation):
    '''
    The Child relation sets an Object as the Child of the owner of the relation
    (wich in turn becomes the parent)
    '''
    _RELATION_TYPE_NAME = 'Child'

    def _create_object(self, parent):
        try:
            related = self.related_type(parent, self.name)
        except:
            logging.getLogger('kabaret.flow').error(
                'Creating related object: %s(%r, %r)' % (
                    self.related_type.__name__, parent.oid(), self.name
                )
            )
            raise
        return related


class Param(Child):
    '''
    A Child relating to a :any:`Value` or one of its subclasses.
    '''

    _RELATION_TYPE_NAME = 'Param'

    _DEFAULT_VALUE_TYPE = Value

    def __init__(self, default_value=None, value_type=None):
        '''
        Beware of the default_value: if it is passed by reference, all
        instance of the class owning the created value will share the value!
        For example:
            class MyObject(Object):
                my_dict = Param({})

            -> all instances of MyObject will have their my_dict Value sharing
            the same dict (initialized when python executed the class definition)

        The workaround is to use a callable that creates a new instance of the value:
            class MyObject(Object):
                my_dict = Param(dict)

        '''
        if value_type is None:
            value_type = self.__class__._DEFAULT_VALUE_TYPE
        elif not issubclass(value_type, self.__class__._DEFAULT_VALUE_TYPE):
            raise TypeError(
                '%r is not a subclass or %r, needed for relation %r' % (
                    value_type, self.__class__._DEFAULT_VALUE_TYPE,
                    self
                )
            )

        super(Param, self).__init__(value_type)
        if callable(default_value):
            self.get_default_value = default_value
        else:
            self.get_default_value = lambda: default_value

        # default for Param is editable:
        self._ui['editable'] = True
        try:
            default_editor = value_type.DEFAULT_EDITOR
        except Exception:
            pass
        else:
            self._ui['editor_type'] = default_editor
        self._watched = False

    def watched(self, b=True):
        '''
        Configures the related value to be watched or not (default is False).
        Watched value call their parent's child_value_changed() when changed.
        '''
        self._watched = b
        return self

    def _create_object(self, parent):
        value = self.related_type(parent, self.name)
        value.set_default_value(self.get_default_value())
        value.set_watched(self._watched)
        return value

#---OLD
    def __set__(self, o, v):
        raise WIPException('Never used this, it is confusing.')
        # we must use get() on related values so not using set() feels strange
        # (you may end up thinking it's an attribute and not a related value...)
        value = self.get_related(o)
        value.set(v)


class SessionParam(Param):
    '''
    A Param relating to a :any:`SessionValue`.
    '''

    _DEFAULT_VALUE_TYPE = SessionValue


class IntParam(Param):
    '''
    A Param relating to an :any:`IntValue`.
    '''

    _DEFAULT_VALUE_TYPE = IntValue


class BoolParam(Param):
    '''
    A Param relating to a :any:`BoolValue`.
    '''

    _DEFAULT_VALUE_TYPE = BoolValue


class FloatParam(Param):
    '''
    A Param relating to a :any:`FloatValue`.
    '''

    _DEFAULT_VALUE_TYPE = FloatValue


class StringParam(Param):
    '''
    A Param relating to a :any:`StringValue`.
    '''

    _DEFAULT_VALUE_TYPE = StringValue


class DictParam(Param):
    '''
    A Param relating to a :any:`DictValue`.
    '''

    _DEFAULT_VALUE_TYPE = DictValue


class OrderedStringSetParam(Param):
    '''
    A Param relating to an :any:`OrderedStringSetValue`.
    '''

    _DEFAULT_VALUE_TYPE = OrderedStringSetValue

    def __init__(self, value_type=None):
        super(OrderedStringSetParam, self).__init__(None, value_type)


class HashParam(Param):
    '''
    A Param relating to a :any:`HashValue`.
    '''

    _DEFAULT_VALUE_TYPE = HashValue

    def __init__(self, value_type=None):
        super(HashParam, self).__init__({}, value_type)


def Separator():
    '''
    Returns a Param relation showing an horizontal line in GUI.
    '''
    return Param(None).ui(editor='label', text='<hr>').ui(label='')


def Label(text, label=''):
    '''
    Returns a Param relation showing a (potentially html) text in GUI.
    '''
    return Param(None).ui(editor='label', text=text).ui(label=label)


class Computed(Param):
    '''
    A Param relating to a :any:`ComputedValue`

    The value computation is delegated to the parent's compute_child_value() method.
    The 'cached' and 'store_value' constuctor arguments will configure the ComputedValue.
    (See kabaret.flow.values.ComputedValue)

    You can use a subclass of ComputedValue by specifying computed_value_type in the constructor
    '''
    _RELATION_TYPE_NAME = 'Computed'

    _DEFAULT_VALUE_TYPE = ComputedValue

    def __init__(self, cached=False, store_value=False, computed_value_type=None):
        super(Computed, self).__init__(None, value_type=computed_value_type)
        self._cached = cached
        self._store_value = store_value
        self.ui(editable=False)

    def _create_object(self, parent):
        value = self.related_type(parent, self.name)
        value.set_watched(self._watched)
        value.set_cached(self._cached)
        value.set_store_value(self._store_value)
        return value


class Connection(Child):
    '''
    A Child relating to a :any:`Ref` subclass.
    '''
    _RELATION_TYPE_NAME = 'Connection'

    def __init__(self, related_type=None, ref_type=None):
        '''
        One of related_type and ref_type must be given:
            - if ref_type is not None, it will be used to reference the connected object
            - if ref_type is None, related_type.ref_type() will be used

        Specifying the ref_type instead of the related_type can be usefull in 
        obscur situation but should be avoided unless you have a good reason.
        (I would explain but I cant remind why I used this in the past :p)
        '''
        if ref_type is None:
            if related_type is not None:
                ref_type = related_type.ref_type()
            # else:
            # This mean the type will be configured later (I hope!)
            # It it used for example to have a ref to the same class.
        super(Connection, self).__init__(ref_type)

        # default for Connection is editable:
        self._ui['editable'] = True
        self._watched = False

    def _create_object(self, parent):
        value = self.related_type(parent, self.name)
        value.set_watched(self._watched)
        return value

    def watched(self, b=True):
        '''
        Configures the related value to be watched or not (default is False).
        Watched value call their parent's child_value_changed() when changed.
        '''
        self._watched = b
        return self

#---OLD
    def __set__(self, o, v):
        raise WIPException('Never used this, it is confusing.')
        # we must use get() on related values so not using set() feels strange
        # (you may end up thinking it's an attribute and not a related value...)
        value = self.get_related(o)
        value.set(v)

#---OLD


class PipelineConnection(Connection):
    '''
    A Connection with ui(editable=False).
    '''

    def __init__(self, related_type=None, ref_type=None):
        raise WIPException('THIS IS OBSOLETE')
        super(PipelineConnection, self).__init__(related_type, ref_type)
        # a PipelineConnection is just a not GUI editable connection
        self._ui['editable'] = False
