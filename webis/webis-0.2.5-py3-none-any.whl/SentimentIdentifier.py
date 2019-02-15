#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright (C) 2019 Christoph Fink, University of Helsinki
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 3
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.


__all__ = ["SentimentIdentifier"]

import collections.abc
import contextlib
import emojientities  # noqa: F401
import jnius_config
import operator
import os
import os.path
import pandas
import re
import shutil
import statistics
import string

if "JAVA_HOME" not in os.environ:
    try:
        javaHome = os.path.dirname(
            os.path.dirname(
                os.path.realpath(
                    shutil.which("javac")
                )
            )
        )
        os.environ["JAVA_HOME"] = javaHome
    except TypeError:
        raise Exception(
            "Could not find `javac`. \n" +
            "Please set the JAVA_HOME environment variable"
        )

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

# Check whether the ECIR-2015-and-SEMEVAL-2015 compiled java classes
# exist in our cache – otherwise download and compile them BEFORE loading
# jnius
# (a more pythonic implementation did not work (JVM would not refresh),
# see a4fba118 and earlier)

# PyJnius, java classes, java types
for javaClass in [
    "Tweet",
    "SentimentSystemNRC",
    "SentimentSystemGUMLTLT",
    "SentimentSystemKLUE",
    "SentimentSystemTeamX"
]:
    if not os.path.exists(
        os.path.join(
            packageDirectory,
            "bin",
            "{}.class".format(javaClass)
        )
    ):
        import webis.util
        webis.util.downloadWebis(packageDirectory)
        break

import jnius  # noqa: E402

# Java types and classes
JHashSet = jnius.autoclass("java.util.HashSet")
JString = jnius.autoclass("java.lang.String")

# Java types and classes from ECIR-2015-and-SEMEVAL-2015
JTweet = jnius.autoclass("Tweet")
JSentimentSystemNRC = jnius.autoclass("SentimentSystemNRC")
JSentimentSystemGUMLTLT = jnius.autoclass("SentimentSystemGUMLTLT")
JSentimentSystemKLUE = jnius.autoclass("SentimentSystemKLUE")
JSentimentSystemTeamX = jnius.autoclass("SentimentSystemTeamX")


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
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

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
                tweets (list of tuple of str or pandas.DataFrame or dict)

            If `tweets` is a pandas.DataFrame, first column is assumed
            to be an id, second column the text to be classified.

            If `tweets` is a list, each list item is a tuple of id and text
            `[(tweetId, tweetText), (tweetId, tweetText) … ]`

            If `tweets` is a dict, the keys correspond to tweetIds, the
            values to tweetText. `{tweetId: tweetText, tweetId: tweetText, …}`
        """
        returnPandasDataFrame = False
        returnDict = False

        if isinstance(tweets, pandas.DataFrame):
            tweets = [
                (row[0], row[1]) for (_, row) in tweets.iterrows()
            ]
            returnPandasDataFrame = True
        elif isinstance(tweets, collections.abc.Mapping):
            tweets = [
                (i, tweets[i])
                for i in tweets
            ]
            returnDict = True

        tweets = self._identifySentiment(tweets)

        if returnPandasDataFrame:
            tweets = pandas.DataFrame(tweets)
        elif returnDict:
            tweets = {
                tweet["tweetId"]: tweet["sentiment"]
                for tweet in tweets
            }
        else:
            tweets = [
                (tweet["tweetId"], tweet["sentiment"])
                for tweet in tweets
            ]

        return tweets

    def _identifySentiment(self, tweets):
        jTweets = JHashSet()

        # assume that all tweetIds are of the same type
        tweetIdType = type(tweets[0][0])

        for tweet in tweets:
            (tweetId, tweetText) = tweet
            tweetText = \
                self._cleanTweetText(tweetText)\
                .strip()\
                .encode("latin-1", errors="ignore")

            if len(tweetText):
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

            # # hide output (the Java backend is horribly verbose)
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
                    "tweetId": tweetIdType(t),
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
