import somajo, os
from smart_open import smart_open
#Kann mit vielen unterschiedlichen Dateitypen umgehen. Komprimierte Archive bis html dateien
#One-Sentence-Per-Line-Opener
class OSLOpen:
    #Resultat ähnlich dem von somajo auf ganzem Text, aber langsamer
    def __init__(self,path,list_output=False):
        self.lo=list_output
        self.path=path
        #if not os.path.isfile(self.path):
        #    raise Exception("File does not exist!")
        self.tokenizer=somajo.Tokenizer()
        self.ssplitter=somajo.SentenceSplitter()
        self.sentences=[]
        self.words=[]
    def __iter__(self):
        self.file=smart_open(self.path)
        return self
        
    def __next__(self):
        if len(self.sentences)>0:
            if self.lo:
                return self.sentences.pop(0)
            return " ".join(self.sentences.pop(0))
        nextline=self.file.readline().decode()
        if len(self.sentences)==1 and nextline=="":
            return self.sentences.pop(0)
        if len(self.sentences)==0 and nextline=="" and len(self.words)>0:
            self.sentences.append(self.words)
            self.words=[]
            return self.__next__()
        if len(self.sentences)==0 and nextline=="":
            raise StopIteration
        self.words+=self.tokenizer.tokenize(nextline)
        sentences=self.ssplitter.split(self.words)
        if len(sentences)>1:
            self.words=sentences.pop() #entfernt den mglw. unvollständigen Satz wieder
            self.sentences=sentences
            if self.lo:
                return self.sentences.pop(0)
            return " ".join(self.sentences.pop(0))
        return self.__next__()
