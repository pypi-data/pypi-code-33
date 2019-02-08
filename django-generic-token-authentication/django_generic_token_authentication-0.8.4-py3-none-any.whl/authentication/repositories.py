from django.conf import settings
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist

from generic.exceptions import (ObjectNotFoundError,
                                ValidationError,
                                InternalError)
from generic.helpers import get_current_datetime
from generic.validators import email_field
from generic.repositories import GenericRepository

from authentication.factories import token_factory
from authentication.helper import get_rand_str
from authentication.models import AuthToken

User = get_user_model()


class TokenRepository:
    """
    Provides a database abstraction layer for the Token model
    """

    @staticmethod
    def delete_by_user(user):
        AuthToken.objects.filter(user=user).delete()
        return True

    @staticmethod
    def create_token(user):
        num_tokens = AuthToken.objects.filter(user=user).count()

        # Make sure that one user has max 10 tokens
        if num_tokens > 9:
            diff = num_tokens - 9
            tokens = AuthToken.objects.filter(user=user)
            ts_to_del = tokens.order_by('created')[:diff].values_list("id", flat=True)
            AuthToken.objects.filter(pk__in=list(ts_to_del)).delete()

        # Create and persist new token
        (token, key) = token_factory(user=user)
        token.save()

        return key, token.refresh_key

    @staticmethod
    def delete_expired_tokens(delta):
        exp_tokens = AuthToken.objects.filter(created__lte=get_current_datetime() - delta)
        num_tokens = exp_tokens.count()
        exp_tokens.delete()

        return num_tokens

    @staticmethod
    def logout(token):
        try:
            unsigned_token = signing.loads(token, max_age=settings.TOKEN_EXPIRY,
                                           salt='access_token')
            token_id = unsigned_token['token_id']
            AuthToken.objects.get(id=token_id).delete()
        except signing.SignatureExpired:
            raise ValidationError('Expired token.', field='token')
        except signing.BadSignature:
            raise ValidationError('Invalid token.', field='token')
        except KeyError:
            raise ValidationError('Invalid request.', field='token_id')
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass='AuthToken')

        return True

    @staticmethod
    def refresh_token(user, token, refresh_token):
        try:
            unsigned_token = signing.loads(token, max_age=settings.REFRESH_TOKEN_EXPIRY,
                                           salt='access_token')
            token_id = unsigned_token['token_id']
            auth_token = AuthToken.objects.filter(id=token_id).filter(refresh_key=refresh_token)
            auth_token = auth_token.get()
        except signing.SignatureExpired:
            raise ValidationError('Expired token.', field='token')
        except signing.BadSignature:
            raise ValidationError('Invalid token.', field='token')
        except KeyError:
            raise ValidationError('Invalid request.', field='tokenId')
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass='AuthToken')

        try:
            salt = user.password + user.username
            signing.loads(refresh_token, max_age=settings.REFRESH_TOKEN_EXPIRY, salt=salt)
        except signing.BadSignature:
            raise ValidationError('Invalid refresh token.', field='refresh_token')

        auth_token.delete()
        return TokenRepository.create_token(user)


class ResetRepository:
    """
    Provides an abstraction layer for the password reset functionality
    """
    namespace = 'passwd_reset_req'

    @staticmethod
    def reset_password(email):
        # Generate reset token
        if email is None:
            raise ValidationError('Email address has not been set.', field='email')

        try:
            user = User.objects.filter(email=email).get()
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass='User')

        if not user.validated_email:
            raise ValidationError('Email address has not been verified.', field='email')

        reset_token = signing.dumps({'user_id': str(user.id),
                                     'rand': get_rand_str(16)},
                                    salt=ResetRepository.namespace, compress=True)

        plaintext = get_template('authentication/mail_reset_passwd.txt')
        html = get_template('authentication/mail_reset_passwd.html')

        context = {'token': reset_token,
                   'proto': settings.PROTO,
                   'host': settings.HOST,
                   'logo': settings.LOGO,
                   'title': settings.TITLE}

        text_content = plaintext.render(context)
        html_content = html.render(context)

        # Send reset token to user
        subject = 'Password reset'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email
        email_message = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email_message.attach_alternative(html_content, "text/html")

        try:
            mail = email_message.send(), reset_token
        except ConnectionRefusedError:
            raise InternalError('Send email failed.', fct='send')

        return mail

    @staticmethod
    def validate_token_and_get_user(reset_token):
        # Unsign reset token
        try:
            unsigned_token = signing.loads(reset_token,
                                           max_age=settings.RESET_TOKEN_EXPIRY,
                                           salt=ResetRepository.namespace)
        except signing.SignatureExpired:
            raise ValidationError('Expired reset request.', field='reset_token')
        except signing.BadSignature:
            raise ValidationError('Invalid reset request.', field='reset_token')

        # Retrieve user
        try:
            user = User.objects.get(id=unsigned_token['user_id'])
        except KeyError:
            raise ValidationError('Invalid request.', field='user_id')
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass='User')

        return user


class MailVerificationRepository:
    """
    Provides an abstraction layer for the verify email functionality
    """
    namespace = 'verify_email_add'

    @staticmethod
    def send_email_validation(user):
        if user.validated_email:
            raise ValidationError('Email has already been verified.', field='email')

        if user.email is None or user.email is "":
            raise ValidationError('Email address has not been set.', field='email')

        validator = email_field(GenericRepository, 'email')
        validator(user)

        # Generate validation token
        val_token = signing.dumps({'user_id': str(user.id),
                                   'rand': get_rand_str(16)},
                                  salt=MailVerificationRepository.namespace)

        plaintext = get_template('authentication/mail_verify.txt')
        html = get_template('authentication/mail_verify.html')

        context = {'token': val_token,
                   'proto': settings.PROTO,
                   'host': settings.HOST,
                   'logo': settings.LOGO,
                   'title': settings.TITLE}

        text_content = plaintext.render(context)
        html_content = html.render(context)

        # Send validation mail
        subject = 'Confirm email address'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email
        email_message = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email_message.attach_alternative(html_content, "text/html")

        try:
            mail = email_message.send(), val_token
        except ConnectionRefusedError:
            raise InternalError('Send email failed.', fct='send')

        return mail

    @staticmethod
    def validate_token_and_get_user(val_token):
        # Unsign reset token
        try:
            unsigned_token = signing.loads(val_token,
                                           max_age=settings.VAL_TOKEN_EXPIRY,
                                           salt=MailVerificationRepository.namespace)
        except signing.SignatureExpired:
            raise ValidationError('Expired validation request.', field='validation_token')
        except signing.BadSignature:
            raise ValidationError('Invalid validation request.', field='validation_token')

        # Retrieve user
        try:
            user = User.objects.get(id=unsigned_token['user_id'])
        except KeyError:
            raise ValidationError('Invalid request.', field='user_id')
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass='User')

        return user
