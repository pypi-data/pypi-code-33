
import aiohttp
import asyncio
import logging

from colibris import settings

from testmyesp import schemas
from testmyesp import utils

from testmyesp.hw import espctl
from testmyesp.hw import esptool

logger = logging.getLogger(__name__)


class FlashImageException(Exception):
    pass


class FlashImageWriteException(FlashImageException):
    def __init__(self, flash_image, root_cause):
        self.flash_image = flash_image
        self.root_cause = root_cause

    def __str__(self):
        return 'failed to write {}: {}'.format(self.flash_image, self.root_cause)


class FlashImageDownloadException(FlashImageException):
    def __init__(self, flash_image, root_cause):
        self.flash_image = flash_image
        self.root_cause = root_cause

    def __str__(self):
        return 'failed to download {} from {}: {}'.format(self.flash_image, self.flash_image.url, self.root_cause)


class FlashImage:
    DOWNLOAD_CONN_TIMEOUT = 5
    DOWNLOAD_READ_TIMEOUT = 30
    DOWNLOAD_RETRY_COUNT = 3

    def __init__(self, job, name, address, content=None, url=None, fill=None, size=None):
        self.job = job
        self.name = name
        self.address = int(address, 0)  # address comes as a string from schema
        self.content = content
        self.url = url
        self.fill = fill
        self.size = size

        self.logger = self.job.logger

    def __str__(self):
        return 'flash image {}@0x{:07X}'.format(self.name, self.address)

    def ensure_content(self):
        # download image if necessary
        if self.url:
            try:
                self.content = utils.run_sync(self.download())

            except Exception as e:
                self.logger.error('%s download failed: %s', self, e)
                raise FlashImageDownloadException(self, e)

        # prepare filled content
        elif self.fill is not None:
            self.content = bytes(self.size * [self.fill])

    async def ensure_content_async(self):
        # download image if necessary
        if self.url:
            try:
                self.content = await self.download()

            except Exception as e:
                self.logger.error('%s download failed: %s', self, e)
                raise FlashImageDownloadException(self, e)

        # prepare filled content
        elif self.fill is not None:
            self.content = bytes(self.size * [self.fill])

    def write(self):
        ex = None
        for t in range(settings.FLASH['image_write_tries']):
            try:
                self.write_flash_image_once()
                break

            except Exception as e:
                ex = e
                self.logger.error('%s writing failed (try %s)', self, (t + 1), exc_info=True)

        else:
            raise FlashImageWriteException(self, ex)

    async def download(self):
        for retry in range(self.DOWNLOAD_RETRY_COUNT):
            self.logger.debug('downloading %s from %s (try %d/%d)', self,
                              self.url, retry + 1, self.DOWNLOAD_RETRY_COUNT)
            try:
                async with aiohttp.ClientSession(raise_for_status=True,
                                                 read_timeout=self.DOWNLOAD_READ_TIMEOUT,
                                                 conn_timeout=self.DOWNLOAD_CONN_TIMEOUT) as session:

                    async with session.get(self.url) as response:
                        content = await response.read()
                        self.logger.debug('downloaded %s of %s bytes', self, len(content))

                        return content

            except asyncio.TimeoutError:
                if retry < self.DOWNLOAD_RETRY_COUNT - 1:
                    self.logger.error('timeout downloading %s (retrying)', self)

                else:
                    raise

    def write_flash_image_once(self):
        self.logger.debug('writing %s', self)

        esptool.write_flash(self.address, self.content)
        espctl.reset()


def write_flash_images(job, names=None):
    flash_images_list = schemas.FlashImageSchema(many=True).loads(job.flash_images_json)

    for flash_image_dict in flash_images_list:
        if (names is not None) and (flash_image_dict['name'] not in names):
            continue

        flash_image = FlashImage(job, **flash_image_dict)
        flash_image.ensure_content()
        flash_image.write()
