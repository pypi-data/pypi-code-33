import requests
import json

# API = "https://studiobitonti.appspot.com"
API = "http://35.185.18.247:3000"


class meshRepair_v2:
    def __init__(self,token): #set global variables
        """
        Initialize
        """
        self.url = "%s/meshRepair_v2" % API
        self.t = token
        self.input = ''
        self.output = ''

    def setInput(self,_input):
        self.input = _input

    def setOutput(self,output):
        self.output = output
    
    def auto_repair(self):
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/auto_repair',payload)
    
    def detect_edges(self, return_index = False):
        payload = {"input":self.input,"return_index":return_index,"t":self.t}
        return send(self.url+'/detect_edges',payload)

    def fill_holes(self, iteration = 1):
        payload = {"input":self.input,"output":self.output,"iteration":iteration,"t":self.t}
        return send(self.url+'/fill_holes',payload)

    def filter_triangles(self, naked, nonManifold):
        payload = {"input":self.input,"output":self.output,"naked":naked,"nonManifold":nonManifold,"t":self.t}
        return send(self.url+'/filter_triangles',payload)

    def unify_mesh_normals(self):
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/unify_mesh_normals',payload)

    def detect_overlap_faces(self):
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/detect_overlap_faces',payload)

    def detect_separate_shells(self):
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/detect_separate_shells',payload)

    def round_up_vertices(self,digits):
        payload = {"input":self.input,"output":self.output,"digits":digits,"t":self.t}
        return send(self.url+'/round_up_vertices',payload)

    def delete_degenerated_faces(self):
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/delete_degenerated_faces',payload)


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

def send(url,payload,printPayload = True,printResult = False):

    payload = {k: v for k, v in payload.items() if v!= ''} # clean None inputs
    if printPayload:
        print('request: ',json.dumps(payload))
    r = requests.post(url,json=payload)
    return parseResponse(r,printResult)