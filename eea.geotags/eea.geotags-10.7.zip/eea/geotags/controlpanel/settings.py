""" Control Panel
"""
from zope.component import queryUtility
from zope.interface import implementer
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from eea.geotags.controlpanel.interfaces import IGeotagsSettings
from eea.geotags.config import _


class EditForm(controlpanel.RegistryEditForm):
    """ Control panel edit form
    """

    schema = IGeotagsSettings
    label = _(u"EEA Geotags Settings")
    description = _(u"EEA Geotags settings")


class ControlPanel(controlpanel.ControlPanelFormWrapper):
    """ Control panel form wrapper
    """

    form = EditForm


@implementer(IGeotagsSettings)
class ControlPanelAdapter(object):
    """ Settings adapter
    """

    def __init__(self, context):
        self.context = context
        self._settings = None

    def __getattr__(self, name):
        return getattr(self.settings, name, None)

    @property
    def settings(self):
        """ Settings
        """
        if self._settings is None:
            self._settings = queryUtility(
                IRegistry).forInterface(IGeotagsSettings, False)
        return self._settings
