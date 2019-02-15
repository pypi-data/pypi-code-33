'''Validator and Validations.'''
import re
import inspect
from base64 import (b64decode)
from dataclasses import (dataclass)
from uuid import (UUID)
from typing import (
    cast,
    Any,
    Awaitable,
    Callable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)
from .validation_result import (ValidationResult)

EMPTY_UUID = UUID(fields=(0, 0, 0, 0, 0, 0))
EMPTY_BYTES = b''

Record = Mapping[str, Any]
MutableRecord = MutableMapping[str, Any]
TryParseResult = Tuple[bool, Any]
ValidateFieldSync = Callable[[Any], bool]
ValidateFieldAsync = Callable[[Any], Awaitable[bool]]
ValidateField = Union[ValidateFieldSync, ValidateFieldAsync]
ValidateRecordSync = Callable[[Record], bool]
ValidateRecordAsync = Callable[[Record], Awaitable[bool]]
ValidateRecord = Union[ValidateRecordSync, ValidateRecordAsync]
ValidateTryParseSync = Callable[[Any], TryParseResult]
ValidateTryParseAsync = Callable[[Any], Awaitable[TryParseResult]]
ValidateTryParse = Union[ValidateTryParseSync, ValidateTryParseAsync]

@dataclass
class FieldValidator:
  '''Information to validate a single field.'''
  field_name: str
  message: str
  validator: ValidateField

  async def validate(self, value: Any) -> bool:
    '''Properly calls the validator.'''
    if inspect.iscoroutinefunction(self.validator):
      return await cast(ValidateFieldAsync, self.validator)(value)
    return cast(ValidateFieldSync, self.validator)(value)

@dataclass
class RecordValidator:
  '''Information to validate a whole record.'''
  message: str
  validator: ValidateRecord
  field_name: Optional[str]

  async def validate(self, record: Record) -> bool:
    '''Properly calls the validator.'''
    if inspect.iscoroutinefunction(self.validator):
      return await cast(ValidateRecordAsync, self.validator)(record)
    return cast(ValidateRecordSync, self.validator)(record)

@dataclass
class TryParseValidator:
  '''Information to try to parse a single field.'''
  field_name: str
  message: str
  validator: ValidateTryParse

  async def validate(self, value: Any) -> TryParseResult:
    '''Properly calls the validator.'''
    if inspect.iscoroutinefunction(self.validator):
      return await cast(ValidateTryParseAsync, self.validator)(value)
    return cast(ValidateTryParseSync, self.validator)(value)

ValidatorType = Union[FieldValidator, RecordValidator, TryParseValidator]

class Validator:
  '''Records validators for a record.'''
  def __init__(self, validators: Optional[List[ValidatorType]] = None):
    self.validators: List[ValidatorType] = validators or []

  @staticmethod
  def field(field_name, message: str, validate: ValidateField) -> FieldValidator:
    return FieldValidator(field_name, message, validate)

  @staticmethod
  def record(message: str, validate: ValidateRecord, field_name: str = None) -> RecordValidator:
    return RecordValidator(message, validate, field_name)

  @staticmethod
  def try_parse(
      field_name: str,
      message: str,
      validate: ValidateTryParse,
  ) -> TryParseValidator:
    '''Builds a TryParseValidator'''
    return TryParseValidator(field_name, message, validate)

  async def validate(self, record: Record) -> ValidationResult[MutableRecord]:
    return await ValidatorInstance(self, record).validate()

class ValidatorInstance:
  '''Holds results for a run of validation.'''
  def __init__(self, validator: Validator, record: Record) -> None:
    self.validator = validator
    self.record = record
    self.output: MutableRecord = {}
    self.validation_result = ValidationResult[MutableRecord](None)

  async def validate(self) -> ValidationResult[MutableRecord]:
    '''Executes all validators against the record until one fails.'''
    for validator in self.validator.validators:
      if isinstance(validator, FieldValidator):
        await self.validate_field(validator)
      elif isinstance(validator, RecordValidator):
        await self.validate_record(validator)
      elif isinstance(validator, TryParseValidator):
        await self.try_parse_field(validator)
      else:
        raise Exception('Invalid validator')

      if not self.validation_result:
        return self.validation_result

    record = self.record or {}
    output = {**record, **self.output}
    self.validation_result.set_output(output)
    return self.validation_result

  async def validate_field(self, validator: FieldValidator) -> None:
    '''Validate a single field.'''
    field_name = validator.field_name

    if field_name not in self.output:
      value = self.record.get(field_name, None)
      self.output[field_name] = value
    else:
      value = self.output[field_name]

    result = await validator.validate(value)

    if not result:
      self.validation_result.add_message(field_name, validator.message)

  async def validate_record(self, validator: RecordValidator) -> None:
    '''Validate an entire record.'''
    record: Record

    if self.record:
      record = {**self.record, **self.output}
    else:
      record = self.output

    result = await validator.validate(record)

    if not result:
      if validator.field_name:
        self.validation_result.add_message(validator.field_name, validator.message)
      else:
        self.validation_result.add_general_message(validator.message)

  async def try_parse_field(self, validator: TryParseValidator) -> None:
    '''Try to parse a field.'''
    field_name = validator.field_name

    if field_name not in self.output:
      value = self.record.get(field_name, None)
      self.output[field_name] = value
    else:
      value = self.output[field_name]

    (is_ok, output) = await validator.validate(value)

    if is_ok:
      self.output[field_name] = output
    else:
      self.validation_result.add_message(field_name, validator.message)

class Validators:
  '''Contains validator methods.'''
  @staticmethod
  def is_present(val: Any) -> bool:
    '''Makes sure a value is present.'''
    if val is None:
      return False
    if val == 0:
      return True
    return bool(val)

  @staticmethod
  def is_match(pattern: str) -> Callable[[str], bool]:
    '''Makes sure a string matches a value.'''
    def matcher(val: str) -> bool:
      if val is None:
        return False
      return bool(re.match(pattern, val))
    return matcher

  @staticmethod
  def optional(validator: Callable[[Any], Any]) -> Callable[[Any], Any]:
    '''Wraps a validator in an optional flag allowing None values.'''
    def checker(val: Any) -> bool:
      if val is None:
        return True
      return validator(val)
    return checker

  @staticmethod
  def try_parse_optional(
      validator: Callable[[Any], TryParseResult],
  ) -> Callable[[Any], TryParseResult]:
    '''Wraps a validator in an optional flag allowing None values.'''
    def checker(val: Any) -> TryParseResult:
      if val is None:
        return (True, val)
      return validator(val)
    return checker

  @staticmethod
  def try_parse_int(val: Any) -> Tuple[bool, int]:
    '''Tries to parse an int.'''
    if val is None:
      return (False, 0)
    try:
      return (True, int(val))
    except ValueError:
      return (False, 0)

  @staticmethod
  def try_parse_float(val: Any) -> Tuple[bool, float]:
    '''Tries to parse a float.'''
    if val is None:
      return (False, 0.0)
    try:
      return (True, float(val))
    except ValueError:
      return (False, 0.0)

  @staticmethod
  def try_parse_base64(val: Any) -> Tuple[bool, bytes]:
    '''Tries to parse a base64 string to bytes.'''
    if val is None:
      return (False, EMPTY_BYTES)
    try:
      return (True, b64decode(val, validate=True))
    except ValueError:
      return (False, EMPTY_BYTES)

  @staticmethod
  def try_parse_uuid(val: Any) -> Tuple[bool, UUID]:
    '''Tries to parse a UUID.'''
    if val is None:
      return (False, EMPTY_UUID)
    if isinstance(val, UUID):
      return (True, val)
    try:
      return (True, UUID(val))
    except (ValueError, TypeError):
      return (False, EMPTY_UUID)

  @staticmethod
  def is_length(min_len: Optional[int], max_len: Optional[int]) -> Callable[[str], bool]:
    '''Checks if a string is in length bounds.'''
    def checker(val: str) -> bool:
      if min_len is not None and len(val) < min_len:
        return False
      if max_len is not None and max_len < len(val):
        return False
      return True
    return checker
