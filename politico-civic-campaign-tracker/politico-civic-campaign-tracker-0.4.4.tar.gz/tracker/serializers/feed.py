from rest_framework import serializers
from campaign.models import Endorsement
from slugify import slugify
from tracker.models import Story, Tweet, Quote, Video


class EndorsementFeedSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    candidate_url = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.endorsee.candidate.person.first_name

    def get_last_name(self, obj):
        return obj.endorsee.candidate.person.last_name

    def get_candidate_url(self, obj):
        name = obj.endorsee.candidate.person.full_name
        return "./{}".format(slugify(name))

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
            "first_name",
            "last_name",
            "candidate_url",
            "identity",
        )


class StoryFeedSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    candidate_url = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.candidate.person.first_name

    def get_last_name(self, obj):
        return obj.candidate.person.last_name

    def get_candidate_url(self, obj):
        name = obj.candidate.person.full_name
        return "./{}".format(slugify(name))

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
            "first_name",
            "last_name",
            "candidate_url",
            "identity",
        )


class TweetFeedSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    candidate_url = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.candidate.person.first_name

    def get_last_name(self, obj):
        return obj.candidate.person.last_name

    def get_candidate_url(self, obj):
        name = obj.candidate.person.full_name
        return "./{}".format(slugify(name))

    def get_identity(self, obj):
        return "tweet-{}".format(obj.pk)

    class Meta:
        model = Tweet
        fields = (
            "url",
            "publish_date",
            "identity",
            "first_name",
            "last_name",
            "candidate_url",
            "identity",
        )


class QuoteFeedSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    candidate_url = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.candidate.person.first_name

    def get_last_name(self, obj):
        return obj.candidate.person.last_name

    def get_candidate_url(self, obj):
        name = obj.candidate.person.full_name
        return "./{}".format(slugify(name))

    def get_identity(self, obj):
        return "quote-{}".format(obj.pk)

    class Meta:
        model = Quote
        fields = (
            "text",
            "date",
            "place",
            "link",
            "first_name",
            "last_name",
            "candidate_url",
            "identity",
        )


class VideoFeedSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    candidate_url = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.candidate.person.first_name

    def get_last_name(self, obj):
        return obj.candidate.person.last_name

    def get_candidate_url(self, obj):
        name = obj.candidate.person.full_name
        return "./{}".format(slugify(name))

    def get_identity(self, obj):
        return "video-{}".format(obj.pk)

    class Meta:
        model = Video
        fields = (
            "video_id",
            "publish_date",
            "title",
            "description",
            "first_name",
            "last_name",
            "candidate_url",
            "identity",
        )
