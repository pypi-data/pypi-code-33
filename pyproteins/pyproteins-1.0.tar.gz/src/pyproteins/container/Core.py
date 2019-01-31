import urllib.request
import urllib.error
import json
from bs4 import BeautifulSoup
from hashlib import md5
import copy
proxyHttp = None
import json

def proxySetting(http=None, https=None):
    if http:
        global proxyHttp
        proxyHttp = http
        print ("!!Proxy set to " + str(proxyHttp))



class Container(object):
    def __init__(self, id, url=None, fileName=None):
        if not id:
            raise ValueError("identifier is empty")
        self.id = id
        self.rawData = None
        self.url = url
        self.fileName = fileName

    def getXmlHandler(self):
        if not self.fileName:
            print ('got to fetch ' + self.id)
        self.rawData = self._fetch() if not self.fileName else self._readFile()
        if not self.rawData:
            raise ValueError("Error, empty xmlHandler")
            
        xmlH = BeautifulSoup(self.rawData, 'xml')
        return xmlH

    def _readFile(self):
        with open (self.fileName, "r") as f:
            rawData = f.read()
        return rawData

    def _fetch(self):
        global proxyHttp
        #print ("Trying to DL " + self.url)
        try:
            if proxyHttp:
                #proxy = urllib2.ProxyHandler({'http': proxyHttp})
                proxy_support = urllib.request.ProxyHandler(proxyHttp)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                con = urllib.request.urlopen(self.url)
               # soup = BeautifulSoup(''.join(website))
            else:
                #print 'using no proxy'
                #p2.7
                #req = urllib2.Request(self.url, headers={'User-Agent' : "Magic Browser"})
                #con = urlopen( req )
                con = urllib.request.urlopen(self.url)
            rawData =  con.read()
            #response = urllib2.urlopen(self.url)

        except urllib.error.HTTPError as error:
            print ("Error at " + self.url)
            print ("HTTP ERROR " + str(error.code))
            print (error.fp.read())
            return None
        except urllib.error.URLError as error:
            print (self.url)
            print (error.reason)
            return None
        #rawData = response.read()
        #response.close()
        return rawData

    def serialize (self):
        return self.rawData

    @property
    def raw(self):
        if not self.rawData:
            self.rawData = self._fetch() if not self.fileName else self._readFile()
        return self.rawData

'''
class mdTreeEncoder(json.JSONEncoder): # DOESNOT WORK stringifed twice (by encoder too)
    def default(self, mdTreeInstance):
        if isinstance(mdTreeInstance, mdTree):
            d = {}
            for x,y,lv in mdTreeInstance:
                if not x in d:
                    d[x] = {}
                if not y in d[x]:
                    d[x][y] = None
                    try:
                        d[x][y] = [ str(e) for e in lv ]
                    except TypeError:
                        d[x][y] = str(lv)
                   
                return d
        # Error
        return json.JSONEncoder.default(self, mdTreeInstance)
'''


'''
    def jsonString(self, leaveJsonifyer=None):
        uBuff = []
        #print(leaveJsonifyer)
        for x in self.data:
            buf = []
            for y in self.data[x]:
                lv = self.data[x][y]
                ls = '00'
                try:
                    ls = '[' + ','.join( [ '"' + json.dumps(e) + '"' if leaveJsonifyer is None else '"' + leaveJsonifyer(e) + '"' for e in lv ] ) + ']'
                except TypeError:
                    print("Non iterable")
                    ls = json.dumps(lv) if leaveJsonifyer is None else leaveJsonifyer(lv)
                
                buf.append('"' + str(y) + '" : ' + ls)
            uBuff.append( '"'  + str(x) + '" : {' + ",".join(buf) + "}" )
        return  '{"mdTree" : { ' + ','.join(uBuff) + '}}'

'''


## md5 hashed tree
## Semi matrix representation as a 
## Two lvl tree, top/down key are min/max md5 hash
class mdTree:
    def __init__(self, append=True):

        self.autoAppendable = append

       # print(self.autoAppendable)

        self.data = {}
    
    def __len__(self): # total number of terminal leaves == non-empty matrix cells
        c = 0
        for k1 in self.data:
            for k2 in self.data[k1]:
                c+=1
        return c

    def keys(self): # Returns all primary and secondary keys
        return set ( list(self.data.keys()) + [ k for k in self.data for _k in self.data[k] ] )

    def _digest(self, k1, k2):
        _k1 = md5(k1.encode('utf-8')).hexdigest()
        _k2 = md5(k2.encode('utf-8')).hexdigest()
        x = k1 if _k1 < _k2 else k2 
        y = k2 if _k1 < _k2 else k1 
        return x,y

    def append (self, k1, k2, datum):# appendig
        if not self.autoAppendable:
            raise TypeError("Cant append to custom leave")

        x, y = self._digest(k1, k2)
        self._push(x,y, datum)

    def get (self, k1, k2): # Mutable ref returned
        x, y = self._digest(k1, k2)
        if x not in self.data:
            return None
        if y not in self.data[x]:
            return None
        return self.data[x][y]
    
    def getOrSet (self, k1, k2, value): # Mutable ref returned
        x, y = self._digest(k1, k2)
        el = self._getMaySet(x, y, value)
        return el

    def _getMaySet(self, x, y, value): # Initailise leave to value if not created already
        if x not in self.data:
            self.data[x] = {}
        if y not in self.data[x]:
            self.data[x][y] = value
        return self.data[x][y]


    def _testRef(self, x, y):
        if x not in self.data:
            return False
        if y not in self.data[x]:
            return False
        return True
    
   
        
    def _push(self, x, y, datum):
        buf = self._getMaySet(x, y, [])
        buf.append(datum)

# We unroll to copy ref of collection elements not of collection itself
# to avoid collection mutability
    def __getitem__(self, k1):
        data = {}
        if k1 in self.data:
            #data[k1] = {}
            for subk1 in self.data[k1]:
                if self.autoAppendable:
                    data[subk1] = [ e for e in self.data[k1][subk1] ]
                else:
                    data[subk1] = self.data[k1][subk1]
        
        _k1 = md5(k1.encode('utf-8')).hexdigest()
        
        
        for k2 in self.data:
            if _k1 < md5(k2.encode('utf-8')).hexdigest():
                continue
            if k1 in self.data[k2]:
                if self.autoAppendable:
                    data[k2] = [ e for e in self.data[k2][k1] ]
                else:
                    data[k2] = self.data[k2][k1]

        return data

    def __iter__(self):
        for k1 in self.data:
            for k2 in self.data[k1]:
                yield(k1, k2, self.data[k1][k2])

    def dnCopy(self):
        other = dnTree()
        other.data = copy.deepcopy(self.data)
        return other


    def __repr__(self):
        return str(self.data)

## dEnSE Tree
## Minimal number of top level leaves tree
## Wrapper to md5 tree with dynamic access to content
##
class dnTree(mdTree):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.weights = {}
        self._rank = None

    def append(self, k1, k2, datum):
        super(dnTree, self).append(k1, k2, datum)
        for x in (k1, k2):
            if x not in self.weights:
                self.weights[x] = 0
            self.weights[x] += 1
        self._rank = None

    def __getitem__(self, k1):
        #print("allKeys: " + str(super().__getitem__(k1)))
        #print(self.rank)
        return { k2: v for k2,v in super().__getitem__(k1).items() if self.rank[k1] < self.rank[k2] }
    
    # Get All elements connected to k1, w/ weight consideration
    def getNonDense(self, k1):
        try :
            d = super().__getitem__(k1)
            return d
        except KeyError:
            return None
        
    @property 
    def rank(self): # sorting key by number of insertion, and convert into non redundatn rank numbers
        #self._rank = None
        if not self._rank:   
            _rank = sorted(self.weights.keys(), key= lambda k :  self.weights[k], reverse=True)
            #print("RK::", str(_rank))
            self._rank = { k : rk  for rk, k in enumerate(_rank) }
        #print ("-->", self._rank)
        return self._rank

    def __repr__(self):
        d = {}
        for k in super().keys():
            _d = self[k]
            if _d:
                d[k] = _d
        
        return str(d)
