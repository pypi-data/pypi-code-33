import feedparser
import json

from django.core.management.base import BaseCommand
from election.models import Candidate
from slugify import slugify
from tracker.utils.aws import defaults, get_bucket
from webpreview import OpenGraph


class Command(BaseCommand):
    def parse_feed(self, candidate):
        data = []

        d = feedparser.parse("https://www.politico.com/rss/donald-trump.xml")
        for entry in d.entries:
            entry_data = {
                "title": entry.title,
                "publish_date": entry.published,
                "link": entry.link,
                "author": self.get_author(entry.author),
                "image": self.get_image(entry.link),
            }

            data.append(entry_data)

        return data

    def get_author(self, author):
        if "(" in author:
            return author.split("(")[1].split(")")[0]
        else:
            return author

    def get_image(self, link):
        data = OpenGraph(link, ["og:image"])
        return data.image

    def publish_feed(self, candidate, feed):
        key = "election-results/2020/candidate-tracker/{}/stories.json".format(
            slugify(candidate.person.full_name)
        )

        print(key)

        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json.dumps(feed),
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def handle(self, *args, **options):
        candidates = Candidate.objects.filter(
            race__cycle__slug="2020", race__office__slug="president"
        )

        for candidate in candidates:
            feed = self.parse_feed(candidate)
            self.publish_feed(candidate, feed)
