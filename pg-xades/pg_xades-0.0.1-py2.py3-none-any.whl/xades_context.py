# -*- coding: utf-8 -*-
# © 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from os import path

from lxml import etree

from pgxmlsig import SignatureContext, utils, constants
from pgxmlsig.utils import b64_print
from cryptography.hazmat.primitives import serialization
from .constants import NS_MAP, EtsiNS
from datetime import datetime
import pytz
import base64
from cryptography.x509.oid import ExtensionOID
from . import policy


from cryptography.x509 import oid


class XAdESContext(SignatureContext):
    def __init__(self, policy):
        """
        Declaration
        :param policy: Policy class
        :type policy: xades.Policy
        """
        self.policy = policy
        super(XAdESContext, self).__init__()

    def sign(self, node):
        """
        Signs a node
        :param node: Signature node
        :type node: lxml.etree.Element
        :return: None 
        """

        signed_properties = node.find(
            "ds:Object/xades:QualifyingProperties["
            "@Target='#{}']/xades:SignedProperties".format(
                node.get('Id')),
            namespaces=NS_MAP)
        assert signed_properties is not None
        self.calculate_signed_properties(signed_properties, node, True)
        unsigned_properties = node.find(
            "ds:Object/xades:QualifyingProperties["
            "@Target='#{}']/xades:UnSignedProperties".format(
                node.get('Id')),
            namespaces=NS_MAP)
        if unsigned_properties is not None:
            self.calculate_unsigned_properties(signed_properties, node, True)

        res = super(XAdESContext, self).sign(node)
        return res

    def verify(self, node):
        """
        verifies a signature
        :param node: Signature node
        :type node: lxml.etree.Element
        :return: 
        """
        schema = etree.XMLSchema(etree.parse(path.join(
            path.dirname(__file__), "data/XAdES.xsd"
        )))
        schema.assertValid(node)
        signed_properties = node.find(
            "ds:Object/xades:QualifyingProperties["
            "@Target='#{}']/xades:SignedProperties".format(
                node.get('Id')),
            namespaces=NS_MAP)
        assert signed_properties is not None
        self.calculate_signed_properties(signed_properties, node, False)
        unsigned_properties = node.find(
            "ds:Object/xades:QualifyingProperties["
            "@Target='#{}']/xades:UnSignedProperties".format(
                node.get('Id')),
            namespaces=NS_MAP)
        if unsigned_properties is not None:
            self.calculate_unsigned_properties(signed_properties, node, False)
        res = super(XAdESContext, self).verify(node)
        return res

    def calculate_signed_properties(self, signed_properties, node, sign=False):
        signature_properties = signed_properties.find(
            'xades:SignedSignatureProperties', namespaces=NS_MAP
        )
        assert signature_properties is not None
        self.calculate_signature_properties(signature_properties, node, sign)
        data_object_properties = signed_properties.find(
            'xades:SignedDataObjectProperties', namespaces=NS_MAP
        )
        if signature_properties is None:
            self.calculate_data_object_properties(
                data_object_properties, node, sign
            )
        return

    def calculate_signature_properties(
            self, signature_properties, node, sign=False):
        signing_time = signature_properties.find(
            'xades:SigningTime', namespaces=NS_MAP
        )
        assert signing_time is not None


        if sign and signing_time.text is None:
            now = pytz.timezone('America/Bogota').localize(datetime.now())
            signing_time.text = now.isoformat()

        certificate_list = signature_properties.find(
            'xades:SigningCertificate', namespaces=NS_MAP
        )
        assert certificate_list is not None
        if sign:
            self.policy.calculate_certificate(certificate_list, self.x509)
        else:
            self.policy.validate_certificate(certificate_list, node)
        policy = signature_properties.find(
            'xades:SignaturePolicyIdentifier', namespaces=NS_MAP
        )
        assert policy is not None
        self.policy.calculate_policy_node(policy, sign)

    def calculate_data_object_properties(self, data_object_properties, node, sign=False):
        return

    def calculate_unsigned_properties(self, unsigned_properties, node, sign=False):
        return
    """
    def fill_x509_data(self, x509_data):
        x509_issuer_serial = x509_data.find(
            'ds:X509IssuerSerial', namespaces=constants.NS_MAP
        )
        if x509_issuer_serial is not None:
            self.fill_x509_issuer_name(x509_issuer_serial)

        x509_crl = x509_data.find('ds:X509CRL', namespaces=constants.NS_MAP)
        if x509_crl is not None and self.crl is not None:
            x509_data.text = base64.b64encode(
                self.crl.public_bytes(serialization.Encoding.DER)
            )
        x509_subject = x509_data.find(
            'ds:X509SubjectName', namespaces=constants.NS_MAP
        )
        if x509_subject is not None:
            x509_subject.text = self.get_rdns_name(self.x509.subject.rdns)
        x509_ski = x509_data.find('ds:X509SKI', namespaces=constants.NS_MAP)
        if x509_ski is not None:
            x509_ski.text = base64.b64encode(
                self.x509.extensions.get_extension_for_oid(
                    ExtensionOID.SUBJECT_KEY_IDENTIFIER
                ).value.digest)
        x509_certificate = x509_data.find(
            'ds:X509Certificate', namespaces=constants.NS_MAP
        )
        if x509_certificate is not None:
            s = base64.b64encode(
                self.x509.public_bytes(encoding=serialization.Encoding.DER)
            )
            x509_certificate.text = b64_print(s)

    def fill_x509_issuer_name(self, x509_issuer_serial):
        x509_issuer_name = x509_issuer_serial.find(
            'ds:X509IssuerName', namespaces=constants.NS_MAP
        )
        if x509_issuer_name is not None:
            x509_issuer_name.text = self.get_rdns_name(self.x509.issuer.rdns)
        x509_issuer_number = x509_issuer_serial.find(
            'ds:X509SerialNumber', namespaces=constants.NS_MAP
        )
        if x509_issuer_number is not None:
            x509_issuer_number.text = str(self.x509.serial_number)
    """

