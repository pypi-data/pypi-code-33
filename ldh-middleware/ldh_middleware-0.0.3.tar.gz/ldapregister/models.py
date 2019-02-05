import logging

import ldap
import ldapdb.models
import pyasn1.codec.ber.encoder
import pyasn1.type.namedtype
import pyasn1.type.univ
from django.conf import settings
from django.db import connections, router
from ldapdb.models.fields import CharField, ListField

log = logging.getLogger(__name__)


class LdapGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP group entry.
    """

    class Meta:
        verbose_name = "LDAP group"
        verbose_name_plural = "LDAP groups"

    # LDAP meta-data
    base_dn = settings.REG_GROUP_BASE_DN
    object_classes = settings.REG_GROUP_OBJECT_CLASSES

    # LDAP group attributes
    cn = CharField(db_column='cn', max_length=200, primary_key=True)
    description = CharField(db_column='description', max_length=200)
    members = ListField(db_column='member')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class LdapPerson(ldapdb.models.Model):
    """
    Class for representing an LDAP person entry.
    """

    class Meta:
        verbose_name = "LDAP person"
        verbose_name_plural = "LDAP people"

    # LDAP meta-data
    base_dn = settings.REG_PERSON_BASE_DN
    object_classes = settings.REG_PERSON_OBJECT_CLASSES

    # Minimal attributes
    uid = CharField(db_column='uid', max_length=200, primary_key=True)
    cn = CharField(db_column='cn', max_length=200)
    description = CharField(db_column='description', max_length=200)
    sn = CharField(db_column='sn', max_length=200)
    mail = CharField(db_column='mail', max_length=200)

    def __str__(self):
        return self.uid

    def __unicode__(self):
        return self.uid

    def change_password(self, raw_password, using=None):
        # dig into the ldapdb primitives
        using = using or router.db_for_write(self.__class__, instance=self)
        connection = connections[using]
        cursor = connection._cursor()

        # call pyldap_orm password modification
        cursor.connection.extop_s(PasswordModify(self.dn, raw_password))


# The following code taken from https://github.com/asyd/pyldap_orm/blob/master/pyldap_orm/controls.py
# Copyright 2016 Bruno Bonfils
# SPDX-License-Identifier: Apache-2.0 (no NOTICE file)


class PasswordModify(ldap.extop.ExtendedRequest):
    """
    Implements RFC 3062, LDAP Password Modify Extended Operation
    Reference: https://www.ietf.org/rfc/rfc3062.txt
    """

    def __init__(self, identity, new, current=None):
        self.requestName = '1.3.6.1.4.1.4203.1.11.1'
        self.identity = identity
        self.new = new
        self.current = current

    def encodedRequestValue(self):
        request = self.PasswdModifyRequestValue()
        request.setComponentByName('userIdentity', self.identity)
        if self.current is not None:
            request.setComponentByName('oldPasswd', self.current)
        request.setComponentByName('newPasswd', self.new)
        return pyasn1.codec.ber.encoder.encode(request)

    class PasswdModifyRequestValue(pyasn1.type.univ.Sequence):
        """
        PyASN1 representation of:
            PasswdModifyRequestValue ::= SEQUENCE {
            userIdentity    [0]  OCTET STRING OPTIONAL
            oldPasswd       [1]  OCTET STRING OPTIONAL
            newPasswd       [2]  OCTET STRING OPTIONAL }
        """
        componentType = pyasn1.type.namedtype.NamedTypes(
            pyasn1.type.namedtype.OptionalNamedType(
                'userIdentity',
                pyasn1.type.univ.OctetString().subtype(
                    implicitTag=pyasn1.type.tag.Tag(pyasn1.type.tag.tagClassContext, pyasn1.type.tag.tagFormatSimple, 0)
                )),
            pyasn1.type.namedtype.OptionalNamedType(
                'oldPasswd',
                pyasn1.type.univ.OctetString().subtype(
                    implicitTag=pyasn1.type.tag.Tag(pyasn1.type.tag.tagClassContext, pyasn1.type.tag.tagFormatSimple, 1)
                )),
            pyasn1.type.namedtype.OptionalNamedType(
                'newPasswd',
                pyasn1.type.univ.OctetString().subtype(
                    implicitTag=pyasn1.type.tag.Tag(pyasn1.type.tag.tagClassContext, pyasn1.type.tag.tagFormatSimple, 2)
                )),
        )
