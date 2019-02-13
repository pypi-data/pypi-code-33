# Copyright (C) 2011-2018 by Dr. Dieter Maurer <dieter@handshake.de>
"""Elementary form template."""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from . import zope_major_version

form_template = ViewPageTemplateFile(
  "form_template%s.pt" % ("" if zope_major_version <= 2 else "-4")
  )
