import os

class ScriptEntry(object):
    
    def __init__(self, src=" ", type=None, priority=9999):
        
        if src == None: 
            src= ""
        self.filename = os.path.basename(src)
        self.src = src
        self.type = type
        self.priority = priority
    
    def html(self):
        return self.__str__()
        
    def __unicode__(self):
        return self.str()
        
        
    def __repr__(self):
        tmplstr=  """ScriptEntry(src="{}", type=="{}", priority={}")"""
        return tmplstr.format(self.src, self.type, self.priority)
    
    def __str__(self):
        
        return """<script type="{}" src="{}"></script>""".format(self.type, self.src)
    
  
    
    def __lt__(self, other):
        result=  int(self.priority) < int(other.priority)
        return result
    def __eq__(self, other):
        return int(self.priority) ==  int(other.priority)
        
    def __gt__(self, other):
        return  int(self.priority) >  int(other.priority)
    

class ScriptRegistry(object):
    
    def __init__(self):
        self.index_by_name = {}
        self._entry_as_list = []

    def register(self, src=None, type="text/javascript", priority=9999):
            
        script_entry = ScriptEntry(src=src, type=type, priority=priority)    
        
        if script_entry.filename in self.index_by_name:
            print("Warning overwriting script with: {}".format(src))
            
        self.index_by_name.update({ script_entry.filename : script_entry})
    
    
    
    def as_list(self):
        
        if len(self._entry_as_list) != len(self.index_by_name):
            self._entry_as_list = [] 
            for key in self.index_by_name.keys():
                self._entry_as_list.append(self.index_by_name.get(key))
            
        print("unsorted: {}".format(self._entry_as_list))
        print("sorted: {}".format(sorted(self._entry_as_list)))
        return sorted(self._entry_as_list)
    
    def __iter__(self):
        self.__i = 0                #  iterable current item 
        return iter(self.as_list())

    def __next__(self):
        if self.__i<len(self.as_list())-1:
            self.__i += 1         
            return self._entry_as_list[self.__i]
        else:
            raise StopIteration
       
       
    def html(self):
        
        out = ""
        for entry in self.as_list():
            out = out + "\n" + str(entry)
            
        return out
        
        
registry = ScriptRegistry()


    
    
        
    
    
