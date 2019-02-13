# Copyright (C) 2011-2018 by Dr. Dieter Maurer <dieter@handshake.de>
from zope.interface import Interface


class ISchemaConfigured(Interface):
  """marker interface for ``SchemaConfigured`` classes.

  Used to facilitate the registration of forms and views.
  """
