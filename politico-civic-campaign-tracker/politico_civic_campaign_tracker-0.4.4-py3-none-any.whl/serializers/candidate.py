from campaign.models import Campaign, Endorsement, Staffer
from election.models import Candidate
from government.models import Party
from tracker.models import (
    CandidateRankingSet,
    CandidateRatingCategory,
    Quote,
    Story,
    Tweet,
    CandidateRanking,
    Video,
)
from rest_framework import serializers


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ("label", "short_label", "slug")


class StafferSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.person.full_name

    class Meta:
        model = Staffer
        fields = ("name", "position", "active")


class EndorsementSerializer(serializers.ModelSerializer):
    identity = serializers.SerializerMethodField()

    def get_identity(self, obj):
        return "endorsement-{}".format(obj.pk)

    class Meta:
        model = Endorsement
        fields = (
            "endorser",
            "endorsement_date",
            "active",
            "statement",
            "link",
            "identity",
        )


class CampaignSerializer(serializers.ModelSerializer):
    endorsements = serializers.SerializerMethodField()
    staffers = serializers.SerializerMethodField()

    def get_endorsements(self, obj):
        return EndorsementSerializer(obj.endorsements, many=True).data

    def get_staffers(self, obj):
        return StafferSerializer(obj.staffers, many=True).data

    class Meta:
        model = Campaign
        fields = (
            "endorsements",
            "staffers",
            "website",
            "facebook",
            "twitter",
            "instagram",
            "declared_date",
            "concession_date",
        )


class RatingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateRatingCategory
        fields = ("label", "order")


class TweetSerializer(serializers.ModelSerializer):
    identity = serializers.SerializerMethodField()

    def get_identity(self, obj):
        return "tweet-{}".format(obj.pk)

    class Meta:
        model = Tweet
        fields = ("url", "publish_date", "identity")


class StorySerializer(serializers.ModelSerializer):
    identity = serializers.SerializerMethodField()

    def get_identity(self, obj):
        return "story-{}".format(obj.pk)

    class Meta:
        model = Story
        fields = (
            "url",
            "headline",
            "description",
            "image_url",
            "publish_date",
            "identity",
            "byline",
        )


class QuoteSerializer(serializers.ModelSerializer):
    identity = serializers.SerializerMethodField()

    def get_identity(self, obj):
        return "quote-{}".format(obj.pk)

    class Meta:
        model = Quote
        fields = ("text", "date", "place", "link", "identity")


class CandidateRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateRanking
        fields = ("value", "explanation")


class VideoSerializer(serializers.ModelSerializer):
    identity = serializers.SerializerMethodField()

    def get_identity(self, obj):
        return "video-{}".format(obj.pk)

    class Meta:
        model = Video
        fields = (
            "video_id",
            "publish_date",
            "title",
            "description",
            "identity",
        )


class CandidateSerializer(serializers.ModelSerializer):
    party = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()
    win_rating = serializers.SerializerMethodField()
    ranking = serializers.SerializerMethodField()
    quotes = serializers.SerializerMethodField()
    tweets = serializers.SerializerMethodField()
    stories = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()

    def get_party(self, obj):
        return PartySerializer(obj.party).data

    def get_campaign(self, obj):
        try:
            return CampaignSerializer(obj.campaign).data
        except:
            return None

    def get_win_rating(self, obj):
        try:
            return RatingCategorySerializer(
                obj.win_ratings.latest("date").category
            ).data
        except:
            return None

    def get_ranking(self, obj):
        ranking_set = CandidateRankingSet.objects.latest("date")
        try:
            return CandidateRankingSerializer(
                ranking_set.rankings.get(candidate=obj)
            ).data
        except:
            return None

    def get_quotes(self, obj):
        return QuoteSerializer(obj.quotes, many=True).data

    def get_tweets(self, obj):
        return TweetSerializer(obj.tweets, many=True).data

    def get_stories(self, obj):
        return StorySerializer(obj.stories, many=True).data

    def get_videos(self, obj):
        return VideoSerializer(obj.videos, many=True).data

    class Meta:
        model = Candidate
        fields = (
            "party",
            "campaign",
            "win_rating",
            "ranking",
            "incumbent",
            "quotes",
            "tweets",
            "stories",
            "videos",
        )
