
import logging
import threading
import time

from .exceptions import *


logger = logging.getLogger(__name__)

all_instructions = {}


def register_instruction(cls):
    all_instructions[cls.NAME] = cls

    return cls


def get_instruction_class(name):
    return all_instructions.get(name)


from .base import BaseInstruction

from testmyesp.availableinstructions import *


def _execute_instruction(instruction):
    try:
        instruction.execute()

    except InstructionException as e:
        instruction.logger.error('failed: %s', e)

        raise

    except Exception as e:
        instruction.logger.error('failed: %s', e, exc_info=True)

        raise

    instruction.logger.debug('succeeded')


def _execute_instruction_delayed(instruction, delay):
    time.sleep(delay / 1000.0)
    _execute_instruction(instruction)


def _fire_and_forget(instruction, delay):
    thread = threading.Thread(target=_execute_instruction_delayed, args=(instruction, delay))
    thread.start()


def execute_instruction(test_case, instruction_dict, serial):
    try:
        instruction = BaseInstruction.from_dict(instruction_dict)

    except NoSuchInstruction as e:
        test_case.logger.error('unknown instruction %s', e)
        raise

    except InvalidInstructionParameters as e:
        test_case.logger.error('invalid instruction parameters: %s', e)
        raise

    except Exception as e:
        test_case.logger.error('failed to create instruction: %s', e, exc_info=True)
        raise

    test_case.memory_logs_handler.set_instruction(instruction)

    instruction.set_logger(test_case.logger)
    instruction.set_serial(serial)
    instruction.set_test_case(test_case)

    if instruction_dict['fire_and_forget']:
        instruction.logger.debug('executing (fire and forget, delayed with %sms)', instruction_dict['fire_delay'])
        _fire_and_forget(instruction, instruction_dict['fire_delay'])

    else:
        instruction.logger.debug('executing')
        _execute_instruction(instruction)

    return instruction
