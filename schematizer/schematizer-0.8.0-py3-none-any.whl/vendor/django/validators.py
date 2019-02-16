from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from common.schematizer.exceptions import CompoundValidationError, SimpleValidationError
from common.schematizer.validators import BaseValidator


class Email(BaseValidator):
    def validate_native(self, obj):
        try:
            validate_email(obj)
        except ValidationError as exc:
            raise SimpleValidationError(exc.code.upper(), extra={'message': exc.message}) from exc


class Password(BaseValidator):
    def validate_native(self, obj):
        try:
            validate_password(obj)
        except ValidationError as exc:
            errors = []
            for error in exc.error_list:
                extra = dict(error.params) if error.params else {}
                extra.update(message=error.message % extra)
                errors.append(
                    SimpleValidationError(error.code.upper(), extra=extra),
                )
            raise CompoundValidationError(errors) from exc
