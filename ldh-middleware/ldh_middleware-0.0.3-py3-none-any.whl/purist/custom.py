import logging

from django.conf import settings
from django.contrib.auth.password_validation import MinimumLengthValidator as BaseValidator
from django.utils.translation import ugettext_lazy as _
from django_auth_ldap.backend import LDAPBackend as BaseBackend
from woocommerce import API as WOOCOMMERCE_API

from .models import User, UsernameValidator

log = logging.getLogger(__name__)


class AuthenticationBackend(BaseBackend):

    def __init__(self, *args, **kwargs):
        super(AuthenticationBackend, self).__init__(*args, **kwargs)

    def is_valid_jwt(self, username=None, password=None):

        is_valid = False

        try:

            jwt_wcapi = WOOCOMMERCE_API(
                url=settings.WOO_URL,
                consumer_key=settings.WOO_CONSUMER_KEY,
                consumer_secret=settings.WOO_CONSUMER_SECRET,
                wp_api=True,
                version="jwt-auth/v1",  # required for JWT Authentication
                query_string_auth=settings.WOO_QUERY_STRING_AUTH,
            )

            jwt_response = jwt_wcapi.post("token", {"username": username, "password": password})

            jwt_status = jwt_response.status_code
            jwt_token = jwt_response.json().get("token", None)
            jwt_code = jwt_response.json().get("code", None)

            known_codes = ["[jwt_auth] incorrect_password", "[jwt_auth] invalid_username"]

            if jwt_status == 200 and jwt_token is not None:
                is_valid = True
            elif jwt_status == 403 and jwt_code in known_codes:
                # recognised authentication failure
                is_valid = False
            else:
                # raise exception for an unrecognised failure
                raise Exception("Unrecognised JWT response: %s" % (jwt_response.json(),))

        except Exception as e:
            logging.exception("JWT authentication failed with an unrecognised error: %s" % (e,))
        finally:
            return is_valid

    def authenticate(self, request=None, username=None, password=None, **kwargs):
        user_model = User
        normalized_username = user_model.normalize_username(username)

        # first, validate username (even if it exists, username must be valid)

        if not settings.DEBUG_SKIP_VALIDATE_ON_AUTHENTICATION:
            validator = UsernameValidator()
            validator(username)

        # second, attempt LDAP authentication (with early exit on success)

        user = super(AuthenticationBackend, self).authenticate(request, normalized_username, password, **kwargs)

        if user is not None:
            return user

        # third, attempt WooCommerce/JWT authentication
        # (if successful, create and return LDAP user, otherwise return None)

        if self.is_valid_jwt(normalized_username, password):

            # try to get a preexisting user object
            # otherwise create a new one

            try:
                user = user_model.objects.get(username=username)
            except user_model.DoesNotExist:
                user = user_model(username=username, email=None)

            # update/set user details
            user.email = user.get_identity()
            user.set_password(password)
            user.save()

            return super(AuthenticationBackend, self).authenticate(request, normalized_username, password, **kwargs)
        else:
            return None


class PassphraseValidator(BaseValidator):
    # TODO: bundle in all the other validators from django.contrib.auth.password_validation

    def __init__(self, min_length=15, *args, **kwargs):
        super(PassphraseValidator, self).__init__(min_length, *args, **kwargs)

    def get_help_text(self):
        return _("A good passphrase is made of at least three long words.")
