import delune
import os
import json

#-----------------------------------------------------------------

def decorate (app):
    
    @app.route ("/test", methods = ["GET"])
    def test (was):
        return was.response.API (tested = "DELUNE PUBLIC API")
    
    @app.route ("/<alias>/documents/<_id>", methods = ["GET"])
    def documents (was, alias, _id, nthdoc = 0):
        return was.response.API (delune.query (alias, "_id:" + _id, nthdoc = nthdoc))
            
    @app.route ("/<alias>/search", methods = ["GET", "POST", "OPTIONS"])
    def query (was, alias, **args):
        q = args.get ("q")
        if not q:
            return was.response.Fault ("400 Bad Request", 40003, 'parameter q required')
        
        l = args.get ("lang", "en")
        analyze = args.get ("analyze", 1)
        
        o = args.get ("offset", 0)
        f = args.get ("limit", 10)
        s = args.get ("sort", "")
        w = args.get ("snippet", 30)    
        r = args.get ("partial", "")
        d = args.get ("nthdoc", 0)    
        data = args.get ("data", 1)
        
        if type (q) is list:
            return was.response.API ([delune.query (alias, eq, o, f, s, w, r, l, d, analyze, data, limit = 1) for eq in q])
        return was.response.API (delune.query (alias, q, o, f, s, w, r, d, l, analyze, data, limit = 1))

    @app.route ("/<alias>/guess", methods = ["GET", "POST", "OPTIONS"])
    def guess (was, alias, **args):    
        # args: q = '', l = 'en', c = "naivebayes", top = 0, cond = ""
        q = args.get ("q")
        if not q:
            return was.response.Fault ("400 Bad Request", 40003, 'parameter q required')                
        l = args.get ("lang", 'en')
        c = args.get ("clf", 'naivebayes')
        top = args.get ("top", 0)
        cond = args.get ("cond", '')
        if type (q) is list:
            return was.response.API ([delune.guess (alias, eq, l, c, top, cond) for eq in q])
        return was.response.API (delune.guess (alias, q, l, c, top, cond))
        
    @app.route ("/<alias>/cluster", methods = ["GET", "POST", "OPTIONS"])
    def cluster (was, alias, **args):
        q = args.get ("q")
        if not q:
            return was.response.Fault ("400 Bad Request", 40003, 'parameter q required')
        l = args.get ("lang", 'en')    
        if type (q) is list:
            return was.response.API ([delune.cluster (alias, eq, l) for eq in q])    
        return was.response.API (delune.cluster (alias, q, l))

    @app.route ("/<alias>/stem", methods = ["GET", "POST", "OPTIONS"])
    def stem (was, alias, **args):
        q = args.get ("q")
        if not q:
            returnwas.response.Fault ("400 Bad Request", 40003, 'parameter q required')
        if isinstance (q, str):
            q = q.split (",")
        l = args.get ("lang", 'en')
        return was.response.API (dict ([(eq, " ".join (delune.stem (alias, eq, l))) for eq in q]))    

    @app.route ("/<alias>/analyze", methods = ["GET", "POST", "OPTIONS"])
    def analyze (was, alias, **args):
        q = args.get ("q")
        if not q:
            return was.response.Fault ("400 Bad Request", 40003, 'parameter q required')
        l = args.get ("lang", 'en')
        return was.response.API (delune.analyze (alias, q, l))
