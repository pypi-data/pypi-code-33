# Copyright (C) 2010-2018 by Dr. Dieter Maurer <dieter@handshake.de>
"""Schema based properties definition.

Interface between Zope[2]'s ``OFS.PropertyManager.PropertyManager`` and
``zope.schema`` schemas.
"""

from sys import version_info

import OFS.PropertyManager as pmm
from ComputedAttribute import ComputedAttribute
from ExtensionClass import Base
from zope.interface import Interface, implementedBy, providedBy
from zope.schema import BytesLine, TextLine, Tuple, Text, Bytes, Bool, Int, Float

from .schema import schemadict, schemaitems

TitleField = BytesLine if version_info[0] <= 2 else TextLine


class _Descriptor(object):
  """auxiliary descriptor class for ``_properties`` access."""
  def __get__(self, instance, cls=None):
    if instance is None:
      # class level access
      assert cls.SC_SCHEMAS is not None, "you must define `SC_SCHEMAS`"
      return _properties_from_schema(schemaitems(cls.SC_SCHEMAS), None)
    else: return _properties_from_schema(schemaitems(instance.SC_SCHEMAS), instance)

  def __set__(self, instance, value):
    raise NotImplementedError('``_properties`` change not supported.')


class TitleSchema(Interface):
  """define the ``title`` property (required for ``PropertyManager`` subclasses).

  Note: for Python 2, this is defined as ``BytesLine``.
  Therefore, non ASCII values will likely not work reliable.
  """

  title = TitleField(title=u'title', default='')



class _PropertyManagerMetaclass(type(pmm.PropertyManager)):
  def __getattr__(pm, key):
    """look up default property values."""
    sd = schemadict(pm.SC_SCHEMAS)
    # should we raise ``AttributeError``, when ``default`` is ``None``?
    if key in sd: return sd[key].default
    raise AttributeError(key)


## This does not work in Zope2
##class PropertyManager(six.with_metaclass(_PropertyManagerMetaclass,
##                                     pmm.PropertyManager)
##                      ):
class PropertyManager(pmm.PropertyManager):
  """a non extensible ``PropertyManager`` with schema defined property types.

  For the moment, we lack selection support. We would need automatic
  "select variable" definition (in our own ``__getattr__``) to change
  this.
  """
  __metaclass__ = _PropertyManagerMetaclass

  # support for class level default property values
  #__metaclass__ = _PropertyManagerMetaclass

  _properties = _Descriptor()
    
  # override ``PropertyManager`` methods
  #  we are not extensible -- maybe, we should provide our own
  #  template instead, to get rid of the ``management_page_charset`` hackles???
  manage_propertiesForm=pmm.DTMLFile('dtml/properties', pmm.__dict__,
                                     property_extensible_schema__=False
                                     )

  def _not_extensible(*args):
    raise NotImplementedError('property schema not extensible')

  _setProperty = _not_extensible
  _delProperty = _not_extensible
  manage_addProperty = _not_extensible

if not isinstance(PropertyManager, _PropertyManagerMetaclass):
  # Python 3: it does not honour the ``__metadata__` hint
  PropertyManager = _PropertyManagerMetaclass(
    PropertyManager.__name__,
    (PropertyManager,),
    dict(PropertyManager.__dict__)
    )


def _properties_from_schema(sis, context):
  """derive property descriptions from schema items *sis*.

  *context* is used to access ``management_page_charset`` in order
  to determine whether we can use unicode properties.
  """
  mpc = getattr(context, 'management_page_charset', None)
  if callable(mpc): mpc = mpc()
  uprops = mpc is None or mpc.upper() == 'UTF-8'

  def u(t): return uprops and 'u' + t or t

  from zope.schema import \
       Text, TextLine, Bytes, BytesLine, Bool, Int, Float, List

  def pd_from_field(id, field):
    bt = isinstance(field, Tuple) and field.value_type or field
    if isinstance(bt, TextLine): ty = u('string')
    elif isinstance(bt, Text): ty = u('text')
    elif isinstance(bt, BytesLine): ty = 'string'
    elif isinstance(bt, Bytes): ty = 'text'
    elif isinstance(bt, Bool): ty = 'bool'
    elif isinstance(bt, Int): ty = 'int'
    elif isinstance(bt, Float): ty = 'float'
    else: raise NotImplementedError('property conversion not implemented for field: %s' % id)
    if isinstance(field, Tuple):
      if not ty.endswith('string'):
        raise NotImplementedError('property conversion not implemented for field: %s' % id)
      ty = ty[-6:] + lines
    # may want to encode unicode values using ``mpc``
    pd = dict(id=id, label=field.title or id,
              mode=field.readonly and 'r' or 'rw',
              type=ty,
              description=field.description,
              )
    return pd

  return tuple(pd_from_field(*i) for i in sis)
