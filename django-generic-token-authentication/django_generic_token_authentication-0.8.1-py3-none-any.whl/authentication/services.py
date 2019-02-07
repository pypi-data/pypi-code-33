from django.contrib.auth.hashers import make_password
from rest_framework.utils import model_meta

from generic.repositories import GenericRepository
from generic.services import generic_update_service


def update_user_service(repository, validator):
    """
    :param repository: Repository that will be called
    :param validator: User validator
    :return: Updated and saved user

    Updates an existing user.
    """

    def _update(pk, requesting_user, **kwargs):

        update = generic_update_service(repository, validator)
        old_instance = repository.get_by_id(pk, requesting_user)
        instance = update(pk, requesting_user, **kwargs)

        # Set validated_email to false if email has been changed
        if instance.email != old_instance.email:
            instance.validated_email = False

        # Save and return
        repository.persist(instance)
        return instance

    return _update


def retrieve_token_service(repository):
    """
    :param repository: Repository that will be called
    :return: token and refresh token

    Creates a new token for the given user.
    """

    def _retrieve(user):
        (token, refresh_token) = repository.create_token(user)
        return token, refresh_token

    return _retrieve


def logout_service(repository):
    """
    :param repository: Repository that will be called
    :return: True in case of success

    Deletes a single token.
    """

    def _logout(token):
        return repository.logout(token)

    return _logout


def logout_all_service(repository):
    """
    :param repository: Repository that will be called
    :return: True in case of success

    Deletes all tokens of user.
    """

    def _logout(user):
        return repository.delete_by_user(user)

    return _logout


def refresh_token_service(repository):
    """
    :param repository: Repository that will be called
    :return: New token and refresh token

    Refreshes a user's token.
    """

    def _refresh(user, token, refresh_token):
        return repository.refresh_token(user, token, refresh_token)

    return _refresh


def reset_password_service(repository):
    """
    :param repository: Repository that will be called
    :return: Mail and reset token

    Send password reset email to users' email.
    """

    def _reset(email):
        return repository.reset_password(email)

    return _reset


def validate_reset_password_service(repository):
    """
    :param repository: Repository that will be called
    :return: User instance

    Checks validity of the password reset token.
    """

    def _test(reset_token):
        return repository.validate_token_and_get_user(reset_token)

    return _test


def confirm_reset_password_service(repository):
    """
    :param repository: Repository that will be called
    :return: User instance

    Checks validity of the password reset token and sets new password.
    """

    def _confirm(reset_token, new_password):
        instance = repository.validate_token_and_get_user(reset_token)
        instance.password = make_password(new_password)
        instance.save()
        return instance

    return _confirm


def validate_email_service(repository):
    """
    :param repository: Repository that will be called
    :return: Mail and validation token

    Sends an email validation email.
    """

    def _validate(instance):
        return repository.send_email_validation(instance)

    return _validate


def confirm_email_service(repository):
    """
    :param repository: Repository that will be called
    :return: User instance

    Checks the validation token and flags the email address as validated.
    """

    def _confirm(val_token):
        instance = repository.validate_token_and_get_user(val_token)
        instance.validated_email = True
        instance.save()
        return instance

    return _confirm
