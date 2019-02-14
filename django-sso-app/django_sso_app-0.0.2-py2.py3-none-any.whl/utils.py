import json
import logging
from six import string_types
from importlib import import_module
import requests

from django.contrib.auth import get_user_model
from django.db import transaction

from . import settings

logger = logging.getLogger("django_sso_app")


def import_callable(path_or_callable):
    if hasattr(path_or_callable, '__call__'):
        return path_or_callable
    else:
        assert isinstance(path_or_callable, string_types)
        package, attr = path_or_callable.rsplit('.', 1)
        return getattr(import_module(package), attr)


def get_profile_model():
    profile_model = settings.SSO_USER_PROFILE_MODEL
    if profile_model is None:
        return get_user_model()
    else:
        return import_callable(profile_model)


def get_sso_id(consumer_username):
    return consumer_username


class SsoUserStatus(object):
    def __init__(self, is_active, is_unsubscribed, is_to_subscribe):
        self.is_active = is_active
        self.is_unsubscribed = is_unsubscribed
        self.is_to_subscribe = is_to_subscribe

    def __repr__(self):
        return "{}(is_active={}, is_unsubscribed={}, is_to_subscribe={})".format(
            self.__class__.__name__, self.is_active, self.is_unsubscribed,
            self.is_to_subscribe)

    @staticmethod
    def get_user_status(is_unsubscribed, subscriptions, email_verified=True):
        _is_active = settings.SSO_DEACTIVATE_USER_ON_UNSUBSCRIPTION

        if is_unsubscribed:  # is unsubscribed from sso
            return SsoUserStatus(is_active=_is_active,
                                 is_unsubscribed=True,
                                 is_to_subscribe=False)


        else:  # is still subscribed to sso
            for subscription in subscriptions:
                if subscription["url"] == settings.SSO_SERVICE_URL:  # subscription found
                    if subscription["is_unsubscribed"]:  # user is unsubscribed from service
                        return SsoUserStatus(is_active=_is_active and email_verified,
                                             is_unsubscribed=True,
                                             is_to_subscribe=False)
                    return SsoUserStatus(is_active=email_verified,
                                         is_unsubscribed=False,
                                         is_to_subscribe=False)

            # is NOT subscribed 
            return SsoUserStatus(is_active=email_verified,
                                 is_unsubscribed=False,
                                 is_to_subscribe=settings.SSO_SERVICE_SUBSCRIPTION_IS_MANDATORY)


def check_profile_on_sso_by_username(username):
    logger.info(
        "Checking with SSO if user {} already exists ...".format(username))

    url = settings.SSO_BACKEND_USERS_CHECK_URL
    params = {
        "username": username
    }
    response = requests.get(url=url, params=params, timeout=10, verify=False)

    if response.status_code == requests.codes.NOT_FOUND:
        logger.info("User {} does NOT exist".format(username))
        return None

    response.raise_for_status()
    sso_id = json.loads(response.text).get("id", None)

    logger.info(
        "User {} already exists with SSO ID {}".format(username, sso_id))

    return sso_id


def check_profile_on_sso_by_email(email):
    logger.info(
        "Checking with SSO if a user with email {} already exists ...".format(
            email))

    url = settings.SSO_BACKEND_USERS_CHECK_URL
    params = {
        "email": email
    }
    response = requests.get(url=url, params=params, timeout=10, verify=False)

    if response.status_code == requests.codes.NOT_FOUND:
        logger.info("A user with email {} does NOT exist".format(email))
        return None

    response.raise_for_status()
    sso_id = json.loads(response.text).get("id", None)

    logger.info(
        "A user with email {} already exists with SSO ID {}".format(
            email, sso_id))

    return sso_id


def get_profile_from_sso(sso_id, encoded_jwt):
    logger.info("Getting SSO profile for ID {} ...".format(sso_id))

    url = settings.SSO_BACKEND_USER_URL.format(user_id=sso_id)
    headers = {
        "Authorization": "Bearer {jwt}".format(jwt=encoded_jwt)
    }
    response = requests.get(url=url, headers=headers, timeout=10, verify=False)
    response.raise_for_status()
    sso_profile = response.json()

    logger.info("Retrieved SSO profile for ID {}".format(sso_id))

    return sso_profile


@transaction.atomic
def create_local_profile_from_sso(sso_profile, can_subscribe=False):
    logger.info("Creating local profile for user {} with SSO ID {} ...".format(
        sso_profile["username"], sso_profile["id"]))

    profile = _create_or_update_local_profile_from_sso(
        sso_profile=sso_profile, can_subscribe=can_subscribe)

    logger.info("Created local profile for user {} with SSO ID {}".format(
        sso_profile["username"], sso_profile["id"]))

    return profile


@transaction.atomic
def update_local_profile_from_sso(sso_profile, profile, can_subscribe=False):
    assert profile is not None

    logger.info("Updating local profile for user {} with SSO ID {} ...".format(
        sso_profile["username"], sso_profile["id"]))

    _create_or_update_local_profile_from_sso(sso_profile=sso_profile,
                                             profile=profile,
                                             can_subscribe=can_subscribe)

    logger.info("Updated local profile for user {} with SSO ID {}".format(
        sso_profile["username"], sso_profile["id"]))


@transaction.atomic
def _create_or_update_local_profile_from_sso(sso_profile, profile=None,
                                             can_subscribe=False):
    username = sso_profile["username"]
    email = sso_profile["email"]
    email_verified = sso_profile["email_verified"]
    password = sso_profile["password"]
    date_joined = sso_profile["date_joined"]
    first_name = sso_profile["first_name"]
    last_name = sso_profile["last_name"]
    sso_id = sso_profile["id"]

    creating = profile is None

    if creating:
        sso_user_status = SsoUserStatus.get_user_status(
            is_unsubscribed=sso_profile["is_unsubscribed"],
            subscriptions=sso_profile["subscriptions"])
        logger.info("Status for user {} with SSO ID {}: {}".format(
            username, sso_id, sso_user_status))
        user_model = get_user_model()
        profile_model = get_profile_model()
        user = user_model()
        user.username = username
        profile = profile_model()
        profile.sso_id = sso_id
    else:
        sso_user_status = SsoUserStatus.get_user_status(
            is_unsubscribed=sso_profile["is_unsubscribed"],
            subscriptions=sso_profile["subscriptions"],
            email_verified=email_verified)
        logger.info("Status for user {} with SSO ID {}: {}".format(
            username, sso_id, sso_user_status))
        user = profile.user

    is_active = sso_user_status.is_active
    is_unsubscribed = sso_user_status.is_unsubscribed
    is_to_subscribe = sso_user_status.is_to_subscribe

    sso_profile['sso_id'] = sso_id
    sso_profile['sso_rev'] = sso_profile['rev']

    user.email = email
    user.password = password
    user.date_joined = date_joined
    user.first_name = first_name
    user.last_name = last_name
    user.is_active = is_active

    for f in settings.SSO_REQUIRED_PROFILE_FIELDS:
        setattr(profile, f, sso_profile[f])

    user.save()
    if creating:
        profile.user = user
    profile.save()

    setattr(user, "is_to_subscribe", is_to_subscribe)
    if is_to_subscribe and can_subscribe:
        _subscribe_to_service(sso_id)

    return profile


def _subscribe_to_service(sso_id):
    logger.info(
        "Subscribing user with SSO ID {sso_id} to service {service_name} ...".format(
            sso_id=sso_id, service_name=settings.SSO_SERVICE_URL))

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {jwt}".format(jwt=settings.SSO_STAFF_JWT),
    }

    # Get all available services
    url = settings.SSO_BACKEND_SERVICES_URL
    response = requests.get(url=url, headers=headers, timeout=10, verify=False)
    response.raise_for_status()
    sso_services = response.json()

    # Find out the id for current service
    service_id = None
    for sso_service in sso_services:
        if sso_service["url"] == settings.SSO_SERVICE_URL:
            service_id = sso_service["id"]
            break
    if not service_id:
        _msg = "Current service {} is not listed in SSO!".format(
            settings.SSO_SERVICE_URL)
        raise Exception(_msg)

    # Subscribe to current service
    url = settings.SSO_BACKEND_USER_SUBSCRIPTIONS_CREATE_URL.format(user_id=sso_id,
                                                                    service_id=service_id)
    response = requests.post(url=url, headers=headers, timeout=10, verify=False)
    response.raise_for_status()
    logger.info(
        "User with SSO ID {sso_id} was successfully subscribed to service {service_name}!".format(
            sso_id=sso_id, service_name=settings.SSO_SERVICE_URL))
