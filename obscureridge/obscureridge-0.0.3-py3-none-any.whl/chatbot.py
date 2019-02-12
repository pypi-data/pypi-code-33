###################################################

import threading, time

import websocket

from queue import Queue
import json

import requests

###################################################

from obscureridge import lichess

###################################################

KEEPALIVE_SLEEP = 3
MAX_KEEPALIVE_SECS = lichess.MAX_TOURNEY_LENGTH_MINS * 60

###################################################

class Message:
    def __init__(self, kind, data):
        self.kind = kind
        self.data = data

    def __repr__(self):
        return "{}".format(self.__dict__)

class Chatbot:
    def __init__(self,
        lila2,
        tid
    ):
        self.lila2 = lila2
        self.tid = tid
        self.tourneychaturl = lichess.tourneychaturl(self.tid)
        print("initialized chatbot {} {}".format(self.tid, self.tourneychaturl))

    def say_thread_target(self, msg):
        self.ws.send(json.dumps({
            "t": "talk",
            "d": msg
        }))
        print("said {} : {}".format(self.tid, msg))

    def say(self, msg):
        threading.Thread(target = self.say_thread_target, args = (msg,)).start()

    def talkhandler(self, user, msg):
        print("message {} : {}".format(user, msg))

    def crowdhandler(self, nb, users, anons):
        print("crowd {} : users = {} , anons = {}".format(nb, " ".join(users), anons))

    def gamefinishedhandler(self, gid):        
        gobj = self.games[gid]
        print("game finished {} : {} ( {} {} ) - {} ( {} {} ) {} \n {}".format(
            gid,
            gobj["whiteName"],
            gobj["whiteRating"],
            gobj["whiteRatingDiff"],
            gobj["blackName"],
            gobj["blackRating"],
            gobj["blackRatingDiff"],
            gobj["score"],
            gobj["moves"])
        )

    def messagehandler_thread_target(self):
        while self.alive:            
            try:
                message = self.messagequeue.get(timeout = KEEPALIVE_SLEEP)                                
                if message.kind == "message":
                    self.talkhandler(message.data["u"], message.data["t"])
                elif message.kind == "crowd":
                    self.crowdhandler(message.data.get("nb", 0), message.data.get("users", []), message.data.get("anons", 0))
                elif message.kind == "gamefinished":
                    self.gamefinishedhandler(message.data)
            except:
                pass
        print("message handler thread terminated for {}".format(self.tid))

    def keepalive_thread_target(self):                
        while self.keepalivecnt > 0:            
            self.ws.send("null")
            time.sleep(KEEPALIVE_SLEEP)
            self.keepalivecnt -= 1
        self.ws.close()
        print("keep alive thread terminated for {}".format(self.tid))

    def read_games_thread_target(self):
        first = True
        while self.alive:
            r = requests.get(lichess.gettourneygamesurl(self.tid), headers = {"Accept": "application/x-ndjson"}, stream = True)
            for line in r.iter_lines():
                try:
                    line = line.decode("utf-8")                    
                    gobj = json.loads(line)
                    gid = gobj["id"]
                    status = gobj["status"]                    
                    if not ( status == "started" ):
                        if not ( gid in self.gameids ):
                            self.gameids.append(gid)
                            players = gobj.get("players", {})
                            for color in ["white", "black"]:
                                player = players.get(color, {})
                                rating = player.get("rating", 1500)
                                ratingdiff = player.get("ratingDiff", 0)
                                user = player.get("user", {})
                                gobj[color + "Name"] = user.get("name")
                                gobj[color + "Rating"] = rating
                                gobj[color + "RatingDiff"] = ratingdiff
                                winner = gobj.get("winner", None)
                                gobj["winner"] = winner
                                gobj["score"] = 0                                
                                if winner:
                                    if winner == "white":
                                        gobj["score"] = 1
                                    else:
                                        gobj["score"] = -1
                            gobj["ratingBias"] = gobj["whiteRating"] - gobj["blackRating"]
                            moves = gobj.get("moves", "")
                            if moves == "":
                                gobj["moves"] = []
                            else:
                                gobj["moves"] = moves.split(" ")
                            self.games[gid] = gobj                            
                            if ( not first ):
                                self.messagequeue.put(Message("gamefinished", gid))
                        else:
                            r.close()
                            break
                except:
                    pass            
            first = False
            time.sleep(5 * KEEPALIVE_SLEEP)
        print("read games thread terminated for {}".format(self.tid))

    def shutdown(self):
        self.keepalivecnt = 0

    def on_open(self):
        print("socket for {} opened".format(self.tid))
        threading.Thread(target = self.keepalive_thread_target).start()
        threading.Thread(target = self.messagehandler_thread_target).start()
        threading.Thread(target = self.read_games_thread_target).start()

    def on_message(self, message):
        try:
            mobj = json.loads(message)
            kind = mobj["t"]
            data = mobj["d"]            
            self.messagequeue.put(Message(kind, data))
        except:
            pass

    def startup_thread_target(self):
        print("starting up chatbot for {}".format(self.tid))

        self.keepalivecnt = int(MAX_KEEPALIVE_SECS / KEEPALIVE_SLEEP)        

        self.alive = True

        self.messagequeue = Queue()

        self.gameids = []
        self.games = {}

        self.ws = websocket.WebSocketApp(self.tourneychaturl,        
            on_open = self.on_open,        
            on_message = self.on_message,
            cookie = "lila2={}".format(self.lila2)
        )

        self.ws.run_forever(
            host = "socket.lichess.org",
            origin = "https://lichess.org"
        )

        print("socket terminated for {}".format(self.tid))

        self.alive = False

    def startup(self):
        threading.Thread(target = self.startup_thread_target).start()

###################################################