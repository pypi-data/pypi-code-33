import uuid

import requests
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from tqdm import tqdm

from slacker import Slacker
from staff.conf import settings
from staff.models import Profile


class Command(BaseCommand):
    help = "Sync users from Slack"

    def handle(self, *args, **options):
        SLACK = Slacker(settings.SLACK_API_TOKEN)
        slack_users = SLACK.users.list().body["members"]
        for slack_user in tqdm(slack_users, desc="Users"):
            id = slack_user["id"]
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

            email = slack_profile.get("email", None)

            if not email or email[-13:] != "@politico.com":
                continue

            user, created = User.objects.update_or_create(
                username=email,
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_staff": True,
                    "is_active": slack_user["deleted"] is False,
                },
            )

            profile, created = Profile.objects.update_or_create(
                user=user,
                defaults={
                    "slack_api_id": id,
                    "politico_title": slack_profile.get("title", "Staff"),
                },
            )

            if (
                slack_profile.get("image_192", False)
                and not profile.slack_image
            ):
                r = requests.get(slack_profile.get("image_192"), stream=True)
                img = r.raw.read()
                profile.slack_image.save(
                    "slack-profile-{}.jpg".format(uuid.uuid4().hex[:10]),
                    ContentFile(img),
                    save=True,
                )
            profile.save()
