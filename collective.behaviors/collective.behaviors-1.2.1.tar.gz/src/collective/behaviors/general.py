
from collective import dexteritytextindexer
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.contenttypes.interfaces import IDocument
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import provider
from zope.interface import implementer
from zope.interface import alsoProvides

from collective.behaviors import _
from collective.behaviors.util import get_registry_entry


@provider(IFormFieldProvider)
class IParentTitleAsCreator(model.Schema):
    
    dexteritytextindexer.searchable('container_as_creator')
    container_as_creator = schema.Bool(
        title=_(u'label_container_as_creator', u'Allow Parent\'s Title as a '
                u'createor'),
        description=_(
            u'help_container_as_creator',
            default=_(u'If checked, the title of container for this item '
                      u'will be added to this item list of creators.')
        ),
        required=False,
        default=True,
    )
    model.fieldset(
        'ownership',
        label=_(
            'label_schema_ownership',
            default=u'Ownership'
        ),
        fields=['container_as_creator'],
    )
    

@implementer(IParentTitleAsCreator)
class ParentTitleAsCreator(object):
    
    def __init__(self, context):
        self.context = context
        
    @property
    def container_as_creator(self):
        return self.context.container_as_creator

    @container_as_creator.setter
    def container_as_creator(self, value):
        """ Set the recruiter for the Job
        
        If the container for this obj is an organisation, then add the title
        of the organisation to the list of creators."""
        parent = self.context.aq_parent
        if value:
            allowed_containers = get_registry_entry(
                "collective.behaviors.containers_as_creators"
            )
            if parent.portal_type in allowed_containers:
                container_title = (parent.title,)
                if parent.title not in self.context.creators:
                    self.context.creators += container_title

        self.context.container_as_creator = value