import requests
from django.conf import settings
from django.contrib.auth.models import User


class AAAAppClient:
    @staticmethod
    def get_user(token):
        response = requests.get(
            settings.AAA_URL,
            headers={
                'Authorization': token,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        if response.status_code == 200:
            profile = response.json()
            user = User()

            for attribute in ['first_name', 'last_name', 'email', 'pk']:
                setattr(user, attribute, profile.get(attribute))

            return user
