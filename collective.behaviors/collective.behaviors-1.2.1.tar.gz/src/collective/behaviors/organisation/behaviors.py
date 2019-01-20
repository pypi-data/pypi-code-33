import uuid

from collective import dexteritytextindexer
from collective.z3cform.datagridfield import BlockDataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from plone.app.users.schema import checkEmailAddress
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.dexterity.behaviors.metadata import Ownership
from plone.app.z3cform.widget import (
    AjaxSelectFieldWidget,
    DateWidget,
    LinkWidget,
    SelectFieldWidget
)
from plone.formwidget.namedfile.widget import NamedImageFieldWidget
from plone.namedfile.field import NamedBlobImage
from plone.schema import Email
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from zope.interface import Interface
from zope.schema.interfaces import IFromUnicode
from Products.CMFCore.interfaces import IDublinCore

from collective.behaviors import _, util


class IEntity(Interface):
    """Abstract marker interface.
    """


@provider(IFormFieldProvider)
class IOrganisation(model.Schema, IEntity):

    dexteritytextindexer.searchable('organisation_type')
    dexteritytextindexer.searchable('industry')
    dexteritytextindexer.searchable('founders')

    organisation_type = schema.Choice(
        title=_(u"Organisation Type"),
        vocabulary=u"collective.vocabularies.organisation.types",
        required=True,
    )
    industry = schema.Choice(
        title=_(u"Industry"),
        vocabulary=u"collective.vocabularies.organisation.industries",
        required=True,
    )
    directives.widget(
        'industry',
        SelectFieldWidget
    )
    
    date_founded = schema.Date(
        title=_(u"Date Founded"),
        required=False
    )
    directives.widget(
        'date_founded',
        DateWidget
    )
    
    organisation_size = schema.Choice(
        title=_(u"Organisation Size"),
        vocabulary=u"collective.vocabularies.organisation.sizes",
        required=True,
    )
    
    model.fieldset(
        'ownership',
        label=_(
            'label_schema_ownership',
            default=u'Ownership'
        ),
        fields=['founders'],
    )

    founders = schema.Tuple(
        title=_(u'label_creators', u'Founders'),
        description=_(
            u'help_founders',
            default=u'Persons who started the business, company or entity.'
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value="",
    )
    directives.widget(
        'founders',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Users'
    )