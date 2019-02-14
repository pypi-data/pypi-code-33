import os
import ray
# ray.init()
import pyarrow
import time
from pathlib import Path
from funhandler.blocks import StoreBlock
from funtime import Store
from loguru import logger
# 
class MrayStorage(StoreBlock):
    def __init__(self, name, redis_loc="localhost:6379", mongohost="localhost",
        huge=False, directory="/tmp/ray", **kwargs):
        super().__init__(name, "store", **kwargs)
        logger.info("Initializing Mongo-Ray Storage Option")
        my_directory = Path(directory)
        if not my_directory.is_dir():
            os.mkdir(directory)
        
        self.funstore = Store(mongohost).create_lib("mray").get_store()["mray"]
        ray.init() # figure out how to initialize this in the beginning.
    
    def reset(self):
        logger.opt(ansi=True).info("<m>Mongo Ray Storage</m> Initialized")
    
    def add_task_parts(self, parts):
        pass

    def add(self, *args, **kwargs):
        if len(args) == 0:
            raise AttributeError("No objects supplied for serialization")
        ref = ray.put(list(args))

        name = kwargs.get("name", None)
        keyword = kwargs.get("keyword", None)
        sessoin_id = kwargs.get("session-id", None)
        if keyword is None or name is None or sessoin_id is None:
            raise AttributeError("Key object is missing. Include: name, keyword, sessoin_id")
        self.funstore.store({"type": "mray", "ref": ref, "timestamp": time.time(), "name": name, "keyword": keyword})
        
    def get(self, **kwargs):
        name = kwargs.get("name", None)
        keyword = kwargs.get("keyword", None)
        sessoin_id = kwargs.get("session-id", None)
        if keyword is None or name is None or sessoin_id is None:
            raise AttributeError("Key object is missing. Include: name, keyword, sessoin_id")
        genitem = self.funstore.query({"type": "mray", "name": name, "keyword": keyword})
        genitem = list(genitem)
        if len(genitem) == 0:
            logger.error("No items available")
            return {"data": {}}
        else:
            return_ids = []
            for _ in genitem:
                return_ids.append(_["ref"])
            r = ray.get(return_ids)
            return {
                "data": r
            }
        # return list(genitem)
    
    
        
