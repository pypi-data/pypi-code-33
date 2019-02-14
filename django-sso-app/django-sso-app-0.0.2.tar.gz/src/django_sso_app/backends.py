import logging

from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist

from . import settings
from .utils import (get_sso_id, get_profile_model,
                    get_profile_from_sso,
                    create_local_profile_from_sso,
                    update_local_profile_from_sso)

logger = logging.getLogger("django_sso_app")


class SsoBackend(ModelBackend):
    """
    See django.contrib.auth.backends.RemoteUserBackend.

    The jwt has an expected payload such as the following

        {
          "iss": "nxhnkMPKcpRWaTKwNOvGcLcs5MHJINOg",
          "user_id": 1,
          "rev": 0,
          "exp": 1528376222,
          "fp": "b28493a6a29a5a38973a8a3e3abe7f34"
        }
    """

    def authenticate(self, request, consumer_username, encoded_jwt, decoded_jwt):
        logger.info("Authenticating consumer {}".format(consumer_username))

        if not consumer_username or not encoded_jwt:
            return None

        sso_id = get_sso_id(consumer_username)

        try:
            profile = get_profile_model().objects.get(sso_id=sso_id)
            user = profile
            if settings.SSO_USER_PROFILE_MODEL is not None:
                user = profile.user

            rev_changed = profile.sso_rev != decoded_jwt["rev"]
            first_access = not user.is_active and not profile.is_unsubscribed
            if rev_changed or first_access:
                if rev_changed:
                    logger.info("Rev changed from {} to {} for {}, updating ...".format(profile.sso_rev,
                                                      decoded_jwt["rev"],
                                                      consumer_username))
                if first_access:
                    logger.info("{}'s first access, updating ...".format(
                        consumer_username))

                # update local profile from SSO
                sso_profile = get_profile_from_sso(sso_id=sso_id,
                                                   encoded_jwt=encoded_jwt)
                update_local_profile_from_sso(sso_profile=sso_profile,
                                              profile=profile)

                logger.info("{} updated with latest data from SSO".format(
                    consumer_username))
            else:
                logger.info("Nothing changed for {}".format(consumer_username))
        except ObjectDoesNotExist:
            # create local profile from SSO
            sso_profile = get_profile_from_sso(sso_id=sso_id,
                                               encoded_jwt=encoded_jwt)

            profile = create_local_profile_from_sso(sso_profile=sso_profile)
            user = profile
            if settings.SSO_USER_PROFILE_MODEL is not None:
                user = profile.user

        return user
