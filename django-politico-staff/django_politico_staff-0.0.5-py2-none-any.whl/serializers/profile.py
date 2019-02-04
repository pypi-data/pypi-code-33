from rest_framework.serializers import ModelSerializer

from staff.models import Profile


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "politico_title",
            "politico_author_page",
            "slack_api_id",
            "slack_image",
            "google_email",
            "google_display_name",
            "twitter_handle",
        )


class EditableProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "politico_author_page",
            "google_email",
            "google_display_name",
            "twitter_handle",
        )
