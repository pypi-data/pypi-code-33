
import re

from colibris import schemas
from colibris import settings

from testmyesp import flashimages
from testmyesp import schemafields

from testmyesp.hw import espctl
from testmyesp.hw import esptool
from testmyesp.instructions import BaseInstruction, register_instruction, InstructionException


class UnexpectedFlashContent(InstructionException):
    def __init__(self, address):
        self.address = address

    def __str__(self):
        return 'unexpected flash content at 0x{:07X}'.format(self.address)


@register_instruction
class WriteFlashImage(BaseInstruction):
    NAME = 'write-flash-image'

    def __init__(self, name, address, content=None, url=None, fill=None, size=None):
        self.name = name
        self.address = address
        self.content = content
        self.url = url
        self.fill = fill
        self.size = size

        super().__init__()

    def execute(self):
        espctl.set_boot_mode(espctl.BOOT_MODE_FLASH)
        espctl.reset()

        flash_image = self.make_flash_image()
        flash_image.ensure_content()
        flash_image.write()

        espctl.set_boot_mode(espctl.BOOT_MODE_FLASH)
        espctl.reset()

    def make_flash_image(self):
        return flashimages.FlashImage(self.test_case.job, self.name, self.address, self.content,
                                      self.url, self.fill, self.size)

    class Schema(schemas.Schema):
        name = schemas.fields.String(required=True, validate=schemas.validate.Regexp(r'^[\w_-]+$', re.IGNORECASE))
        address = schemas.fields.String(validate=schemas.validate.Regexp('^[x0-9a-fA-F]+$'), required=True)
        content = schemafields.Base64Field()
        url = schemas.fields.URL()
        fill = schemas.fields.Integer(validate=schemas.validate.Range(0, 255))
        size = schemas.fields.Integer(validate=schemas.validate.Range(0, settings.FLASH['size'] * 1024))

        @schemas.validates_schema
        def validate_content_size(self, data):
            if 'content' in data:
                if int(data['address'], 0) + len(data['content']) > settings.FLASH['size'] * 1024:
                    raise schemas.ValidationError('Content is out of memory range.')

        @schemas.validates_schema
        def validate_some_content(self, data):
            if 'content' not in data and 'url' not in data and 'fill' not in data:
                raise schemas.ValidationError('Either content, URL or fill must be supplied.')

        @schemas.validates_schema
        def validate_fill(self, data):
            if 'fill' in data and 'size' not in data:
                raise schemas.ValidationError('Size is required when fill is supplied.')


@register_instruction
class ReadFlashImage(BaseInstruction):
    NAME = 'read-flash-image'

    def __init__(self, address, expected_content):
        self.address = int(address, 0)
        self.expected_content = expected_content

        super().__init__()

    def execute(self):
        espctl.set_boot_mode(espctl.BOOT_MODE_FLASH)
        espctl.reset()

        got_content = esptool.read_flash(self.address, len(self.expected_content))

        espctl.set_boot_mode(espctl.BOOT_MODE_FLASH)
        espctl.reset()

        if got_content != self.expected_content:
            raise UnexpectedFlashContent(self.address)

    class Schema(schemas.Schema):
        address = schemas.fields.String(validate=schemas.validate.Regexp('^[x0-9a-fA-F]+$'), required=True)
        expected_content = schemafields.Base64Field(required=True)
