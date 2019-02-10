
import time

from colibris import schemas
from colibris import settings

from testmyesp.instructions import BaseInstruction, register_instruction


@register_instruction
class Sleep(BaseInstruction):
    NAME = 'sleep'

    def __init__(self, duration):
        self.duration = duration

        super().__init__()

    def execute(self):
        self.logger.debug('going to sleep for %d milliseconds', self.duration)
        time.sleep(self.duration / 1000.0)
        self.logger.debug('woke up')

    class Schema(schemas.Schema):
        duration = schemas.fields.Integer(required=True,
                                          validate=schemas.validate.Range(1, settings.MAX_JOB_TIME * 1000))


@register_instruction
class Noop(BaseInstruction):
    NAME = 'noop'

    def execute(self):
        self.logger.debug('noop')
