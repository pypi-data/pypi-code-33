import os
import vcf
from collections import defaultdict
from scipy import stats
from math import log10,ceil
from defaults import *

def reverseComp(seq):
    rev_seq = ""
    for s in seq:
        rev_seq = complements[s] + rev_seq
    return rev_seq

def create_dirs(dirlist):
    for dirname in dirlist:
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

class DetailMetrics(object):
    def __init__(self,metrics):
        self.metricsFile = metrics                
        if not os.path.isfile(self.metricsFile):
            raise IOError("No such file: %s"%self.metricsFile)
    @property
    def qscore(self):
        score = {}
        self.header = False
        with open(self.metricsFile) as met:    ### only one sampleAlias allowed
            for line in met:
                if not line.strip() or line.startswith("#"):
                    continue
                if not self.header:
                    self.header = line.strip().split("\t")
                    continue
                line = line.split()
                sampleAlias = line[0]
                transtion = line[2] + ">" + line[3]
                for i in range(5,9):
                    score.setdefault(transtion,defaultdict(float))[self.header[i]]+=float(line[i])
        for t,d in score.items():
            total = sum(d.values())
            s = d[self.header[6]]/total - d[self.header[8]]/total
            #score[t] = {"score":-10*log10(max(pow(10,-10),abs(s))),"raw":s}
            score[t] = {"score":-10*log10(max(pow(10,-10),s)),"raw":s}
        score["sampleAlias"] = sampleAlias
        return score

class FilterByOrientationBias(object):    
    def __init__(self,vcfFile,transition=list()):   ### do not include complete transition
        self._path = os.path.abspath(vcfFile)
        if not os.path.isfile(self._path):
            raise IOError("No such file: %s"%self.metricsFile)
        with open(self._path) as vf:
            myvcf = vcf.Reader(vf)
            self.cf_record = list(myvcf)
        self.transition = transition        
    def getTransVar(self):     
        transitionVar = {}
        for trans in self.transition:
            var = [OrderedDict(),OrderedDict()]
            ref,ALT = trans.split("/")
            for rec in self.cf_record:
                if not rec.is_snp:
                    continue
                if rec.REF == ref and rec.ALT[0].sequence == ALT:
                    var[0][rec.POS] = rec
                elif rec.REF == complements[ref] and rec.ALT[0].sequence == complements[ALT]:
                    var[1][rec.POS] = rec
            transitionVar[trans] = var
        return transitionVar
    @staticmethod
    def isRelevantArtifact(trans_type,ref="G",ALT="T"):
        if trans_type[0] == ref and trans_type[1] == ALT:
            return True
        return False
    @staticmethod
    def isRelevantArtifactComplement(trans_type,ref="G",ALT="T"):
        if trans_type[0] == complements[ref] and trans_type[1] == complements[ALT]:       
            return True
        return False
    @staticmethod
    def getOBAM(trans_type,transition):
        obam = ["false","false"]
        for trans in transition:
            ref,ALT = trans.split(">")
            if FilterByOrientationBias.isRelevantArtifact(trans_type,ref,ALT):
                obam[0] = "true"
            if FilterByOrientationBias.isRelevantArtifactComplement(trans_type,ref,ALT):
                obam[1] = "true"
        return obam
    @staticmethod
    def getFOBandPvalue(called,allele_index,ref="G",ALT="T"):
        gt_bases = called.gt_bases.split(called.gt_phase_char())
        try:            ###  GATK mutect2
            alt_F1R2 = list(called.data.F1R2)[1:]
            alt_F2R1 = list(called.data.F2R1)[1:]
        except AttributeError:   ###  setieon mutect2
            alt_F1R2 = [called.data.ALT_F1R2,] if isinstance(called.data.ALT_F1R2,int) else called.data.ALT_F1R2
            alt_F2R1 = [called.data.ALT_F2R1,] if isinstance(called.data.ALT_F2R1,int) else called.data.ALT_F2R1
        altdepth = called.data.AD[1:]
        i = allele_index - 1
        if gt_bases[0] == ref and gt_bases[allele_index] == ALT:
            fob = float(alt_F1R2[i])/(alt_F2R1[i] + alt_F1R2[i])   
        else:
            fob = float(alt_F2R1[i])/(alt_F2R1[i] + alt_F1R2[i])
        OBP = stats.binom(altdepth[i],BIAS_P).cdf(int(ceil(fob*altdepth[i])))  
        return fob,OBP 
