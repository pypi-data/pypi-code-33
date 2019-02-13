# Copyright (C) 2018 by Dr. Dieter Maurer <dieter@handshake.de>
"""Resources to test the package.

You need a Zope [2 or 4] setup and must ensure that this directories
`configure.zcml` is activated during startup.
"""
from zope.interface import Interface, implementer
from zope.schema import TextLine, Int

from OFS.SimpleItem import SimpleItem

from ...schema import SchemaConfigured
from ...propertymanager import PropertyManager

from ..constructor import \
     add_form_factory, SchemaConfiguredZmiAddForm
from ..form import SchemaConfiguredZmiDisplayForm, SchemaConfiguredZmiEditForm

class ISchema(Interface):
  title = TextLine(title=u"Title", default=u"")
  number = Int(title=u"Number", required=False)
  

@implementer(ISchema)
class TestSchemaConfigured(SimpleItem, SchemaConfigured):
  """An object to test `dm.zope.schema.z2.constructor`."""

  meta_type = "Test schema configured constructor"

  manage_options = (
    dict(label="View", action="manage_view"),
    dict(label="Edit", action="manage_edit"),
    ) + SimpleItem.manage_options

  SC_SCHEMAS = ISchema

  # for test purposes only -- usually, you would use `ClassSecurityInfo`
  __roles__ = None
  manage_view__roles__ = None # public
  manage_edit__roles__ = ["Manager"]

  def manage_view(self, REQUEST):
    """show the object."""
    return SchemaConfiguredZmiDisplayForm(self, REQUEST)()

  def manage_edit(self, REQUEST):
    """esit the object."""
    return SchemaConfiguredZmiEditForm(self, REQUEST)()


@implementer(ISchema)
class TestPropertyManager(SimpleItem, PropertyManager, SchemaConfigured):
  """An object to test `dm.zope.schema.propertymanager`."""

  meta_type = "Test schema configured property manager"

  manage_options = PropertyManager.manage_options + SimpleItem.manage_options

  SC_SCHEMAS = ISchema


def initialize(context):
  context.registerClass(
    TestSchemaConfigured,
    constructors=(add_form_factory(TestSchemaConfigured,
                                   form_class=SchemaConfiguredZmiAddForm
                                   ),
                  )
    )
  # register `TestPropertyManager` if `dm.zope.generate` is present
  try:
    from dm.zope.generate.constructor import \
         add_form_factory as pm_add_form_factory, \
         add_action_factory
  except ImportError: pass
  else:
    context.registerClass(
      TestPropertyManager,
      constructors=(pm_add_form_factory(TestPropertyManager),
                    add_action_factory(TestPropertyManager),
                    ),
      )

