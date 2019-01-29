from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from asn1crypto.core import UTF8String
from asn1crypto.pem import unarmor
from asn1crypto.x509 import Certificate, GeneralName
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptokey import asn1utils
from cryptokey.backend.cryptography import backend
from cryptokey.backend.cryptography.rsa import RsaPrivateKey
from cryptokey.hashes import sha2_256
from cryptokey.public.key import PrivateKey
from cryptokey.public.rsa import RsaScheme


def load_private_key(path: Path) -> PrivateKey:
    logging.info('Loading private key in %s', path.absolute().resolve())

    with path.open('rb') as fp:
        key = RsaPrivateKey(serialization.load_pem_private_key(
            fp.read(),
            password=None,
            backend=backend,
        ))
        key.default_scheme = RsaScheme.PKCS1v1_5
        key.default_hash_algorithm = sha2_256()
        return key


def gen_private_key(path: Path, algo: str, params: Mapping[str, Any]) -> PrivateKey:
    logging.info('Creating private %s key in %s', algo, path.absolute().resolve())
    if algo == 'rsa':
        key = RsaPrivateKey(rsa.generate_private_key(
            public_exponent=int(params['exp']),
            key_size=int(params['bits']),
            backend=backend,
        ))
        key.default_scheme = RsaScheme.PKCS1v1_5
        key.default_hash_algorithm = sha2_256()
    else:
        raise NotImplementedError(f'Algorithm {algo!r} not supported')

    try:
        old_umask = os.umask(0o177)
        with path.open('xt') as fp:
            fp.write(key.export_private_pem())
    finally:
        os.umask(old_umask)

    return key


def load_or_gen_private_key(path: Path, algo: str, params: Mapping[str, Any]) -> PrivateKey:
    try:
        return load_private_key(path)
    except FileNotFoundError:
        return gen_private_key(path, algo, params)


async def build_csr(key: PrivateKey, domains: Sequence[str]) -> bytes:
    extensions = [
        {
            'extn_id': 'subject_alt_name',
            'critical': False,
            'extn_value': [
                GeneralName(name='dns_name', value=dom)
                for dom in domains
            ],
        },
    ]
    attr = [
        {
            'type': 'extension_request',
            'values': [extensions],
        },
    ]

    return await asn1utils.build_csr(key, [('common_name', UTF8String(domains[0]))], attr)


def cert_expiry(cert: bytes) -> float:
    cert = Certificate.load(unarmor(cert)[2])
    now = datetime.now(tz=timezone.utc)
    valid_to = cert['tbs_certificate']['validity']['not_after'].native
    seconds_left = (valid_to - now).total_seconds()
    return seconds_left / 86400
