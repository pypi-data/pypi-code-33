from rest_framework.renderers import JSONRenderer
from slugify import slugify
from tqdm import tqdm
from tracker.serializers import (
    CandidateRatingCategorySerializer,
    PersonSerializer,
    PersonHomeSerializer,
    PersonSummarySerializer,
    StoryFeedSerializer,
    EndorsementFeedSerializer,
    QuoteFeedSerializer,
    TweetFeedSerializer,
    VideoFeedSerializer,
)
from tracker.utils.aws import defaults, get_bucket


def bake_candidate(candidate):
    data = PersonSerializer(candidate.person).data
    json_string = JSONRenderer().render(data)
    key = "election-results/2020/presidential-candidates/{}/data.json".format(
        slugify(candidate.person.full_name)
    )
    bucket = get_bucket()
    bucket.put_object(
        Key=key,
        ACL=defaults.ACL,
        Body=json_string,
        CacheControl=defaults.CACHE_HEADER,
        ContentType="application/json",
    )


def sort_feed_item(item):
    if item["identity"].startswith("quote"):
        return item["date"]

    if item["identity"].startswith("tweet"):
        return item["publish_date"]

    if item["identity"].startswith("endorsement"):
        return item["endorsement_date"]

    if item["identity"].startswith("story"):
        return item["publish_date"]

    if item["identity"].startswith("video"):
        return item["publish_date"]


def bake_feed(candidates):
    feed_items = []
    print("Baking master feed")
    for candidate in tqdm(candidates):
        endorsements = EndorsementFeedSerializer(
            candidate.campaign.endorsements, many=True
        ).data
        stories = StoryFeedSerializer(candidate.stories, many=True).data
        quotes = QuoteFeedSerializer(candidate.quotes, many=True).data
        tweets = TweetFeedSerializer(candidate.tweets, many=True).data
        videos = VideoFeedSerializer(candidate.videos, many=True).data

        feed_items.extend(endorsements)
        feed_items.extend(stories)
        feed_items.extend(quotes)
        feed_items.extend(videos)
        feed_items.extend(tweets)

    sorted_feed = sorted(feed_items, key=sort_feed_item, reverse=True)
    json_string = JSONRenderer().render(sorted_feed)
    key = "election-results/2020/presidential-candidates/feed.json"
    bucket = get_bucket()
    bucket.put_object(
        Key=key,
        ACL=defaults.ACL,
        Body=json_string,
        CacheControl=defaults.CACHE_HEADER,
        ContentType="application/json",
    )


def bake_homepage(candidates):
    people = []
    print("Baking homepage candidates")
    for candidate in tqdm(candidates):
        person = PersonHomeSerializer(candidate.person).data
        people.append(person)

    json_string = JSONRenderer().render(people)
    key = "election-results/2020/presidential-candidates/candidates.json"
    bucket = get_bucket()
    bucket.put_object(
        Key=key,
        ACL=defaults.ACL,
        Body=json_string,
        CacheControl=defaults.CACHE_HEADER,
        ContentType="application/json",
    )


def bake_feed_summary(candidates):
    people = []
    print("Baking candidate summaries")
    for candidate in tqdm(candidates):
        person = PersonSummarySerializer(candidate.person).data
        people.append(person)

    json_string = JSONRenderer().render(people)
    key = "election-results/2020/presidential-candidates/summary.json"
    bucket = get_bucket()
    bucket.put_object(
        Key=key,
        ACL=defaults.ACL,
        Body=json_string,
        CacheControl=defaults.CACHE_HEADER,
        ContentType="application/json",
    )


def bake_categories(categories):
    print("Baking categories")
    data = CandidateRatingCategorySerializer(categories, many=True).data
    json_string = JSONRenderer().render(data)
    key = "election-results/2020/presidential-candidates/categories.json"
    bucket = get_bucket()
    bucket.put_object(
        Key=key,
        ACL=defaults.ACL,
        Body=json_string,
        CacheControl=defaults.CACHE_HEADER,
        ContentType="application/json",
    )
