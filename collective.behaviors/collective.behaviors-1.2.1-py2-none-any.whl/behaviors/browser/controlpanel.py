from zope.interface import Interface
from zope import schema
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from plone.z3cform import layout
from plone.directives import form
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from collective.behaviors import _


class IParentTitleAsCreator(form.Schema):
    """ Define controlpanel Data data structure """
    
    containers_as_creators = schema.Tuple(
        title=_(u'label_containers_as_creators', 
                default=u'List Content Types for Parent\'s Title as Creator'),
        description=_(
            u'help_containers_as_creators',
            default=(u'List each content type in a new line. '
                     u'Enable Parent\'s Title as Creator Behavior for child '
                     u'content type.')
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value="",
    )



class ParentTitleAsCreatorVCPF(RegistryEditForm):
    """
    Container Name As Creator Vocabulary Controlpanel Form 
    """
    schema = IParentTitleAsCreator
    schema_prefix = "collective.behaviors"
    label = (u"Content Type for Parent's Title as Creator Form")

    def getContent(self):
        try:
            data = super(ParentTitleAsCreatorVCPF, self).getContent()
        except KeyError:
            data =  {
                'containers_as_creators': ('Document',)
            }
            registry = getUtility(IRegistry)
            registry.registerInterface(IParentTitleAsCreator)
        return data


ParentTitleAsCreatorVCPView = layout.wrap_form(
   ParentTitleAsCreatorVCPF, ControlPanelFormWrapper)
