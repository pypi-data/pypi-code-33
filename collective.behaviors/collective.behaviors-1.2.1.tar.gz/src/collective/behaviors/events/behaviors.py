import uuid
from plone.autoform import directives
from zope.schema.interfaces import IFromUnicode
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from plone.supermodel import model
from plone.autoform import directives
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from plone.schema import Email
from plone.app.users.schema import checkEmailAddress
from plone.namedfile.field import NamedBlobImage

from plone.app.z3cform.widget import LinkWidget
from plone.formwidget.namedfile.widget import NamedImageFieldWidget
from collective.z3cform.datagridfield import BlockDataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from collective.behaviors import _, util


@implementer(IFromUnicode)
class ISpeaker(model.Schema):
    
    directives.mode(oid='hidden')
    oid = schema.TextLine(
        title=u"UUID",
        default=u'{}'.format(uuid.uuid4().hex)
    )
    
    first_name = schema.TextLine(
        title=_(u"First Name")
    )
    last_name = schema.TextLine(
        title=_(u"Last Name"),
    )
    email = Email(
        title=_(u'label_email', default=u'Email'),
        description=_(u'help_email', default=u''),
        required=False
    )
    profession = schema.TextLine(
        title=_(u"Profession"),
        required=False,
    )
    description = schema.Text(
        title=_(u"Biography"),
        required=False,
    )
    website = schema.URI(
        title=_(u'label_website', default=u'Website'),
        description=_(u'help_website', default=u''),
        required=False
    )
    directives.widget(
        'website',
        LinkWidget
    )
    phone = schema.TextLine(
        title=_(u'label_phone', default=u'Phone'),
        description=_(u'help_phone', default=u''),
        required=False
    )
    picture = schema.ASCII(
        title=_(u"Please upload an image"),
        required=False,
    )
    directives.widget(
        'picture',
        NamedImageFieldWidget
    )


@provider(IFormFieldProvider)
class ISpeakers(model.Schema):
    

    speakers = schema.List(
        title=_(u'Event Speakers'),
        value_type=DictRow(title=u"speakers", schema=ISpeaker),
        required=False
    )
    directives.widget(
        'speakers',
        BlockDataGridFieldFactory
    )
    
    model.fieldset(
        'event_speakers',
        label=_(u"Speakers"),
        fields=['speakers']
    )


@implementer(IFromUnicode)
class ISponsor(model.Schema):
    
    directives.mode(oid='hidden')
    oid = schema.TextLine(
        title=u"UUID",
        default=u'{}'.format(uuid.uuid4().hex)
    )
    
    name = schema.TextLine(
        title=_(u"Name")
    )
    email = Email(
        title=_(u'label_email', default=u'Email'),
        description=_(u'help_email', default=u''),
        required=False
    )
    website = schema.URI(
        title=_(u'label_website', default=u'Website'),
        description=_(u'help_website', default=u''),
        required=False
    )
    picture = schema.ASCII(
        title=_(u"Please upload an image"),
        required=False,
    )
    directives.widget(
        'picture',
        NamedImageFieldWidget
    )


@provider(IFormFieldProvider)
class ISponsors(model.Schema):
    

    sponsors = schema.List(
        title=_(u'Event Sponsors'),
        value_type=DictRow(title=u"sponsors", schema=ISponsor),
        required=False
    )
    directives.widget(
        'sponsors',
        BlockDataGridFieldFactory
    )
    
    model.fieldset(
        'event_sponsors',
        label=_(u"Sponsors"),
        fields=['sponsors']
    )


@implementer(ISponsors)
class Sponsors(object):
    
    _sponsors = None
    
    def __init__(self, context):
        self.context = context
        
    @property
    def sponsors(self):
        return self.context.sponsors

    @sponsors.setter
    def sponsors(self, data):
        if data is None:
            data = []
        
        sponsors = {
            v['oid']: v
            for v in (self.context.sponsors or [])
        }
        for index, item in enumerate(data):
            if not item['picture']:
                data[index]['picture'] = sponsors[index]['picture']

        self.context.sponsors = data


@implementer(ISpeakers)
class Speakers(object):
    
    _speakers = None
    
    def __init__(self, context):
        self.context = context
        
    @property
    def speakers(self):
        return self.context.speakers

    @speakers.setter
    def speakers(self, data):
        if data is None:
            data = []
        
        speakers = [
            { v['oid']: v }
            for v in (self.context.speakers or [])
        ]
        speakers = self.context.speakers
        for index, item in enumerate(data):
            # if no picture data is passed, then maybe
            # we are resaving and we already have a pic
            if not item['picture']:
                data[index]['picture'] = speakers[index]['picture']

        self.context.speakers = data
