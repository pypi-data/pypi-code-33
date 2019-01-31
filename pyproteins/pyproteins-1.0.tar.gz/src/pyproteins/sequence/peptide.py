#import customCollection

import pyproteins.utils.unixCmd
import pyproteins.sequence.msa
import pyproteins.sequence.psipred

import os

import json
import random
import re
import collections
import uuid
#from Bio.Blast import NCBIXML
from subprocess import call
from pyproteins.utils.miscellaneous import lFormat
from Bio import SeqIO

aminoAcidTable = {
    'A' : ['ALA'],
    'C' : ['CYS'],
    'D' : ['ASP'],
    'E' : ['GLU'],
    'F' : ['PHE'],
    'G' : ['GLY'],
    'H' : ['HIS'],
    'I' : ['ILE'],
    'K' : ['LYS'],
    'L' : ['LEU'],
    'M' : ['MET', 'MSE'],
    'N' : ['ASN'],
    'P' : ['PRO'],
    'Q' : ['GLN'],
    'R' : ['ARG'],
    'S' : ['SER'],
    'T' : ['THR'],
    'V' : ['VAL'],
    'W' : ['TRP', 'TRY'],
    'Y' : ['TYR'],
    'X' : ['UNK']
}

def threeToOne(aa):
    for l in aminoAcidTable:
        if aa in  aminoAcidTable[l]:
            return l;
    print("Warning 3 letter code", aa, "not found")
    return 'X';

def oneToThree(aa):
    if aa in aminoAcidTable:
        return aminoAcidTable[aa][0]
    print("Warning one letter code", aa, "not found")
    return 'UNK';

class EntrySet(object): #customCollection.EntrySet
    def __init__(self, name=None, dataFile=None):
        self.data = collections.OrderedDict()
        #customCollection.EntrySet.__init__(self, collectionPath="/Users/guillaumelaunay/work/data/peptides", constructor=Entry, typeCheck=isValidID, indexer=strip)
        if not dataFile and not name:
            print("flat file storage missing, Can't creating empty set w/out a name")
            return
        if name:
            self.name = name
            return
        self._parse(dataFile)


    def pluck(self):
        k = random.choice(self.data.keys())
        return self.data[k]

    def mash(self):
        m = hash(self.name + str(len(self)))
        return str(abs(m))

    def _parse(self, dataFile):
        f = open(dataFile, "r")
        dBuffer = json.load(f)
        self.name = dBuffer['id']

        for d in dBuffer['data']:
            e = Entry(datum=d)
            if hash(e) in self.data: # hash string more efficient
                print("Mutliple definition of petide fragment \"", d['seq'], "\"")
            self.data[hash(e)] = e

    def __len__(self):
        return len(self.data)
    def __repr__(self):
        string = "Peptide set \"" + self.name + "\" ("  + str(len(self)) + " elements)\n"
        for e in self:
            string += e.id + "\n"
        return string

    def enrich(self, _blankShotID=None, service="arwen", *kwargs):
        pass
        #global ppServ
        #if not ppServ:
        #    ppServ = startPpServ(service=service)
        #stash = [d for d in self if not d.ss2]
        #jobid = ppServ.push(peptidesList=stash, _blankShotID=_blankShotID)
        #data = ppServ.pull(jobid)

        #for i,d in enumerate(stash):
            #d.ss2Bind(ss2Obj=data[i])
         #   datum = ppServ.pull(jobid)
         #   d.ss2Bind(ss2Obj=datum)

    def __iter__(self):
        for k in self.data:
            yield self.data[k]

    def __getitem__(self, k):
        for x in self.data:
            if self.data[x].id == k:
                return self.data[x]
        return None

    def index(self, string=None, peptideObject=None):
        if string:
            try:
                return [ e.id for e in self.data.values() ].index(string)
            except ValueError:
                return None
        if peptideObject:
            return [ e.id for e in self.data.values() ].index(peptideObject.id)


    def get(self, peptideObject):
        k = hash(peptideObject)
        if k in self.data:
            return self.data[k]
        return None

    def add(self, peptideObject):
        if self.delete(peptideObject):
            print("Following peptide already part of the set")
            print(peptideObject)
        self.data[hash(peptideObject)] = peptideObject

    def delete(self, peptideObject):
        k = hash(peptideObject)
        if k in self.data:
            del self.data[k]
            return True
        return False

    def serialize(self, targetFile=None, comments="peptide collection"):
        dataOut = {'id' : self.name, 'comments' : comments, 'data' : [ e.dict for e in self ]}
        asJson =  json.JSONEncoder().encode(dataOut)
        if targetFile:
            with open(targetFile, "w") as f:
                f.write(asJson)
        return asJson

    # Create a list of blast
    #
#blastBean : {
#    'env' : 'sge', 'slurm', 'local'[DEFAULT]
#    'blastDb' : REQUIRED
#    'BLASTDBROOT' : REQUIRED
#    'rootDir' : oc.getcwd() [DEFAULT]
#}
#

    def blastAll(self, blastBean, blastXmlOnly=False):
        pass


    @property # return list of peptides name
    def labels(self):
        return [ e.id for e in self ]




class Entry(object):

    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)

    def parse(self, fastaFile):
        handle = open(fastaFile, "rU")
        records = list(SeqIO.parse(handle, "fasta"))
        handle.close()
        self.id = records[0].id  #first record
        self.seq = str(records[0].seq)  #first record


    def __eq__(self, other):
        return self.seq == other.seq
            
    def __hash__(self):
        if not self.seed:
            random.seed()
            #self.seed = os.urandom(5)
            self.seed = random.randint(1,1000000)
        return hash(self.seq + str(self.seed))

    @property
    def tag(self):
        tag = re.sub('[\s]+','_', self.id)
        return tag

    def fastaWrite(self, path="./", fileName='default'):
        path = re.sub('[/]+$', '', path)
        fName = path + '/' + str(fileName) + '.fasta'
        with open (fName, 'w') as fOut:
                fOut.write(self.fasta)

    
        #print 'peptide \'' + self.id + '\' fasta wrote to file ' + fName


    def mash(self):
        m = hash(self)
        return str(abs(m))

    def serialize(self):
        return json.JSONEncoder().encode(self.dict) # Check that function name does not create None attribute
        pass # write json formated data structure call be customCollection

    def __init__(self, datum=None, **kwargs):
        self.description = None
        self.ss2Obj = None
        self.ss2Seq = None
        self.seq = None
        self.id = None
        self.seed = None # we need a random generator, bc sequence could be identical

        if datum:
            if 'id' not in datum or 'seq' not in datum:
                raise ValueError("Attribute missing for peptide definition")
            self.id = datum['id']
            self.seq = datum['seq']
            self.description = datum['desc']
            #if 'ss2' in datum:
            #    self.ss2Obj = pyproteins.services.psipredServ.collection(stream=datum['ss2'])
        else:
            if 'id' in kwargs:
                self.id = kwargs['id']
            if 'seq' in kwargs:
                self.seq = kwargs['seq']
            if 'desc' in kwargs:
                self.description = kwargs['desc']


       #     if 'ss2' in kwargs:
       #         self.ss2 = kwargs['ss2']

        #if not self.seq or not self.id:
        #    raise ValueError("Cant create peptide object")


    def __iter__(self):
        for i in range (0, len(self.seq)):
            yield self[i + 1]

    def __getitem__(self, i):
        if i < 0:
            raise ValueError("minimal amino-acid number is 1")
        v = {'aa' : self.seq[i], 'ss2' : None, 'burial' : None }
        if self.ss2:
            v['ss2'] = self.ss2[i]
        return pyproteins.sequence.msa.Position(v)

    @property
    def hasSse(self):
        if self.ss2:
            return True
        return False

    def __len__(self):
        return len(self.seq)

    def __repr__(self):
        s = self.fasta
        if self.ss2Obj:
            s += "\n" + self.ss2Obj.horiz
        return s
    @property
    def dict(self):
        ss2 = None
        if self.ss2Obj:
            ss2 = self.ss2Obj.dict
        return {
            'id' : self.id,
            'seq' : self.seq,
            'desc' : self.description,
            'ss2' : ss2
        }

    def ss2Bind(self, **kwargs):
       raise ValueError("NO SS2BIND")
       # ss2Obj = None
       # if 'ss2Obj' in kwargs:
       #     ss2Obj = kwargs['ss2Obj']
       # elif 'file' in kwargs:
       #     ss2Obj = pyproteins.utils.psipredServ.collection(fileName=kwargs['file'])

        #if ss2Obj.aaSeq != self.aaSeq:
        #    raise ValueError("amino-acid sequence dont match\nss2Obj_aaSeq : \"" + ss2Obj.aaSeq + "\"\n not equal to \npeptide_aaSeq : \"" + self.aaSeq + "\"")
        #self.ss2Obj = ss2Obj

    @property
    def aaSeq(self):
        return self.seq.upper()

    @property
    def fasta(self):
        add = ''
        if self.description:
            add = self.description
        return ">" + self.id + add + "\n" + lFormat(self.aaSeq)

    @property
    def ss2(self):
        if self.ss2Obj:
            return self.ss2Obj.horiz
        if self.ss2Seq:
            return self.ss2Seq
        return None
        #else:
        #    tmp = ppServ.push(peptidesList=[self])
        #    return tmp

    @property # try to extract pfam id
    def pfamID(self):
        m = re.search("(PF[\d]+)", self.id)
        if m:
            return m.groups(1)[0]
        return None

''' MUST REWRITE USING ETREE in dedicated parser
    def blast(self, xmlPsiBlastOutput=None, xmlPsiBlastStream=None, strict=False): # return an msa Object

        def hit_check(hit):
            for i in range(0, len(hit.hsps) - 1):
                for j in range(i + 1, len(hit.hsps)):
                    if hit.hsps[i].sbjct_start >= hit.hsps[j].sbjct_start:
                        if hit.hsps[i].sbjct_end <= hit.hsps[j].sbjct_end:
                            errorString =  "hsp  " + str(i) + " / " + str(j) + "overlap error in hit named " + hit.title + "\n"
                            errorString += str(hit.hsps[i].sbjct_start) + ',' + str(hit.hsps[i].sbjct_end) + ") vs (" + str(hit.hsps[j].sbjct_start) + ',' + str(hit.hsps[j].sbjct_end) + ')'
                            #raise ValueError( errorString)
                            print("Warning : " + errorString)

        def HspOverlap(mem, x):
            for y in mem:
                if (x[0] >= y[0] and  x[0] <= y[1]) : return True
                if (x[1] >= y[0] and  x[1] <= y[1]) : return True
            return False

        def hsp_merge(hsp, array):

            pos = hsp.query_start - 1
            for i in range(0, hsp.align_length):
                if hsp.query[i] == '-':
                    continue
                array[pos] = hsp.sbjct[i]
                pos += 1
            #return ''.join(mergedStrand)


        array=[{ 'id' : self.id,  'seq' : list(self.aaSeq) }]

        if not unixCmd.which("blastpgp"):
            raise initError("Cant find blastpgp executable")

        if not xmlPsiBlastOutput and not xmlPsiBlastStream:
            rootId = uuid.uuid4()
            self.fastaWrite(name=rootId)

            call(['blastpgp', '-j', '2', '-i', str(rootId) + '.fasta', '-d', 'nr70', '-m', '7', '-o', str(rootId) + '.xml'])
            f = open(str(rootId) + '.xml')
            records = NCBIXML.parse(f)
        else :
            if xmlPsiBlastOutput :
                f = open(xmlPsiBlastOutput)
            else:
                f = xmlPsiBlastStream
            records = NCBIXML.parse(f)

        recordList = [x for x in records]
        for psiPass in reversed(recordList):
            if not psiPass.alignments:
                continue
            for hit in psiPass.alignments:
                if len(hit.hsps) > 1:
                    if strict:
                        hit_check(hit)
                if hit.hsps[0].sbjct == self.aaSeq:
                    #print "Self hit, skipping"
                    continue
                title = str(hit.title) + '[' + ','.join([ str(hsp.sbjct_start) + '-' + str(hsp.sbjct_end) for hsp in hit.hsps ]) + ']'
                datum = { 'id' : title,  'seq' : ['-'] * len(self) }
                mem = []
                for hsp in hit.hsps:
                    if HspOverlap(mem, (hsp.sbjct_start,hsp.sbjct_end)):
                        if strict:
                            raise ValueError('hsp overlap error')
                        continue
                    mem.append((hsp.sbjct_start,hsp.sbjct_end))
                    hsp_merge(hsp, datum['seq'])
                array.append(datum)
            break

        f.close()
        #return [[ hit['seq'] for hit in array ], [ hit['id'] for hit in array ]]
        msaBean = pyproteins.sequence.msa.MsaBean([ hit['seq'] for hit in array ], [ hit['id'] for hit in array ])
        msa = pyproteins.sequence.msa.Msa(msaBean=msaBean)
        msa.set_id(self.id)
        #return msaBean
        return msa
'''