import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out

from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser

from generic.exceptions import (ValidationError,
                                ObjectNotFoundError,
                                InternalError)
from generic.helpers import get_current_datetime
from generic.logger import get_log_msg
from generic.validators import (validate_many, required_field, unique_field,
                                email_field, min_length, min_char_classes,
                                max_length, image_dim_validator,
                                image_size_validator, image_square_validator)
from generic.views import GenericViewset
from generic.factories import generic_factory
from generic.repositories import (OwnershipRepository, GenericRepository,
                                  ImageRepository)
from generic.services import (generic_retrieve_single_service,
                              generic_delete_service, generic_update_service,
                              generic_create_service,
                              store_image_service,
                              remove_image_service)

from authentication.repositories import (TokenRepository, ResetRepository,
                                         MailVerificationRepository)
from authentication.serializers import (RegisterSerializer,
                                        UpdatePasswordSerializer,
                                        RefreshSerializer, ResetSerializer,
                                        ConfirmSerializer,
                                        ProfileImageSerializer)
from authentication.services import (update_user_service, retrieve_token_service,
                                     logout_service, logout_all_service,
                                     refresh_token_service, reset_password_service,
                                     validate_reset_password_service,
                                     confirm_reset_password_service,
                                     validate_email_service, confirm_email_service)

User = get_user_model()
LOGGER = logging.getLogger("views")


def get_user_serializer():
    """
    Return the User model serializer that is active in the project.
    """
    try:
        name = settings.USER_SERIALIZER
        names = name.split('.')
        mod = __import__('.'.join(names[:-1]), fromlist=names[-1:])
        return getattr(mod, names[-1])
    except ValueError:
        raise ImproperlyConfigured("""USER_SERIALIZER must be of the
                                   form 'app_label.model_name.""")
    except:
        raise ImproperlyConfigured(
            """USER_SERIALIZER refers to model '%s' that
            has not been installed""" % settings.AUTH_USER_MODEL
        )


UserSerializer = get_user_serializer()


class PasswordRequirementsView(APIView):
    """
    PasswordRequirementsView

    Returns the password requirements.

    **Parameters and return value**

    :allowed: GET
    :auth required: False
    :many: False
    :returns: 200 in case of success
    :returns: json object containing the password requirements
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/password.json' \
        --header 'Content-Type: application/json'

    **Return value example of GET request**

    {

        "minimal_length": 12,

        "char_classes": 3

    }
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        user = self.request.user
        LOGGER.info(get_log_msg(self.request, user))
        content = {'minimal_length': settings.MIN_PW_LENGTH,
                   'char_classes': settings.CHAR_CLASSES}

        return Response(content, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ViewSet):
    """
    UserViewSet

    Provides get, update and delete operations for
    User instances.

    **Parameters and return value**

    :allowed: GET, PATCH, DELETE
    :auth required: True
    :many: False
    :returns: 200 in case of success
    :error: 400 if a validation error occurs (inspect response for details)
    :error: 401 if the request is unauthorized
    :error: 404 if the requested user could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/users/d47947b4-65b1.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e423374d' \
        --header 'Content-Type: application/json'

    **Return value example of GET request**
    {

        "id": "a9caebca-5a81-11e8-8a23-f40f2434c1ce",

        "username": "josefK1526637368",

        "email": "josefK1526637368@example.com",

        "first_name": "Josef",

        "last_name": "K"

    }
    """
    repository = OwnershipRepository(User)
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None, format=None):
        """
        Builds and exposes retrieve view for users
        """
        service = generic_retrieve_single_service(self.repository)
        view = GenericViewset(self.serializer_class, service, request)

        return view.retrieve(pk)

    def destroy(self, request, pk=None, format=None):
        """
        Builds and exposes destroy view for users
        """
        service = generic_delete_service(self.repository)
        view = GenericViewset(self.serializer_class, service, request)

        return view.destroy(pk)

    def partial_update(self, request, pk=None, format=None):
        """
        Builds and exposes partial update view for users
        """
        validators = (unique_field(self.repository, 'email'),
                      unique_field(self.repository, 'username'),)
        args_validators = (email_field(self.repository, 'email'),
                           max_length(self.repository, 'username', 50),
                           max_length(self.repository, 'first_name', 50),
                           max_length(self.repository, 'last_name', 50),)
        service = update_user_service(self.repository, validate_many(*validators))
        view = GenericViewset(self.serializer_class, service, request)

        return view.partial_update(pk, validate_many(*args_validators))


class ProfileImageViewSet(viewsets.ViewSet):
    """
    ProfileImageViewSet

    Allows to add, and delete profile images for users.
    """
    image_repository = ImageRepository(User)
    repository = OwnershipRepository(User)
    image_serializer_class = ProfileImageSerializer
    serializer_class = UserSerializer
    parser_classes = (FileUploadParser,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, format=None):
        LOGGER.info(get_log_msg(self.request, self.request.user))
        user = request.user
        # Check if the user already has a profile image
        if user.image:
            content = {settings.ERROR_KEY: 'Profile image is already defined for user.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # Apply serializer
        data = request.data
        serializer = self.image_serializer_class(data=data,
                                                 context={'request': request})

        if serializer.is_valid(raise_exception=False):
            image = serializer.validated_data['file']
            return self._create_image(user, image)

        return ProfileImageViewSet._handle_error('Validation failed.',
                                                 status.HTTP_400_BAD_REQUEST)

    def _create_image(self, user, image):
        validators = (image_size_validator(self.image_repository,
                                           'image',
                                           settings.MAX_IMG_SIZE),
                      image_square_validator(self.image_repository, 'image'),
                      image_dim_validator(self.image_repository,
                                          'image',
                                          settings.MAX_IMG_WIDTH,
                                          settings.MAX_IMG_HEIGHT),)
        service = store_image_service(self.image_repository,
                                      validate_many(*validators),
                                      'image')
        try:
            service(user, image)
        except ValidationError as e:
            return ProfileImageViewSet._handle_error(e, status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None, format=None):
        service = remove_image_service(self.repository, 'image')
        view = GenericViewset(self.serializer_class, service, request)

        return view.destroy(pk)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


class UpdatePasswordViewSet(viewsets.ViewSet):
    """
    UpdatePasswordViewSet

    Provides update password operation for User instances.

    **Parameters and return value**

    :allowed: PATCH
    :auth required: True
    :many: False
    :returns: 204 in case of success
    :error: 400 if a validation error occurs (inspect response for details)
    :error: 401 if the request is unauthorized
    :error: 404 if the requested user could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for PATCH request**

    curl --request PATCH \
        --url 'https://api.basement.technology/auth/users/d47947b4-65b1.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e423374d' \
        --header 'Content-Type: application/json'
        --data

        '{

            "password": "new_password"

        }'
    """
    repository = OwnershipRepository(User)
    serializer_class = UpdatePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def partial_update(self, request, pk=None, format=None):
        """
        Builds and exposes update password view for users
        """
        validators = ()
        args_validators = (required_field(self.repository, 'password'),
                           min_length(self.repository, 'password', settings.MIN_PW_LENGTH),
                           min_char_classes(self.repository, 'password', settings.CHAR_CLASSES),)
        service = generic_update_service(self.repository, validate_many(*validators))

        view = GenericViewset(self.serializer_class, service, request)
        response = view.partial_update(pk, validate_many(*args_validators))

        if response.status_code == 200:
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return response


class RegisterViewSet(viewsets.ViewSet):
    """
    RegisterViewSet

    Provides create operation for User instances.

    **Parameters and return value**

    :allowed: POST
    :auth required: False
    :many: False
    :returns: 201 in case of success
    :returns: user instance that was created
    :error: 400 if posted user object is invalid: json representation
                is invalid, password is too weak, email address is invalid
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url https://api.basement.technology/auth/token.json \
        --header 'Content-Type: application/json' \
        --data

        '{

            "username": "josef1526637489",

            "password": "1Secure#Password"

        }'

    **Return value example of POST request**
    {

        "id": "f7c8aaa6-5a81-11e8-bd41-f40f2434c1ce",

        "username": "josef1526637489",

        "email": null,

        "first_name": null,

        "last_name": null

    }
    """
    repository = OwnershipRepository(User)
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Builds and exposes create view for users
        """
        validators = (unique_field(self.repository, 'email'),
                      unique_field(self.repository, 'username'),)
        args_validators = (required_field(self.repository, 'username'),
                           required_field(self.repository, 'password'),
                           email_field(self.repository, 'email'),
                           min_length(self.repository, 'password', settings.MIN_PW_LENGTH),
                           min_char_classes(self.repository, 'password', settings.CHAR_CLASSES),
                           max_length(self.repository, 'username', 50),
                           max_length(self.repository, 'first_name', 50),
                           max_length(self.repository, 'last_name', 50),)

        service = generic_create_service(self.repository, validate_many(*validators),
                                         generic_factory)

        view = GenericViewset(self.serializer_class, service, request)
        response = view.create(validate_many(*args_validators))

        if 'password' in response.data:
            del response.data['password']

        return response


class TokenViewSet(viewsets.ViewSet):
    """
    TokenView

    Provides api endpoint that delivers api access tokens.
    Takes username and password of User instance.

    **Parameters and return value**

    :allowed: POST
    :auth required: False
    :many: False
    :returns: 200 in case of success
    :returns: token and refresh token with expiry time
    :error: 400 if posted credentials are invalid
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url https://api.basement.technology/auth/token.json \
        --header 'Content-Type: application/json' \
        --data

        '{

            "username": "johndoe@example.com",

            "password": "John-Doe-1"

        }'

    **Return value example of POST request**

    {

        "user": "babda7de-6115-11e8-add9-f40f2434c1ce",

        "token": "x8bxmnsaxniz9q800h8pm554efj4l7b2u921d1c0ld66w3rf9t0rirc",

        "refresh_token": "th7t047ag6bnwkurqd9e81a9630ssuhuermh7qeb7vew8wan",

        "token_expiry": "2018-05-26T20:00:15.563893Z",

        "refresh_token_expiry": "2018-05-27T19:00:15.563915Z"

    }
    """
    serializer_class = AuthTokenSerializer
    repository = TokenRepository()
    validator_repository = GenericRepository(User)
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Takes a user's username and password and generates a new token for
        that user if username and password are correct
        """
        args_validators = (required_field(self.validator_repository, 'username'),
                           required_field(self.validator_repository, 'password'),
                           email_field(self.validator_repository, 'email'),)
        args_validator = validate_many(*args_validators)

        # Validate arguments
        data = self.request.data
        try:
            if args_validator is not None: args_validator(data)
        except ValidationError as error:
            return TokenViewSet._handle_error(error, status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data,
                                           context={'request': request})

        if serializer.is_valid(raise_exception=False):
            user = serializer.validated_data['user']
            LOGGER.info(get_log_msg(self.request, user))
            return self._retrieve_token(request, user)

        LOGGER.info(get_log_msg(self.request, self.request.user))
        return TokenViewSet._handle_error('Validation failed.', status.HTTP_400_BAD_REQUEST)

    def _retrieve_token(self, request, user):
        service = retrieve_token_service(self.repository)
        (token, refresh_token) = service(user)
        exp = get_current_datetime() + settings.TOKEN_EXPIRY
        refresh_exp = get_current_datetime() + settings.REFRESH_TOKEN_EXPIRY
        content = {'user': user.id,
                   'token': token,
                   'refresh_token': refresh_token,
                   'token_expiry': exp,
                   'refresh_token_expiry': refresh_exp}
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        return Response(content, status=status.HTTP_200_OK)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


class LogoutViewSet(viewsets.ViewSet):
    """
    LogoutViewSet

    Provides api endpoint that deletes the token that is passed by header.

    **Parameters and return value**

    :allowed: GET
    :auth required: True
    :many: False
    :returns: 204 in case of success
    :error: 400 if the request is malformed, should never happen
    :error: 404 if the passed token could not be found, should never happen
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/logout.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471' \
        --header 'Content-Type: application/json'
    """
    repository = TokenRepository()
    permission_classes = (IsAuthenticated,)

    def list(self, request, format=None):
        """
        Destroys the token that was used got authentication
        """
        if 'HTTP_AUTHORIZATION' not in request.META:
            return LogoutViewSet._handle_error('No auth header provided.',
                                               status.HTTP_401_UNAUTHORIZED)

        service = logout_service(self.repository)
        token_str = str(request.META['HTTP_AUTHORIZATION'])
        token = token_str.split(sep=' ', maxsplit=1)[1]
        try:
            service(token)
        except ObjectNotFoundError as e:
            return LogoutViewSet._handle_error(e, status.HTTP_401_UNAUTHORIZED)
        except ValidationError as e:
            return LogoutViewSet._handle_error(e, status.HTTP_401_UNAUTHORIZED)

        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


class LogoutAllViewSet(viewsets.ViewSet):
    """
    LogoutViewSet

    Provides api endpoint that deletes all tokens of the logged in user.

    **Parameters and return value**

    :allowed: GET
    :auth required: True
    :many: False
    :returns: 204 in case of success
    :error: 400 if the request is malformed, should never happen
    :error: 401 if the request is unauthorized
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/logoutall.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb' \
        --header 'Content-Type: application/json'
    """
    repository = TokenRepository()
    permission_classes = (IsAuthenticated,)

    def list(self, request, format=None):
        """
        Destroys all tokens associated with the authenticated user
        """
        if 'HTTP_AUTHORIZATION' not in request.META:
            return LogoutAllViewSet._handle_error('No auth header provided.',
                                                  status.HTTP_401_UNAUTHORIZED)

        service = logout_all_service(self.repository)
        service(request.user)
        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


class RefreshViewSet(viewsets.ViewSet):
    """
    RefreshViewSet

    Provides api endpoint that refreshes api access tokens.
    Takes token and refresh token of :model:`authentication.AuthToken` instance.

    **Parameters and return value**

    :allowed: POST
    :auth required: True
    :many: False
    :returns: 200 in case of success
    :returns: token and refresh token with expiry times (see example below)
    :error: 400 if posted json object is invalid
    :error: 401 if the request is unauthorized
    :error: 404 if posted token could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url 'https://api.basement.technology/auth/refresh.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb' \
        --header 'Content-Type: application/json' \
        --data

        '{

            "refresh_token": "1a958a16e9ab03489f8aa345851248d23062f9"

        }'


    **Return value example of POST request**

    {

        "user": "babda7de-6115-11e8-add9-f40f2434c1ce",

        "token": "x8bxmnsaxniz9q800h8pm554efj4l7b2u",

        "refresh_token": "2r17z2hedt2hsjjp79g97hxyzoyuy4dw2cq",

        "token_expiry": "2018-05-26T20:00:15.563893Z",

        "refresh_token_expiry": "2018-05-27T19:00:15.563915Z"

    }
    """
    serializer_class = RefreshSerializer
    repository = TokenRepository()
    validator_repository = GenericRepository(User)
    permission_classes = (IsAuthenticated,)

    def create(self, request, format=None):
        """
        Takes a user's refresh token and generates a new token for
        that user
        """
        if 'HTTP_AUTHORIZATION' not in request.META:
            return RefreshViewSet._handle_error('No auth header provided.',
                                                status.HTTP_401_UNAUTHORIZED)

        args_validators = (required_field(self.validator_repository, 'refresh_token'),)
        args_validator = validate_many(*args_validators)

        # Validate arguments
        data = self.request.data
        try:
            if args_validator is not None: args_validator(data)
        except ValidationError as error:
            return RefreshViewSet._handle_error(error, status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data, context={'request': request})

        if serializer.is_valid(raise_exception=False):
            token_str = str(request.META['HTTP_AUTHORIZATION'])
            token = token_str.split(sep=' ', maxsplit=1)[1]
            refresh_token = serializer.validated_data['refresh_token']
            LOGGER.info(get_log_msg(self.request, request.user))
            return self._refresh_token(request.user, token, refresh_token)

        LOGGER.info(get_log_msg(self.request, self.request.user))

        return RefreshViewSet._handle_error('Validation failed.', status.HTTP_400_BAD_REQUEST)

    def _refresh_token(self, user, token, refresh_token):
        service = refresh_token_service(self.repository)

        try:
            (token, refresh_token) = service(user, token, refresh_token)
        except (ObjectNotFoundError, ValidationError) as e:
            return RefreshViewSet._handle_error(e, status.HTTP_401_UNAUTHORIZED)

        exp = get_current_datetime() + settings.TOKEN_EXPIRY
        refresh_exp = get_current_datetime() + settings.REFRESH_TOKEN_EXPIRY
        content = {'user': user.id,
                   'token': token,
                   'refresh_token': refresh_token,
                   'token_expiry': exp,
                   'refresh_token_expiry': refresh_exp}

        return Response(content, status=status.HTTP_200_OK)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


class ResetPasswordViewSet(viewsets.ViewSet):
    """
    ResetPasswordViewSet

    Provides api endpoint that resets a users' password.
    Takes email address of :model:`authentication.AuthToken` instance.

    **Parameters and return value**

    :allowed: POST
    :auth required: False
    :many: False
    :returns: 204 in case of success
    :returns: only status code is returned, also sends an email to the
              given address
    :error: 400 if posted json object is invalid or if the email address
                has not been verified
    :error: 404 if posted user could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url 'https://api.basement.technology/auth/resetpassword.json' \
        --header 'Content-Type: application/json' \
        --data

        '{

            "email": "john.doe@example.com"

        }'
    """
    serializer_class = ResetSerializer
    repository = ResetRepository()
    validator_repository = GenericRepository(User)
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Sends reset password email to the posted email address
        """
        args_validators = (required_field(self.validator_repository, 'email'),
                           email_field(self.validator_repository, 'email'),)
        args_validator = validate_many(*args_validators)

        # Validate arguments
        data = self.request.data
        try:
            if args_validator is not None: args_validator(data)
        except ValidationError as error:
            return ResetPasswordViewSet._handle_error(error, status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data,
                                           context={'request': request})

        if serializer.is_valid(raise_exception=False):
            email = serializer.validated_data['email']
            LOGGER.info(get_log_msg(self.request, request.user))
            return self._reset_password(email)

        LOGGER.info(get_log_msg(self.request, self.request.user))

        return ResetPasswordViewSet._handle_error('Validation failed.',
                                                  status.HTTP_400_BAD_REQUEST)

    def _reset_password(self, email):
        service = reset_password_service(self.repository)

        try:
            service(email)
        except ObjectNotFoundError as e:
            return ResetPasswordViewSet._handle_error(e, status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return ResetPasswordViewSet._handle_error(e, status.HTTP_400_BAD_REQUEST)
        except InternalError as e:
            return ResetPasswordViewSet._handle_error(e, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


class ValidateResetPasswordViewSet(viewsets.ViewSet):
    """
    ValidateResetPasswordViewSet

    Provides api endpoint that takes a password reset token as GET parameter
    and checks if that token is valid.

     **Parameters and return value**

    :allowed: GET
    :auth required: False
    :many: False
    :returns: 204 in case of success
    :returns: only status code is returned
    :error: 400 if token is malformed or expired
    :error: 404 if associated user could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/validatereset/efc51.json' \
        --header 'Content-Type: application/json'
    """
    repository = ResetRepository()
    permission_classes = (AllowAny,)

    def retrieve(self, request, pk=None, format=None):
        """
        Validates the given reset password token
        """
        LOGGER.info(get_log_msg(self.request, request.user))
        return self._validate_reset_token(pk)

    def _validate_reset_token(self, reset_token):
        service = validate_reset_password_service(self.repository)

        try:
            service(reset_token)
        except ObjectNotFoundError as e:
            return ValidateResetPasswordViewSet._handle_error(e, status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return ValidateResetPasswordViewSet._handle_error(e, status.HTTP_400_BAD_REQUEST)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


class ConfirmResetPasswordViewSet(viewsets.ViewSet):
    """
    ConfirmResetPasswordViewSet

    Provides api endpoint that validates the given reset password token and
    resets the associated User instance's password.

    **Parameters and return value**

    :allowed: POST
    :auth required: False
    :many: False
    :returns: 204 in case of success
    :returns: only status code is returned
    :error: 400 if posted reset token or password are invalid
    :error: 404 if associated User instance
                could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url 'https://api.basement.technology/auth/confirmreset.json' \
        --header 'Content-Type: application/json' \
        --data

        '{

            "reset_token": "efc5158869dc580466dc291901dd8af39f3cd2b50f4",
            "password": "NewPassword"

        }'
    """
    serializer_class = ConfirmSerializer
    repository = ResetRepository()
    validator_repository = GenericRepository(User)
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Validates the token and resets users' password
        """
        args_validators = (required_field(self.validator_repository, 'reset_token'),
                           required_field(self.validator_repository, 'password'),
                           min_length(self.validator_repository, 'password',
                                      settings.MIN_PW_LENGTH),
                           min_char_classes(self.validator_repository, 'password',
                                            settings.CHAR_CLASSES),)
        args_validator = validate_many(*args_validators)

        # Validate arguments
        data = self.request.data
        try:
            if args_validator is not None: args_validator(data)
        except ValidationError as error:
            return ConfirmResetPasswordViewSet._handle_error(error, status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data,
                                           context={'request': request})

        if serializer.is_valid(raise_exception=False):
            reset_token = serializer.validated_data['reset_token']
            password = serializer.validated_data['password']

            LOGGER.info(get_log_msg(self.request, request.user))
            return self._validate_reset_token(reset_token, password)

        LOGGER.info(get_log_msg(self.request, self.request.user))

        return ConfirmResetPasswordViewSet._handle_error('Validation failed.',
                                                         status.HTTP_400_BAD_REQUEST)

    def _validate_reset_token(self, reset_token, password):
        service = confirm_reset_password_service(self.repository)

        try:
            service(reset_token, password)
        except ObjectNotFoundError as e:
            return ConfirmResetPasswordViewSet._handle_error(e, status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return ConfirmResetPasswordViewSet._handle_error(e, status.HTTP_400_BAD_REQUEST)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


class ConfirmEmailViewSet(viewsets.ViewSet):
    """
    ConfirmEmailViewSet

    Provides api endpoint that sends an email validation email to the
    authenticated User instance.

    **Parameters and return value**

    :allowed: GET
    :auth required: True
    :many: False
    :returns: 204 in case of success
    :returns: only status code is returned
    :error: 400 if the user has got an invalid email address of none at
                all or if the given validation token is invalid or expired
    :error: 401 if the request is unauthorized
    :error: 404 if the User instance associated with
                the given validation token could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/confirmemail.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e' \
        --header 'Content-Type: application/json'
    """
    serializer_class = ConfirmSerializer
    repository = MailVerificationRepository()
    validator_repository = OwnershipRepository(User)
    permission_classes = (IsAuthenticated,)

    def list(self, request, format=None):
        """
        Sends an email verification email
        """
        LOGGER.info(get_log_msg(self.request, request.user))
        return self._validate_email(request)

    def _validate_email(self, request):
        user = request.user
        service = validate_email_service(self.repository)

        try:
            service(user)
        except ValidationError as e:
            return ConfirmEmailViewSet._handle_error(e, status.HTTP_400_BAD_REQUEST)
        except InternalError as e:
            return ConfirmEmailViewSet._handle_error(e, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk=None, format=None):
        """
        Checks the validation token and flags the email address as validated
        """
        LOGGER.info(get_log_msg(self.request, request.user))
        return self._confirm_email(pk)

    def _confirm_email(self, val_token):
        service = confirm_email_service(self.repository)

        try:
            service(val_token)
        except ObjectNotFoundError as e:
            return ConfirmEmailViewSet._handle_error(e, status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return ConfirmEmailViewSet._handle_error(e, status.HTTP_400_BAD_REQUEST)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)
