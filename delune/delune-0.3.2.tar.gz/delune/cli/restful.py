from rs4 import siesta
from . import local
from rs4 import logger
import time

class Documents (local.Documents):
    def __init__ (self, name, addr, logger):
        self.addr = addr
        self.logger = logger
        self.api = siesta.API (self.addr)
        self.name = name
        self.counts = [0, 0]
    
    def __enter__ (self):
        return self
    
    def __exit__ (self, type, value, tb):
        pass
            
    def add (self, doc):
        if doc._id:
            return self.update (doc)    
        self.logger ("#{} add document".format (self.counts [0]), "info", self.name)
        self.counts [0] += 1
        self.api.ops (self.name).documents.post (doc.as_dict ())
    
    def update (self, doc):
        assert doc._id, "_id required"
        self.logger ("#{} upsert document ({})".format (self.counts [0], doc._id), "info", self.name)
        self.counts [0] += 1
        return self.api.ops (self.name).documents (doc._id).patch (doc.as_dict ())
    
    def delete (self, id):
        self.logger ("#{} delete document ({})".format (self.counts [1], id), "info", self.name)
        self.counts [1] += 1
        return self.api.ops (self.name).documents (id).delete ()
    
    def qdelete (self, qs):
        self.api.ops (self.name).documents.delete (q = qs)
    
    def truncate (self, name):
        self.api.ops (self.name).documents.delete (truncate_confirm = name)
        
    def search (self, qs):
        return self.api (self.name).search.get (q = qs)
    
    def guess (self, qs):
        return self.api (self.name).guess.get (q = qs)
    
    def commit (self):
        self.api.ops (self.name).commit.get ()
    
    def index (self):
        raise AttributeError 
    
    def rollback (self):
        self.api.ops (self.name).rollback.get ()
        

class Collection:
    def __init__ (self, name, config, addr, logger = None):
        self.addr = addr
        self.logger = logger
        self.api = siesta.API (self.addr)
        self.name = name
        self.config = config
        self.documents = Documents (self.name, self.addr, logger)
    
    def _wait (self, flag = True):
        for i in range (60):
            if self.is_active () is flag:
                break
            else:
                time.sleep (1)
            
    def is_active (self):
        return self.name in self.api.ops.list.get ().data ["collections"]
    
    def save (self):
        if self.is_active ():
            self.api.ops (self.name).patch (self.config)            
        else:
             self.api.ops (self.name).post (self.config)   
        self._wait (True)
            
    def drop (self, include_date = False):
        if not self.is_active ():
            return
        if include_date:
            self.api.ops (self.name).delete (side_effect = 'data')
        else:
            self.api.ops (self.name).delete ()    
        self._wait (False)
    
    def undrop (self):
        if self.is_active ():
            return
        self.api.ops (self.name).get (side_effect = 'undo')
        self._wait (True)
    
    
class Delune:
    def __init__ (self, addr):
        self.addr = addr
        self.logger = logger.screen_logger ()
        self.api = siesta.API (self.addr)
        self.cols = self.lscol ()
         
    def lscol (self):
        return self.api.ops.list.get ().data ["collections"]
    
    def load (self, name):
        if name not in self.cols:
            raise NameError ("collection not found")
        config = self.api.ops (name).config.get ().data            
        return Collection (name, config, self.addr, self.version)
    
    def create (self, name, data_dirs = [], version = 1, **kargs):
        config = local.make_config (name, data_dirs, version, **kargs)
        return Collection (name, config, self.addr, self.logger)
    