import uuid

import requests
from celery import shared_task
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from slacker import Slacker
from staff.conf import settings
from staff.models import Profile


def get_slack_user(user, slack_users):
    """Return user profile from Slack."""
    if hasattr(user, "profile"):
        if user.profile.slack_api_id:
            for slack_user in slack_users:
                if slack_user["id"] == user.profile.slack_api_id:
                    return slack_user
        return None
    else:
        for slack_user in slack_users:
            if (
                user.email
                and slack_user.get("profile", {}).get("email", None)
                == user.email
            ):
                return slack_user
        return None


@shared_task(acks_late=True)
def sync_slack_users(pks):
    SLACK = Slacker(settings.SLACK_API_TOKEN)
    slack_users = SLACK.users.list().body["members"]
    for pk in pks:
        user = User.objects.get(pk=pk)

        if not user.email or user.email[-13:] != "@politico.com":
            continue

        slack_user = get_slack_user(user, slack_users)

        if not slack_user:
            continue

        slack_profile = slack_user["profile"]

        real_name = slack_profile.get("real_name", None)
        display_name = slack_profile.get("display_name", None)
        try:
            first_name, last_name = real_name.split(" ", 1)
        except ValueError:
            try:
                first_name, last_name = display_name.split(" ", 1)
            except ValueError:
                first_name = real_name or display_name or ""
                last_name = ""

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        profile, created = Profile.objects.update_or_create(
            user=user,
            defaults={
                "slack_api_id": slack_profile["id"],
                "politico_title": slack_profile.get("title", "Staff writer"),
            },
        )

        if slack_profile.get("image_192", False):
            r = requests.get(slack_profile.get("image_192"), stream=True)
            img = r.raw.read()
            profile.slack_image.save(
                "slack-profile-{}.jpg".format(uuid.uuid4().hex[:10]),
                ContentFile(img),
                save=True,
            )
            profile.save()
