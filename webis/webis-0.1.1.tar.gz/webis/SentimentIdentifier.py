#!/bin/env python

__all__ = ["SentimentIdentifier"]

import contextlib
import emojientities  # noqa: F401
import jnius_config
import operator
import os
import pandas
import re
import statistics
import string

if "JAVA_HOME" not in os.environ:
    raise Exception("Please set the JAVA_HOME environment variable")

packageDirectory = os.path.abspath(
    os.path.join(
        (
            os.environ.get('APPDATA') or
            os.environ.get('XDG_CONFIG_HOME') or
            os.path.join(os.environ['HOME'], '.config')
        ),
        "python-webis",
        "ECIR-2015-and-SEMEVAL-2015"
    )
)

for path in (
    "bin",
    "lib",
    "lib/*",
    "src"
):
    jnius_config.add_classpath(
        os.path.join(
            packageDirectory,
            path
        )
    )

import jnius  # noqa: E402

# Java types and classes
JHashSet = jnius.autoclass("java.util.HashSet")
JString = jnius.autoclass("java.lang.String")

# Java types and classes from ECIR-2015-and-SEMEVAL-2015
for retry in range(3):
    try:
        JTweet = jnius.autoclass("Tweet")
        JSentimentSystemNRC = jnius.autoclass("SentimentSystemNRC")
        JSentimentSystemGUMLTLT = jnius.autoclass("SentimentSystemGUMLTLT")
        JSentimentSystemKLUE = jnius.autoclass("SentimentSystemKLUE")
        JSentimentSystemTeamX = jnius.autoclass("SentimentSystemTeamX")
        break
    except jnius.JavaException:
        import webis.util
        webis.util.downloadWebis(packageDirectory)


@contextlib.contextmanager
def chdir(path):
    originalWorkingDirectory = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(originalWorkingDirectory)


class SentimentIdentifier(object):
    """
        Class to identify the sentiment of Tweets (or other social
        media posts)
    """
    def __init__(self, tweets=None):
        if tweets is not None:
            return self.identifySentiment(tweets)

    def _cleanTweetText(self, tweetText):
        # split into words
        tweetText = tweetText.split()

        # filter out hashtags (#…), mentions (@…) and urls (https?://…),
        # and strip newlines and empty characters
        rePattern = re.compile(
            r'^[#@]\S|^https?:\/\/|^RT$'
        )
        tweetText = [
            word for word in tweetText
            if not rePattern.match(word)
        ]

        # join words again
        tweetText = " ".join(tweetText)

        # remove emoji characters
        tweetText = "".join([
                c for c in tweetText
                if (c not in string.emojis)
                and (c not in string.punctuation)
        ])

        return tweetText

    def identifySentiment(self, tweets):
        """
            Identify the sentiment of `tweets`

            Args:
                tweets (list of tuple of str or pandas.DataFrame)

            If `tweets` is a pandas.DataFrame, first column is assumed
            to be an id, second column the text to be classified.

            If `tweets` is a list, each list item is a tuple of id and text
            `[(tweetId, tweetText), (tweetId, tweetText) … ]`
        """
        returnPandasDataFrame = False

        if isinstance(tweets, pandas.DataFrame):
            tweets = [
                (row[0], row[1]) for (_, row) in tweets.iterrows()
            ]
            returnPandasDataFrame = True

        tweets = self._identifySentiment(tweets)

        if returnPandasDataFrame:
            tweets = pandas.DataFrame(tweets)

        return tweets

    def _identifySentiment(self, tweets):
        jTweets = JHashSet()

        for tweet in tweets:
            (tweetId, tweetText) = tweet
            tweetText = \
                self._cleanTweetText(tweetText)\
                .strip()\
                .encode("latin-1", errors="ignore")

            if len(tweetText) > 50:
                jTweets.add(
                    JTweet(
                        JString(tweetText),
                        JString("unknwn"),
                        JString(str(tweetId))
                    )
                )

        if len(tweets):

            del(tweets)
            tweets = {}

            # # hide output (these scripts are horribly verbose
            # stdout = sys.stdout
            # stderr = sys.stderr
            # sys.stdout = open(os.devnull, "w")
            # sys.stderr = open(os.devnull, "w")

            for JSentimentSystem in (
                JSentimentSystemNRC,
                JSentimentSystemGUMLTLT,
                JSentimentSystemKLUE,
                JSentimentSystemTeamX
            ):
                with chdir(packageDirectory):
                    try:
                        jSentimentSystem = JSentimentSystem(jTweets)
                        tweetsWithSentiment = \
                            jSentimentSystem \
                            .test(JString("")) \
                            .entrySet() \
                            .toArray()

                        for tweet in tweetsWithSentiment:
                            sentimentProbabilities = \
                                tweet.getValue().getResultDistribution()
                            tweetId = \
                                tweet \
                                .getValue() \
                                .getTweet() \
                                .getTweetID()

                            if tweetId not in tweets:
                                tweets[tweetId] = {
                                    "positive": [],
                                    "neutral": [],
                                    "negative": []
                                }
                            tweets[tweetId]["positive"].append(
                                sentimentProbabilities[0]
                            )
                            tweets[tweetId]["neutral"].append(
                                sentimentProbabilities[1]
                            )
                            tweets[tweetId]["negative"].append(
                                sentimentProbabilities[2]
                            )

                    except jnius.JavaException as e:
                        print(
                            "jnius.JavaException occured:\n",
                            str(e),
                            str(e.args)
                        )
                        continue

                # # reset output
                # sys.stdout = stdout
                # sys.stderr = stderr
                # del stdout, stderr

            for t in tweets:
                for s in ("positive", "neutral", "negative"):
                    tweets[t][s] = statistics.mean(tweets[t][s])

            tweets = [
                {
                    "tweetId": t,
                    "sentiment": max(
                        tweets[t].items(),
                        key=operator.itemgetter(1)
                    )[0]
                }
                for t in tweets
            ]

        else:  # len(tweets)
            tweets = []

        return tweets
