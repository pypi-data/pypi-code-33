import copy
import hashlib
import logging
import urllib.request
from datetime import timedelta

import saml2
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import CASCADE
from django.shortcuts import reverse
from django.utils.translation import ugettext as _
from saml2.config import IdPConfig, SPConfig
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED
from saml2.saml import NAME_FORMATS_SAML2
from saml2.server import Server
from saml2.attribute_converter import AttributeConverter

import django_saml2_framework as DSF
from django_saml2_framework.utils import deepmerge

logger = logging.getLogger('django')

NAMEID_FORMAT_CHOICES = (
    (NAMEID_FORMAT_EMAILADDRESS, _('Email Address')),
    (NAMEID_FORMAT_UNSPECIFIED, _('Unspecified')),
)

NAMEID_FIELD_EMAIL = "EMAIL_FIELD"
NAMEID_FIELD_USERNAME = "USERNAME_FIELD"
NAMEID_FIELD_CHOICES = (
    ('EMAIL_FIELD', _('Email')),
    ('USERNAME_FIELD', _('Username')),
    ('__pk__', _('Primary Key')),
)


class ProviderMixin(models.Model):
    config_class = None
    settings_attr = None

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)
    entity = models.SlugField(max_length=100, unique=True)
    is_default = models.NullBooleanField(unique=True)

    name_id_format = models.CharField(
        max_length=200, choices=NAMEID_FORMAT_CHOICES, default=NAMEID_FORMAT_EMAILADDRESS)
    name_id_user_field = models.CharField(max_length=100,
                                          choices=NAMEID_FIELD_CHOICES, default=NAMEID_FIELD_EMAIL)
    # todo: add save location for this
    cert_file = models.FileField(blank=True)
    key_file = models.FileField(blank=True)  # todo: add save location for this

    logout_requests_signed = models.NullBooleanField(help_text=_(''))

    valid_for = models.DurationField(blank=True, default=timedelta(days=365))

    use_pysaml_maps = models.BooleanField(default=True, help_text=_('todo: put link to docs'))
    use_django_maps = models.BooleanField(default=True, help_text=_('Use the custom mapping for django'))
    use_custom_maps = models.BooleanField(default=True, help_text=_('use custom mapping models'))

    custom_maps = models.ManyToManyField('AttributeMap')

    class Meta:
        abstract = True

    def __str__(self):
        return '{} ({})'.format(self.name, self.entity)

    def save(self, *args, **kwargs):
        if not self.is_default:
            self.is_default = None

        self.reload()
        return super(ProviderMixin, self).save(*args, **kwargs)

    @property
    def url_kwargs(self):
        if not self.is_default:
            return {'entity_id': self.entity}
        return {}

    def reverse(self, url_name):
        return '{}{}'.format(settings.SAML2_BASE_URL, reverse(url_name, kwargs=self.url_kwargs))

    def get_attribute_converters(self, acs):
        if not self.use_pysaml_maps:
            # set the attr list to none to start
            acs = []
        if self.use_django_maps:
            from saml2.attribute_converter import AttributeConverter
            import importlib
            from django_saml2_framework import attributemaps

            for typ in attributemaps.django_maps:
                mod = importlib.import_module(".%s" % typ, "django_saml2_framework.attributemaps")
                for key, item in mod.__dict__.items():
                    if key.startswith("__"):
                        continue
                    if isinstance(item, dict) and "to" in item and "fro" in item:
                        atco = AttributeConverter(item["identifier"])
                        atco.from_dict(item)
                        acs.append(atco)
        if self.use_custom_maps:
            # todo: need model for this
            for attribute_map in self.custom_maps.all():
                acs.append(attribute_map.get_attribute_converter())

        return acs

    def get_entity_id(self) -> str:
        pass

    def get_config_data(self):
        return {'entityid': self.get_entity_id()}

    def pre_config(self, conf):
        """use property config to get the providers config"""
        return conf

    def post_config(self, conf):
        return conf

    @property
    def config(self):
        config = copy.deepcopy(getattr(settings, self.settings_attr, {}))
        deepmerge(config, self.get_config_data())
        conf = self.config_class()
        conf = self.pre_config(conf)
        conf.load(config)
        conf = self.post_config(conf)
        return conf

    def reload(self):
        raise NotImplementedError()


class MetadataMixin(models.Model):
    name = models.CharField(max_length=100, unique=True)
    metadata_hash = models.CharField(max_length=100, blank=True)
    # todo: add save location for this
    metadata_xml = models.FileField(blank=True)
    metadata_url = models.URLField(blank=True, help_text=_(
        'Changing this value will override the xml file.'))

    class Meta:
        abstract = True

    def __str__(self):
        if self.parent:
            return '{} ({})'.format(self.name, self.parent.name)
        return '{}'.format(self.name)

    def save(self, *args, **kwargs):
        if not (self.metadata_xml or self.metadata_url):
            raise Exception("todo: both must not be null exception")
        # restart?
        logger.info(self.metadata_hash)

        if self.metadata_url:
            self.download_metadata_xml()

        return super(MetadataMixin, self).save(*args, **kwargs)

    @property
    def parent(self):
        pass

    def download_metadata_xml(self):
        logger.info('Downloading metadata file from: {}'.format(
            self.metadata_url))
        file_name, headers = urllib.request.urlretrieve(self.metadata_url)
        with open(file_name) as f:
            xml_data = f.read()
            file_hash = hashlib.sha1(xml_data.encode()).hexdigest()
            print(self.metadata_hash, file_hash)
            if file_hash != self.metadata_hash:
                logger.info('Saving new metadata file.')
                self.metadata_hash = file_hash
                self.metadata_xml.save(
                    self.name, ContentFile(xml_data), save=False)

    @property
    def xml_path(self):
        # todo: return path to xml file
        return ''


class AttributeMixin(models.Model):
    name = models.CharField(max_length=100)
    value_path = models.CharField(max_length=100)

    class Meta:
        abstract = True


class IdentityProvider(ProviderMixin, models.Model):
    config_class = IdPConfig
    settings_attr = 'SAML2_IDP_CONFIG'

    sign_assertion = models.NullBooleanField(help_text=_(''))
    sign_response = models.NullBooleanField(help_text=_(''))

    def reload(self):
        # logger.info(self.config)
        idp_server = Server(config=self.config)
        idp_server.ticket = {}
        DSF.set_idp(self.entity, idp_server)
        if self.is_default:
            DSF.set_idp('', idp_server)

    def get_entity_id(self):
        return self.reverse('idp')

    def post_config(self, conf):
        # from saml2.attribute_converter import AttributeConverter
        # ac = AttributeConverter('urn:oasis:names:tc:SAML:2.0:attrname-format:uri')
        # ac.from_dict({
        #     'identifier': 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
        #     'fro': {'first_name': 'first_name',
        #             'LastName': 'LastName',
        #             'urn:oid:1.2.840.113549.1.9.1.1': 'email_addr',
        #             },
        #     # 'to': {'first_name': 'first_name',
        #     #        'LastName': 'LastName',
        #     #        'email_address': 'urn:oid:1.2.840.113549.1.9.1.1',},
        # })
        # # config = self.config_class()
        # # conf.attribute_converters = conf.attribute_converters + [ac]
        conf.attribute_converters = self.get_attribute_converters(conf.attribute_converters)
        return conf

    def get_config_data(self):
        config = super().get_config_data()
        idp_config = {
            'service': {
                'idp': {
                    'name': self.name,
                    'name_id_format': [self.name_id_format, ],
                    'endpoints': {
                        'single_sign_on_service': [
                            (self.reverse('idp_sso'), saml2.BINDING_HTTP_POST),
                            (self.reverse('idp_sso'), saml2.BINDING_HTTP_REDIRECT),
                        ],
                        'single_logout_service': [
                            (self.reverse('idp_slo'), saml2.BINDING_HTTP_POST),
                            (self.reverse('idp_slo'), saml2.BINDING_HTTP_REDIRECT),
                        ]
                    },
                    "policy": {
                        "default": {
                            # "lifetime": {"minutes": 15},
                            # "attribute_restrictions": None,  # means all I have
                            # "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                            "nameid_format": self.name_id_format,  # NAMEID_FORMAT_EMAILADDRESS, 
                        },
                    },
                    # 'sign_assertion': self.sign_assertion,
                    # 'sign_response': self.sign_response,
                    # "policy": {
                    #     "default": {
                    #         "lifetime": {"minutes": 15},
                    #         "attribute_restrictions": None,  # means all I have
                    #         "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
                    #     },
                    # },
                },
            },
            'metadata': {'local': []},
        }
        if self.description:
            idp_config.update(description=self.description)

        if self.sign_assertion is not None:
            idp_config['service']['idp']['sign_assertion'] = self.sign_assertion

        if self.sign_response is not None:
            idp_config['service']['idp']['sign_response'] = self.sign_response

        if self.key_file and self.cert_file:
            idp_config.update(key_file=self.key_file.path)
            idp_config.update(cert_file=self.cert_file.path)

        for sp in self.identitymetadata_set.all():
            # logger.info(sp.metadata_xml.path)
            idp_config['metadata']['local'].append(sp.metadata_xml.path)

        # todo: Encryption
        # 'encryption_keypairs': [{
        #     'key_file': BASE_DIR + '/certificates/server.key',
        #     'cert_file': BASE_DIR + '/certificates/server.crt',
        # }],

        deepmerge(config, idp_config)
        # # import pprint, io
        # # out = io.BytesIO()
        # # pprint.pprint(config, stream=out)
        # logger.info(config)
        return config


class IdentityMetadata(MetadataMixin, models.Model):
    identity_provider = models.ForeignKey(IdentityProvider, on_delete=CASCADE)

    @property
    def parent(self):
        return self.identity_provider


class IdentityAttribute(AttributeMixin, models.Model):
    identity_provider = models.ForeignKey(IdentityProvider, related_name='attributes', on_delete=CASCADE)

    class Meta:
        unique_together = (('identity_provider', 'name'),)


class ServiceProvider(ProviderMixin, models.Model):
    config_class = SPConfig
    settings_attr = 'SAML2_SP_CONFIG'

    authn_requests_signed = models.NullBooleanField(help_text=_(''))
    want_response_signed = models.NullBooleanField(help_text=_(''))
    # force_authn = models.NullBooleanField(help_text=_(''))
    # allow_unsolicited = models.NullBooleanField(help_text=_(''))
    want_assertions_signed = models.NullBooleanField(help_text=_(''))

    allow_unknown_attributes = models.NullBooleanField(
        help_text=_('If True there must be a mapping for the attribute.'))

    create_user = models.BooleanField(default=False, blank=True,
                                      help_text=_('If checked the SP will try to create new user accounts.'))

    def reload(self):
        pass

    def get_entity_id(self):
        return self.reverse('sp')

    def post_config(self, conf):
        # ac = AttributeConverter('urn:oasis:names:tc:SAML:2.0:attrname-format:uri')
        # ac.from_dict({
        #     'identifier': 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
        #     'fro': {'first_name': 'first_name',
        #             'LastName': 'LastName',
        #             'urn:oid:1.2.840.113549.1.9.1.1': 'email_address',
        #             },
        #     # 'to': {'first_name': 'first_name',
        #     #        'LastName': 'LastName',
        #     #        'email_address': 'urn:oid:1.2.840.113549.1.9.1.1',},
        # })

        # django_acs = ac_factory('django_saml2_framework/attributemaps')
        # config = self.config_class()
        conf.attribute_converters = self.get_attribute_converters(conf.attribute_converters)
        # conf.attribute_converters = [ac]
        return conf

    def get_config_data(self):
        config = super().get_config_data()
        sp_config = {
            # "attribute_map_dir": '/usr',
            # 'attribute_converters': [ac, None],
            'service': {
                'sp': {
                    'name': self.name,
                    'name_id_format': [self.name_id_format, ],
                    'endpoints': {
                        'assertion_consumer_service': [
                            (self.reverse('sp_acs'), saml2.BINDING_HTTP_POST),
                            (self.reverse('sp_acs'), saml2.BINDING_HTTP_REDIRECT),
                        ],
                        'single_logout_service': [
                            (self.reverse('sp_slo'), saml2.BINDING_HTTP_POST),
                            (self.reverse('sp_slo'), saml2.BINDING_HTTP_REDIRECT),
                        ]
                    },
                },
            },
            'metadata': {'local': []},
        }
        if self.description:
            sp_config.update(description=self.description)

        if self.authn_requests_signed is not None:
            sp_config['service']['sp']['authn_requests_signed'] = self.authn_requests_signed

        if self.want_response_signed is not None:
            sp_config['service']['sp']['want_response_signed'] = self.want_response_signed

        if self.want_assertions_signed is not None:
            sp_config['service']['sp']['want_assertions_signed'] = self.want_assertions_signed

        # attributes
        requested_attributes = []
        required_attributes = []
        optional_attributes = []
        for attribute in self.attributes.all():
            requested_attributes.append(attribute.get_config_data())
            if attribute.is_required:
                required_attributes.append(attribute.name)
            else:
                optional_attributes.append(attribute.name)
        if requested_attributes:
            sp_config['service']['sp']['requested_attributes'] = requested_attributes
            sp_config['service']['sp']['required_attributes'] = required_attributes
            sp_config['service']['sp']['optional_attributes'] = optional_attributes

        if self.key_file and self.cert_file:
            sp_config.update(key_file=self.key_file.path)
            sp_config.update(cert_file=self.cert_file.path)

        for sp in self.servicemetadata_set.all():
            # logger.info(sp.metadata_xml.path)
            sp_config['metadata']['local'].append(sp.metadata_xml.path)

        if self.allow_unknown_attributes is not None:
            sp_config['allow_unknown_attributes'] = self.allow_unknown_attributes

        deepmerge(config, sp_config)
        # logger.info(config)
        return config


class ServiceMetadata(MetadataMixin, models.Model):
    service_provider = models.ForeignKey(ServiceProvider, on_delete=CASCADE)

    @property
    def parent(self):
        return self.service_provider


class ServiceAttribute(AttributeMixin, models.Model):
    service_provider = models.ForeignKey(ServiceProvider, related_name='attributes', on_delete=CASCADE)
    is_required = models.BooleanField(default=False, help_text=_(''))
    show_in_metadata = models.BooleanField(default=True, help_text=_(''))

    class Meta:
        unique_together = (('service_provider', 'name'),)

    def get_config_data(self):
        return {
            # "name": self.name,
            "friendly_name": self.name,
            "required": self.is_required,
        }


class AttributeMap(models.Model):
    name = models.CharField(max_length=100)
    format = models.CharField(max_length=100, choices=NAME_FORMATS_SAML2)

    class Meta:
        unique_together = (('name', 'format'),)

    def __str__(self):
        return '{} ({})'.format(self.name, self.format)

    def get_attribute_converter(self):
        ac = AttributeConverter(self.format)
        ac.from_dict({
            'identifier': self.format,
            'fro': {field.local: field.remote for field in self.fields.all()},
            'to': {field.remote: field.local for field in self.fields.all()},
            # 'fro': {'first_name': 'first_name',
            #         'LastName': 'LastName',
            #         'urn:oid:1.2.840.113549.1.9.1.1': 'email_address',
            #         },
            # 'to': {'first_name': 'first_name',
            #        'LastName': 'LastName',
            #        'email_address': 'urn:oid:1.2.840.113549.1.9.1.1',},
        })
        return ac


class AttributeMapField(models.Model):
    map = models.ForeignKey(AttributeMap, related_name='fields', on_delete=CASCADE)
    local = models.CharField(max_length=100)
    remote = models.CharField(max_length=100)
