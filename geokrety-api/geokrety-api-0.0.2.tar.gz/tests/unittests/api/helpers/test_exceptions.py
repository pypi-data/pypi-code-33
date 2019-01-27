from app.api.helpers.exceptions import (AuthenticationRequired,
                                        ConflictException, ForbiddenException,
                                        MethodNotAllowed, UnprocessableEntity)
from tests.unittests.utils.base_test_case import BaseTestCase


class TestExceptionsHelperValidation(BaseTestCase):

    def test_exceptions(self):
        """Check ExceptionsHelper: exceptions types"""
        # Unprocessable Entity Exception
        with self.assertRaises(UnprocessableEntity):
            raise UnprocessableEntity({'pointer': '/data/attributes/min-quantity'},
                                      "min-quantity should be less than max-quantity")

        # Conflict Exception
        with self.assertRaises(ConflictException):
            raise ConflictException({'pointer': '/data/attributes/email'}, "Email already exists")

        # Authentication Required Exception
        with self.assertRaises(AuthenticationRequired):
            raise AuthenticationRequired({'source': ''}, "Authentication Required")

        # Forbidden Exception
        with self.assertRaises(ForbiddenException):
            raise ForbiddenException({'source': ''}, "Access Forbidden")

        # Method Not Allowed Exception
        with self.assertRaises(MethodNotAllowed):
            raise MethodNotAllowed({'source': ''}, "Method Not Allowed")
