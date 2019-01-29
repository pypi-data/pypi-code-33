from entity.models import Person
from rest_framework import serializers
from rest_framework.reverse import reverse
from tracker.models import CampaignContent, CandidateRankingSet

from .biography import BiographySerializer
from .candidate import (
    CampaignSerializer,
    CandidateSerializer,
    PartySerializer,
    RatingCategorySerializer,
    CandidateRankingSerializer,
)


class PersonListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse(
            "tracker_api_person-detail",
            request=self.context["request"],
            kwargs={"pk": obj.pk},
        )

    class Meta:
        model = Person
        fields = ("url", "full_name")


class CampaignContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignContent
        fields = ["blurb"]


class PersonHomeSerializer(serializers.ModelSerializer):
    party = serializers.SerializerMethodField()
    win_rating = serializers.SerializerMethodField()
    ranking = serializers.SerializerMethodField()
    incumbent = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_party(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )

        return PartySerializer(candidacy.party).data

    def get_win_rating(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )
        try:
            return RatingCategorySerializer(
                candidacy.win_ratings.latest("date").category
            ).data
        except:
            return None

    def get_ranking(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )
        ranking_set = CandidateRankingSet.objects.latest("date")
        try:
            return CandidateRankingSerializer(
                ranking_set.rankings.get(candidate=candidacy)
            ).data
        except:
            return None

    def get_incumbent(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )
        return candidacy.incumbent

    def get_content(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )

        try:
            return CampaignContentSerializer(candidacy.campaign.content).data
        except:
            return None

    def get_campaign(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )

        try:
            return CampaignSerializer(candidacy.campaign).data
        except:
            return None

    def get_image(self, obj):
        try:
            return obj.images.get(tag__name="tracker").image
        except:
            return None

    class Meta:
        model = Person
        fields = (
            "id",
            "last_name",
            "first_name",
            "middle_name",
            "suffix",
            "summary",
            "full_name",
            "gender",
            "race",
            "birth_date",
            "party",
            "win_rating",
            "ranking",
            "incumbent",
            "content",
            "campaign",
            "image",
        )


class PersonSerializer(serializers.ModelSerializer):
    biography = serializers.SerializerMethodField()
    candidacy = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_biography(self, obj):
        try:
            return BiographySerializer(obj.biography).data
        except:
            return None

    def get_candidacy(self, obj):
        return CandidateSerializer(
            obj.candidacies.get(
                race__cycle__slug="2020", race__office__slug="president"
            )
        ).data

    def get_content(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )

        try:
            return CampaignContentSerializer(candidacy.campaign.content).data
        except:
            return None

    def get_image(self, obj):
        return obj.images.get(tag__name="tracker").image

    class Meta:
        model = Person
        fields = (
            "last_name",
            "first_name",
            "middle_name",
            "suffix",
            "full_name",
            "gender",
            "race",
            "nationality",
            "state_of_residence",
            "summary",
            "birth_date",
            "biography",
            "candidacy",
            "content",
            "image",
        )


class PersonSummarySerializer(serializers.ModelSerializer):
    party = serializers.SerializerMethodField()
    blurb = serializers.SerializerMethodField()
    declared_date = serializers.SerializerMethodField()
    headshot = serializers.SerializerMethodField()

    def get_party(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )

        try:
            return PartySerializer(candidacy.party).data["label"]
        except:
            return None

    def get_blurb(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )

        try:
            return CampaignContentSerializer(candidacy.campaign.content).data[
                "blurb"
            ]
        except:
            return ""

    def get_declared_date(self, obj):
        candidacy = obj.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )

        try:
            return CampaignSerializer(candidacy.campaign).data["declared_date"]
        except:
            return None

    def get_headshot(self, obj):
        try:
            return obj.images.get(tag__name="tracker").image
        except:
            return None

    class Meta:
        model = Person
        fields = (
            "full_name",
            "birth_date",
            "party",
            "summary",
            "blurb",
            "headshot",
            "declared_date",
        )
