#!/home/hacmec/.local/venv/hacmec/bin/python

from __future__ import annotations

import logging
import subprocess
from contextlib import suppress
from pathlib import Path
from time import sleep, time
from typing import Mapping
from urllib.parse import quote

from hacmec import problem
from hacmec.client import (AcmeAccount, AcmeChallengeDns01, AcmeIdentifier,
                           Hacmec)
from hacmec.http import aiohttp

from . import VERSION
from .config import Config, ConfigCertificate
from .crypto import (build_csr, cert_expiry, gen_private_key,
                     load_or_gen_private_key)
from .dnsupdate import poll_dns, update_txt


class AcmeCert:
    def __init__(self, client: AcmeClient, basepath: Path, config: ConfigCertificate) -> None:
        self.client = client
        self.config = config
        self.path = basepath.joinpath(quote(config.name, safe=''))
        self.path.mkdir(exist_ok=True)

    @property
    def is_current_okay(self) -> bool:
        try:
            with self.path.joinpath('current.crt').open('rb') as fp:
                days = cert_expiry(fp.read())
        except FileNotFoundError:
            return False
        except Exception:
            logging.exception('Cannot read current cert')
            return False
        if days < 32:
            return False
        return True

    async def solve_challenges(self) -> None:
        records = {}
        for auth in self.order.authorizations:
            await auth.update()
            for chall in auth.challenges:
                if isinstance(chall, AcmeChallengeDns01):
                    records[chall.fqdn] = chall.txt_record
        await self.client.solve_dns(records)

        for auth in self.order.authorizations:
            for chall in auth.challenges:
                if isinstance(chall, AcmeChallengeDns01):
                    await chall.respond()

        broken = False
        while True:
            done = True
            for auth in self.order.authorizations:
                if auth.status == 'pending':
                    await auth.update()

                if auth.status == 'pending':
                    done = False
                elif auth.status != 'valid':
                    broken = True
            if done:
                break
            sleep(5)

        if broken:
            for auth in self.order.authorizations:
                if auth.status != 'valid':
                    logging.error(f'Authorization failed: {auth.url} {auth.identifier}')
            raise Exception('Authorization failed')

    async def wait_order_ready(self) -> None:
        while self.order.status == 'pending':
            logging.info('Polling order')
            await self.order.update()
            if self.order.status == 'pending':
                sleep(5)

        if self.order.status != 'ready':
            raise Exception(f'Order failed: {self.order.status}')

    async def fetch_cert(self) -> bytes:
        while self.order.status == 'processing':
            logging.info('Polling order')
            await self.order.update()
            if self.order.status == 'processing':
                sleep(5)
        if self.order.status != 'valid':
            raise Exception(f'Order status: {self.order.status}')

        logging.info('Downloading certificate')
        return await self.order.download()

    async def acquire(self) -> None:
        logging.info(f'Acquring certificate {self.config.name!r}')
        if self.is_current_okay:
            logging.info('Nothing to do')
            return

        account = await self.client.account
        logging.info(f'Sending new order for domains {self.config.domains}')
        self.order = await account.new_order(map(AcmeIdentifier.dns, self.config.domains))
        await self.solve_challenges()
        await self.wait_order_ready()
        name = str(int(time()))
        keypath = self.path.joinpath(name + '.key')
        crtpath = self.path.joinpath(name + '.crt')
        key = gen_private_key(keypath, self.config.algo, self.config.params)
        logging.info('Sending CSR')
        csr = await build_csr(key, self.config.domains)
        await self.order.send_csr(csr)
        cert = await self.fetch_cert()
        logging.info(f'Writing new cert to {crtpath}')
        with crtpath.open('wb') as fp:
            fp.write(cert)

        cur_crt = self.path.joinpath('current.crt')
        cur_key = self.path.joinpath('current.key')

        logging.info('Setting symlink from current.crt/current.key')
        with suppress(FileNotFoundError):
            cur_crt.unlink()
        with suppress(FileNotFoundError):
            cur_key.unlink()

        cur_crt.symlink_to(crtpath.name)
        cur_key.symlink_to(keypath.name)

        for cmd in self.config.on_update:
            logging.info(f'Running update hook: {cmd!r}')
            subprocess.run(cmd, shell=True)


class AcmeClient:
    def __init__(self, config: Config, http) -> None:
        self.config = config
        self.http = http
        self.certs = [
            AcmeCert(self, config.basepath, cert_config)
            for cert_config in config.certificates
        ]

    @property
    async def acme(self) -> Hacmec:
        with suppress(AttributeError):
            return self._acme
        acme = Hacmec(self.http)
        await acme.load_directory(self.config.account.endpoint)
        self._acme = acme
        return self._acme

    @property
    async def is_tos_agreed(self) -> bool:
        try:
            tos = (await self.acme).directory.terms_of_service
        except KeyError:
            return False

        if self.config.account.accepted_tos == tos:
            return True

        raise Exception(f'You need to set account.accepted_tos to: {tos!r}')

    @property
    async def account(self) -> AcmeAccount:
        with suppress(AttributeError):
            return self._account

        config = self.config.account
        acme = await self.acme
        private_key = load_or_gen_private_key(self.config.basepath.joinpath(config.key), config.algo, config.params)
        try:
            acc = await acme.find_account(private_key)
        except problem.AcmeProblemAccountDoesNotExist:
            logging.info('Account does not exist yet')
            acc = await acme.register_account(private_key, config.contacts, await self.is_tos_agreed)
        logging.info('Using account %s', acc.kid)
        if acc.status != 'valid':
            raise Exception(f'Cannot use account in status {acc.status!r}')
        self._account = acc
        return acc

    async def solve_dns(self, records: Mapping[str, str]) -> None:
        zone_records: Mapping[str, Mapping[str, str]] = {}
        for fqdn, value in records.items():
            best_zone = max((
                zone
                for zone in self.config.zones.keys()
                if fqdn.rstrip('.').endswith(zone)
            ), key=len, default='')

            if not best_zone:
                raise Exception(f'No zone found for {fqdn!r}')

            zone_records.setdefault(best_zone, {})[fqdn] = value

        for zone, records in zone_records.items():
            conf = self.config.zones[zone]
            logging.info(f'Updating DNS records on {conf.server!r} / {zone!r}:')
            for name, value in sorted(records.items()):
                logging.info(f'  {name!r} --> {value!r}')
            update_txt(conf.server, conf.key, conf.secret, conf.algo, zone, records, 60)

        poll_dns(zone_records)

    async def run(self) -> None:
        for cert in self.certs:
            await cert.acquire()


async def demo(config: Config) -> None:
    async with aiohttp.AioHttpClient(f'hACMEc-Demo/{VERSION}', 'en') as http:
        await AcmeClient(config, http).run()
