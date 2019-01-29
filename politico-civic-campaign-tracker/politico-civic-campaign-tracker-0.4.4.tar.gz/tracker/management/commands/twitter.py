import json
import requests
import time
import twitter

from django.conf import settings
from django.core.management.base import BaseCommand
from election.models import Candidate
from tracker.conf import Settings as app_settings
from tracker.models import Tweet


class Command(BaseCommand):
    def process_mention(self, mention, api):
        user = mention.user.screen_name

        if user not in app_settings.TWITTER_WHITELIST:
            return

        candidates = self.scan_text(mention.text)

        kwargs = {}
        kwargs["url"] = "https://twitter.com/{}/status/{}".format(
            user, mention.id
        )
        kwargs["publish_date"] = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.strptime(mention.created_at, "%a %b %d %H:%M:%S +0000 %Y"),
        )
        kwargs["tweet_text"] = mention.text
        kwargs["tweet_handle"] = user

        if len(candidates) == 1:
            kwargs["candidate"] = Candidate.objects.get(
                person__full_name=candidates[0],
                race__cycle__slug="2020",
                race__office__slug="president",
            )

        tweet = Tweet.objects.get_or_create(**kwargs)[0]

        if len(candidates) != 1:
            self.send_to_slack(user, tweet)

        api.PostRetweet(mention.id)

    def scan_text(self, text):
        candidates = Candidate.objects.filter(
            race__cycle__slug="2020", race__office__slug="president"
        )

        found_entities = []

        for candidate in candidates:
            if candidate.person.full_name in text:
                found_entities.append(candidate.person.full_name)

        return found_entities

    def send_to_slack(self, user, tweet):
        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": settings.SLACKFORMS_FEEDBACK_CHANNEL,
            "text": "{} tweeted to us, but we couldn't figure what candidate they were talking about. Help! {}".format(
                user, tweet.url
            ),
            "edit": "Pick a Candidate",
            "form": "2020-tweet",
            "data_id": tweet.id,
        }
        r = requests.post(
            url=settings.SLACKFORMS_CALLBACK_URL, data=callback_data
        )
        print(r)

    def handle(self, *args, **options):
        api = twitter.Api(
            consumer_key=app_settings.TWITTER_CONSUMER_KEY,
            consumer_secret=app_settings.TWITTER_CONSUMER_SECRET,
            access_token_key=app_settings.TWITTER_ACCESS_TOKEN_KEY,
            access_token_secret=app_settings.TWITTER_ACCESS_TOKEN_SECRET,
        )

        kwargs = {"contributor_details": True}

        if len(Tweet.objects.all()) > 0:
            latest_tweet = Tweet.objects.latest("publish_date")

            if latest_tweet:
                kwargs["since_id"] = latest_tweet.url.split("/")[-1]

        mentions = api.GetMentions(**kwargs)

        for mention in mentions:
            self.process_mention(mention, api)
