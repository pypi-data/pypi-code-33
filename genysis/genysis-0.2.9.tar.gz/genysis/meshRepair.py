import requests
import json

API = "https://studiobitonti.appspot.com"

class meshRepair:
    def __init__(self,token): #set global variables
        """
        Initialize
        """
        self.url = "%s/meshRepair" % API
        self.t = token
        self.input = ''
        self.output = ''

    def setInput(self,_input):
        self.input = _input
    
    def setOutput(self,output):
        self.output = output
    
    def detectEdges(self):
        payload = {"input":self.input,"t":self.t}
        return send(self.url+'/detectEdges',payload)
    
    def fillHoles(self, iteration = 1):
        payload = {"input":self.input,"output":self.output,"iteration": iteration,"t":self.t}
        return send(self.url+'/fillHoles',payload)

    def unifyNormals(self):
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/unifyNormals',payload)

    def alignVertices(self, tolerance):
        payload = {"input":self.input,"output":self.output,"tolerance": tolerance,"t":self.t}
        return send(self.url+'/alignVertices',payload)

    def mergeVertices(self):
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/mergeVertices',payload)

    def removeDupFaces(self):
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/removeDupFaces',payload)

    def removeFloatingTriangles(self):
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/removeFloatingTriangles',payload)

    def removeBadTriangles(self,tolerance):
        payload = {"input":self.input,"output":self.output,"tolerance": tolerance,"t":self.t}
        return send(self.url+'/removeBadTriangles',payload)

    def detectShells(self):
        payload = {"input":self.input,"output":"placeholder","t":self.t}
        return send(self.url+'/detectShells',payload)

    def smooth(self, iteration = 1):
        payload = {"input":self.input,"output":self.output,"iteration": iteration,"t":self.t}
        return send(self.url+'/smooth',payload)


def parseResponse(r,printResult = True, parseJSON = True):
    if r.status_code == 200:
        if printResult:
            print('response: ',r.text)
        if parseJSON:
            return json.loads(r.text)
        else: 
            return
    else:
        raise RuntimeError(r.text)

def send(url,payload,printPayload = True,printResult = True):

    payload = {k: v for k, v in payload.items() if v!= ''} # clean None inputs
    if printPayload:
        print('request: ',json.dumps(payload))
    r = requests.post(url,json=payload)
    return parseResponse(r,printResult)