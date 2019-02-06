# -*- coding: utf-8 -*-
# © 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from cryptography.hazmat.primitives import hashes

from pgxmlsig import constants
from .ns import EtsiNS



NS_MAP = {
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    'fe' : 'http://www.dian.gov.co/contratos/facturaelectronica/v1',
    'cac' : 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc' : 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'clm54217' : 'urn:un:unece:uncefact:codelist:specification:54217:2001',
    'clm66411' : 'urn:un:unece:uncefact:codelist:specification:66411:2001',
    'clmIANAMIMEMediaType' : 'urn:un:unece:uncefact:codelist:specification:IANAMIMEMediaType:2003',
    'ext' : 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'qdt' : 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2',
    'sts' : 'http://www.dian.gov.co/contratos/facturaelectronica/v1/Structures',
    'udt' : 'urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2',
    'xsi' : 'http://www.w3.org/2001/XMLSchema-instance',
    'ds11': 'http://www.w3.org/2009/xmldsig11#',
    'xades': 'http://uri.etsi.org/01903/v1.3.2#',
    'xades141': 'http://uri.etsi.org/01903/v1.4.1#'
    }

MAP_HASHLIB = {
    constants.TransformMd5: hashes.MD5,
    constants.TransformSha1: hashes.SHA1,
    constants.TransformSha224: hashes.SHA224,
    constants.TransformSha256: hashes.SHA256,
    constants.TransformSha384: hashes.SHA384,
    constants.TransformSha512: hashes.SHA512,
}
