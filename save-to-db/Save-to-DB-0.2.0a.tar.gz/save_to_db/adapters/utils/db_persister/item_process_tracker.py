from collections import defaultdict


class ItemProcessTracker(object):
    
    def __init__(self, item, adapter, adapter_settings):
        self.adapter = adapter
        self.adapter_settings = adapter_settings
        
        self.item = item
        self.models = []
        self.fkeys = defaultdict(list)
    


