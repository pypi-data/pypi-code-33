from rs4 import siesta
from . import local
from rs4 import logger
import time

def make_api (point):
    if not isinstance (point, str):
        return point
    else:
        return siesta.API (point)
    
class Documents (local.Documents):
    def __init__ (self, name, addr, logger):
        self.addr = addr
        self.logger = logger
        self.api = make_api (self.addr)
        self.name = name
        self.counts = [0, 0]
    
    def __enter__ (self):
        return self
    
    def __exit__ (self, type, value, tb):
        pass
            
    def add (self, doc):
        if doc._id:
            return self.update (doc)
        #self.logger ("#{} add document".format (self.counts [0]), "info", self.name)
        self.counts [0] += 1
        r = self.api.cols (self.name).documents.post (doc.as_dict ())
        assert r.status_code == 202
        return r
    
    def update (self, doc):
        assert doc._id, "_id required"
        #self.logger ("#{} upsert document ({})".format (self.counts [0], doc._id), "info", self.name)
        self.counts [0] += 1
        r = self.api.cols (self.name).documents (doc._id).put (doc.as_dict ())
        assert r.status_code == 202
        return r
    
    def delete (self, id):
        #self.logger ("#{} delete document ({})".format (self.counts [1], id), "info", self.name)
        self.counts [1] += 1
        r = self.api.cols (self.name).documents (id).delete ()
        assert r.status_code == 202
        return r
    
    def qdelete (self, q, lang = "en", analyze = 1):
        r = self.api.cols (self.name).documents.delete (q = q, lang = lang, analyze = analyze)
        assert r.status_code == 202        
    
    def truncate (self, name):
        r = self.api.cols (self.name).documents.delete (truncate_confirm = name)
        assert r.status_code == 202
        return r
    
    def search (self, q, **karg):
        r = self.api.cols (self.name).documents.get (q = q, **karg)
        assert r.status_code == 200
        return r.data
    
    def get (self, id, **karg):
        r = self.api.cols (self.name).documents.get (q = "_id:{}".format (id), **karg)
        assert r.status_code == 200
        return r.data
    
    
class Collection (local.Collection):
    def __init__ (self, name, config, addr, logger = None):
        self.addr = addr
        self.logger = logger
        self.api = make_api (self.addr)
        self.name = name
        self.config = config
        self.documents = Documents (self.name, self.addr, logger)
    
    def _wait (self, flag = True):
        for i in range (60):
            if self.is_active () is flag:
                return True
            else:
                time.sleep (1)
        return False        
    
    def close (self):
        pass
            
    def is_active (self):
        return self.name in self.api.cols.get_ ().data ["collections"]
    
    def save (self):
        r = self.api.cols (self.name).put (self.config)        
        assert r.status_code == 200, "Collection update failed"
            
    def commit (self):
        r = self.api.cols (self.name).commit.post ({})
        assert r.status_code == 205
    
    def rollback (self):
        r = self.api.cols (self.name).rollback.post ({})
        assert r.status_code == 205
            
    def drop (self, include_date = False):
        if not self.is_active ():
            return
        if include_date:
            r = self.api.cols (self.name).delete (side_effect = 'data')
        else:
            r = self.api.cols (self.name).delete ()
        assert r.status_code == 202        
        self._wait (False)
    
    
class Delune:
    def __init__ (self, addr):
        self.addr = addr
        self.logger = logger.screen_logger ()
        self.api = make_api (self.addr)
                 
    def lscol (self):
        return self.api.cols.get_ ().data ["collections"]
    
    def load (self, name):
        if name not in self.lscol ():
            raise NameError ("collection not found")
        config = self.api.cols (name).config.get ().data            
        return Collection (name, config, self.addr, self.logger)
    
    def create (self, name, data_dirs, version = 1, **kargs):
        if name in self.lscol ():
            raise NameError ("collection exists") 
        config = local.make_config (name, data_dirs, version, **kargs)
        r = self.api.cols (name).post (config)
        assert r.status_code == 202, "Collection creating failed"
        col = Collection (name, config, self.addr, self.logger)
        assert col._wait (), "Collection creating timeout"
        return col
        
    