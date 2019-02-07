import requests, time,inspect, json
#import traceback, datetime
class A:
    def __init__(self):
        self.server = 'http://localhost:6006/dlp'
        self.problems = {}
        self.current = None
        self.params = None
        self.stop = False
        self.key = None
        self.running = False
        self.callb = None
        self.name = None
        self.keyExperiment = None
        self.stopEx = False
        self.expars = None
    def debug(self):
        self.name = None
    def setName(self, name, pars=None):
        #{'nr':1,'tag':datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), 'rtag':datetime.now()}
            #rtag -> hyperpar:value||[now] ,,, tag=[now]
        self.name=name
        
        if False and pars is not None:
            self.expars['tag'] = self.expars['tag']+"||"#+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.expars['rtag'] = self.expars['rtag']+"||"#+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.expars['range'] = self.expars['rtag']+"||"#+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
        self.expars = pars
    def trymakenew(self, frame):
        if self.running or self.name is None:
            return
        args, _, _, values = inspect.getargvalues(frame)
        self.makeExperiment(self.name, values)
    def trymakenewD(self, values):
        if self.running or self.name is None:
            return
        self.makeExperiment(self.name, values)
    def setProblem(self,n,p):
        self.problems[n] = p
        print('new problem added')
    def setKey(self,k):
        self.key = k
        print('new key added')
    def start(self):
        self.stop = False
        if self.key is None:
            print('no key')
            return
        process = Thread(target=self.callServer, args=[])
        process.start()
        while True:
            time.sleep(1)
    def sentEnd(self, status, mess):
        self.name = None
        if self.keyExperiment is None:
            print('no exp key')
            return
        res = requests.post(self.server, data={"action":'endJob','key':self.keyExperiment, 'status':status,
                                              'mess':mess})
        if res.ok:
            result = res.json()
    def callServer(self):
        while True:
            if self.stop:
                print('stoped')
                break
            if self.params is None:
                time.sleep(5)
                res = requests.post(self.server, data={"action":'ask','key':self.key})
                if res.ok:
                    result = res.json()
                    print(result)
                    if result['new']:       
                        self.stopEx = False
                        print('new problem starts')
                        print(result)
                        self.params = result['params']
                        self.current = result['current']
                        self.keyExperiment = result['key']
                    elif 'stop' in result and result['stop']:
                        self.stop = True
            else:
                self.running = True
                try:
                    self.problems[self.current](**self.params)
                    self.sentEnd('ended','')
                except Exception as e:
                    self.sentEnd('error',str(e))
                    print(e)
                    #print(traceback.format_exc())
                self.running = False
                self.params = None

    def sentInfo(self, p):
        if self.keyExperiment is None:
            print('no experiment key')
            return
        res = requests.post(self.server, json={"action":'addI','key':self.keyExperiment, 'info':p})
        if res.ok:
            result = res.json()
            if result['stop']:
                self.stopEx = True
                
    def makeExperiment(self, name, params):
        self.stopEx = False        
        if self.key is None:
            print('no key')
            return
        data = {"action":'addEx','name':name,'nrExperiment':1,
                                               'w':0,'status':'running','gran':json.dumps(None),
                                               'mid':self.key, 'params':json.dumps(params)}
        if self.expars is not None:
            data.update(self.expars)
            
        res = requests.post(self.server, data=data)
        self.expars = None
        print('make experiment')
        if res.ok:
            result = res.json()
            self.keyExperiment = result['id']
            print('got key experimnet', result['id'])
    def getParams(self):
        return self.params#json.dump(self.params)
    
    def convertParams(self, a, b):
        types = [int, float, str]
        for k in a:
            if typeof (a[k]) == "object":
                self.convert(a[k],b[k])
            elif typeof (a[k]) is list:
                tp = typeof (a[k][0])
                for i in range(len(b)):
                    b[i] = tp(b[i])
            else:
                tp = typeof (a[k])
                b[k] = tp(b[k])
                        
    def setServer(self,server):
        self.server= server
    def getP(self, f):
        s = inspect.getargspec(f)
        p = {}
        for i in s.args:
            #print(i)
            p[i] = None
        n = len(s.args)-1 if len(s.defaults)!=len(s.args) else 0
        for i in s.defaults:
            #print(i)
            p[s.args[n]] = i
            n = n-1 if len(s.defaults)!=len(s.args) else n+1
        return p
    
    def sentParams(self, f):
        p = self.getP(f)
        #print(p)
        self.initparams = p
        #return
        res = requests.post(self.server,json={"action":'addP','key':self.key, 'params':p})
        if res.ok:
            print('sent',p.keys())
    def setCallB(self, f):
        self.callb = f
    def monitor(self, func):
        def wrapper(*args, **kwargs):
            values = self.getP(func)
            s = inspect.getargspec(func)
            #print(args,s.args,kwargs, s.defaults)
            for i,k in enumerate(s.args): 
                if i>=len(args):continue
                values[k] = args[i]
            for k,v in  kwargs.items():
                values[k]=v
            print(values)
            self.trymakenewD(values)
            if self.callb is not None and 'callb' in kwargs:
                kwargs['callb'] = kwargs
            try:
                out = func(*args, **kwargs)
                self.sentEnd('ended','')
                return out
            except Exception as e:
                self.sentEnd('error',str(e))
                print(e)
                print(traceback.format_exc())
        return wrapper