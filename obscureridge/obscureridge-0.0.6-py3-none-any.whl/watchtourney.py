###################################################

from obscureridge import lichess
from obscureridge.urllibutils import geturljson
from obscureridge.chatbot import Chatbot

from os import environ
import time
import random

###################################################

def getallfeaturedtourneys(kinds = ["created", "started"]):
    alltourneys = geturljson(lichess.getalltourneysurl())    
    allfeaturedtourneys = []
    for kind in kinds:
        tourneys = alltourneys[kind]
        for tourney in tourneys:
            createdby = tourney["createdBy"]
            name = tourney["fullName"]
            if ( createdby == lichess.FEATURED_TOURNEY_CREATOR ) and ( name == lichess.FULL_FEATURED_TOURNEY_NAME ):
                allfeaturedtourneys.append(tourney)
    return allfeaturedtourneys

###################################################

class MyChatbot(Chatbot):
    def __init__(self, lila2, tid):
        super().__init__(lila2, tid)

    def talkhandler(self, user, msg):
        print("MY message {} : {}".format(user, msg))

    def crowdhandler(self, nb, users, anons):
        return
        print("MY crowd {} : users = {} , anons = {}".format(nb, " ".join(users), anons))

    def gamefinishedhandler(self, gid):                
        gobj = self.games[gid]
        ratingbias = gobj["ratingBias"]
        score = gobj["score"]
        nomoves = len(gobj["moves"])
        whitename = gobj["whiteName"]
        whiterating = gobj["whiteRating"]
        blackname = gobj["blackName"]
        blackrating = gobj["blackRating"]
        rs = ratingbias * score        
        if score < 0:
            rs = rs * 2        
        print("game finished", whitename, whiterating, blackname, blackrating, score, rs)
        if ( rs < -100 ) and ( nomoves > 1 ):            
            upset = whitename            
            upsetloser = blackname
            if score < 0:
                upset = blackname
                upsetloser = whitename            
            self.say(random.choice([
                "what a game {} wins against {}".format(upset, upsetloser),
                "wow {} defeats {}".format(upset, upsetloser),
                "unbelievable {} beating {} higher rated".format(upset, abs(ratingbias))
            ]))
            time.sleep(2)
            if upset == blackname:
                self.say("with black!")
            time.sleep(2)
            self.say(random.choice([
                "grats @{}".format(upset),
                "gg @{}".format(upset),
                "well done @{}".format(upset)
            ]))
        elif ( ( whiterating - blackrating ) > 100 ) and ( score == 0 ):            
            say("lol {} draws {} with black".format(blackname, whitename))
            time.sleep(2)
            self.say(random.choice([
                "grats @{}".format(blackname),
                "gg @{}".format(blackname),
                "well done @{}".format(blackname)
            ]))

bottids = {}

def startup():
    chatuserlila2 = environ.get("CHATUSERLILA2", None)

    while True:
        print("getting tourneys for chatbot")
        tourneys = getallfeaturedtourneys()

        if len(tourneys) > 0:
            tourney = tourneys[0]
            tid = tourney["id"]
            print("found tourney {}".format(tid))
            if not ( tid in bottids ):
                print("no bot yet, creating one")
                chatbot = MyChatbot(chatuserlila2, tid)
                chatbot.startup()
                bottids[tid] = True
            else:
                print("bot already up")
        else:
            print("could not find tourney")

        time.sleep(180)

###################################################