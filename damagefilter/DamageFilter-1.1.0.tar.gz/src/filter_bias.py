#!/usr/bin/env python
#coding:utf-8

import os        
import vcf
from collections import defaultdict,OrderedDict
from math import exp,log10,ceil
from scipy import stats
from compiler.ast import flatten

from defaults import *
from utils import DetailMetrics,FilterByOrientationBias


def main():   
    args = parserArg()
    premetricsfile = args.detailfile
    vcfile = args.vcfile
    outvcf = args.output
    transmode = args.artifactmodes   
    formatdict = OrderedDict()  
    formatdict["OBAM"] = dict(id='OBAM', num=-1, type='String', desc='Whether the variant can be one of the given REF/ALT artifact modes.')
    formatdict["OBAMRC"] = dict(id='OBAMRC', num=-1, type='String', desc='Whether the variant can be one of the given REF/ALT artifact mode complements.')
    formatdict["OBF"] = dict(id='OBF', num=-1, type='Float', desc='Fraction of ALT reads indicating orientation bias error (taking into account artifact mode complement).')
    formatdict["OBP"] = dict(id='OBP', num=-1, type='Float', desc='Orientation bias p value for the given REF/ALT artifact or its complement.')
    formatdict["OBQ"] = dict(id='OBQ', num=-1, type='Float', desc='Measure (across entire bam file) of orientation bias for a given REF/ALT error.')
    formatdict["OBQRC"] = dict(id='OBQRC', num=-1, type='Float', desc='Measure (across entire bam file) of orientation bias for the complement of a given REF/ALT error.')   
    
    artifactQscore = DetailMetrics(premetricsfile).qscore
    print artifactQscore
    artifactVcf = FilterByOrientationBias(vcfile,transmode)
    transition = [">".join(m.split("/")) for m in transmode]
    transition_rev = [">".join([complements[i] for i in m.split("/")]) for m in transmode]
    vcfin = open(vcfile)
    vcfout = open(outvcf,"w")
    myvcf = vcf.Reader(vcfin)    
    for tag,f in formatdict.items():
        if tag in myvcf.formats:
            continue
        formatHeader = vcf.parser._Format(id=f["id"], num=f["num"], type=f["type"], desc=f["desc"])
        myvcf.formats[tag] = formatHeader
    filterHeader = vcf.parser._Filter(id='orientation_bias', desc='Orientation bias (in one of the specified artifact mode(s) or complement) seen in one or more samples.')
    myvcf.filters['orientation_bias'] = filterHeader
    myvcf.metadata["orientation_bias_artifact_modes"] = [OrderedDict([('ID', "|".join(transmode)), ('Description', '"The artifact modes that were used for orientation bias artifact filtering for this VCF"')])]
    
    cf_writer = vcf.Writer(vcfout, myvcf)
    totalOrientationBiasCount = defaultdict(lambda :defaultdict(int))
    artifactrecord = defaultdict(dict)
    new_record = []
    for ln,rec in enumerate(artifactVcf.cf_record):
        FORMAT = []
        for snCall in rec.samples:           
            if (not snCall.is_variant) or (not rec.is_snp):  # 0/0 or not a snv
                FORMAT.append(rec.FORMAT + ":" + ":".join(['OBAM', 'OBAMRC']))
                nd = vcf.parser.make_calldata_tuple(list(snCall.data._fields) + ['OBAM', 'OBAMRC'])
                nd = nd._make(snCall.data + ("flase","flase"))  
            else:
                FORMAT.append(rec.FORMAT + ":" + ":".join(formatdict.keys()))
                nd = vcf.parser.make_calldata_tuple(list(snCall.data._fields) + formatdict.keys())                
                alleles = [int(i) for i in snCall.gt_alleles]
                gt_bases = snCall.gt_bases.split(snCall.gt_phase_char())
                # trans_type_list = [gt_bases[0] + ">" +gt_bases[i] for i in range(1,len(alleles))]
                # trans_type_rev_list = [complements[gt_bases[0]] + ">" + complements[gt_bases[i]] for i in range(1,len(alleles))]
                calldata = list(snCall.data)
                obam_tag = []
                obamrc_tag = []
                fob = []
                pvalue = []
                obq = []
                obq_rc = []
                for i in range(1,len(alleles)):   ## 0/1, 0/1/2, ...
                    trans_type = gt_bases[0] + ">" +gt_bases[i]
                    trans_type_rev = complements[gt_bases[0]] + ">" + complements[gt_bases[i]]
                    if trans_type in transition or trans_type_rev in transition:   
                        trans = trans_type if trans_type in transition else trans_type_rev
                        totalOrientationBiasCount[snCall.sample][trans_type] += 1 
                        obam = FilterByOrientationBias.getOBAM([gt_bases[0],gt_bases[i]],transition)
                        fobP = FilterByOrientationBias.getFOBandPvalue(snCall,i,*trans.split(">"))
                        fob.append(fobP[0])
                        pvalue.append(fobP[1])
                        obam_tag.append(obam[0])
                        obamrc_tag.append(obam[1])
                        artifactrecord[trans_type][ln] = {"FOB":fobP[0],"PVALUE":fobP[1],"rec":rec}
                    else:
                        obam_tag.append("false")
                        obamrc_tag.append("false")
                        fob.append(None)
                        pvalue.append(None)
                    obq.append(artifactQscore[trans_type])
                    obq_rc.append(artifactQscore[trans_type_rev])
                nd = nd._make(calldata + [obam_tag,obamrc_tag,fob,pvalue,obq,obq_rc])
            snCall.data = nd
        rec.FORMAT = sorted(FORMAT,key=len)[-1]
        new_record.append(rec)        
    vcfin.close()    
    artifactPOS = dict.fromkeys(artifactrecord.keys(),[])
    for t in artifactrecord:        
        trans = t if t in transition else ">".join([complements[i] for i in t.split(">")])
        v = sorted(artifactrecord[t].items(),key=lambda x:x[1]["PVALUE"],reverse=True)
        pvalue = [i[1]["PVALUE"] for i in v]
        pre_cut_num = len(pvalue) - 1
        for p in range(len(pvalue)):
            if pvalue[p] < fdrThreshold*(p+1)/len(pvalue):
                pre_cut_num = p
                break
        suppression = 1/(1+exp(BIASQP2*(artifactQscore[trans]-BIASQP1)))
        post_cut_num = int(round(pre_cut_num*suppression))
        artifactPOS[t] = [i[0] for i in v[:post_cut_num]]
        print t,dict(total=len(pvalue),pre_cut_num=pre_cut_num,post_cut_num=post_cut_num) 
    filterPos = flatten(artifactPOS.values())
    for ln,rec in enumerate(new_record):
        if ln in filterPos:
            rec.add_filter("orientation_bias")
        cf_writer.write_record(rec)    
    vcfout.close()
   
def run_filter_bias(args):   
    premetricsfile = args.metrics
    vcfile = args.vcfile
    outvcf =os.path.join(args.outdir,args.name)
    transmode = args.type
    formatdict = OrderedDict()  
    formatdict["OBAM"] = dict(id='OBAM', num=-1, type='String', desc='Whether the variant can be one of the given REF/ALT artifact modes.')
    formatdict["OBAMRC"] = dict(id='OBAMRC', num=-1, type='String', desc='Whether the variant can be one of the given REF/ALT artifact mode complements.')
    formatdict["OBF"] = dict(id='OBF', num=-1, type='Float', desc='Fraction of ALT reads indicating orientation bias error (taking into account artifact mode complement).')
    formatdict["OBP"] = dict(id='OBP', num=-1, type='Float', desc='Orientation bias p value for the given REF/ALT artifact or its complement.')
    formatdict["OBQ"] = dict(id='OBQ', num=-1, type='Float', desc='Measure (across entire bam file) of orientation bias for a given REF/ALT error.')
    formatdict["OBQRC"] = dict(id='OBQRC', num=-1, type='Float', desc='Measure (across entire bam file) of orientation bias for the complement of a given REF/ALT error.')   
    
    artifactQscore = DetailMetrics(premetricsfile).qscore
    print artifactQscore
    artifactVcf = FilterByOrientationBias(vcfile,transmode)
    transition = [">".join(m.split("/")) for m in transmode]
    transition_rev = [">".join([complements[i] for i in m.split("/")]) for m in transmode]
    vcfin = open(vcfile)
    vcfout = open(outvcf,"w")
    myvcf = vcf.Reader(vcfin)    
    for tag,f in formatdict.items():
        if tag in myvcf.formats:
            continue
        formatHeader = vcf.parser._Format(id=f["id"], num=f["num"], type=f["type"], desc=f["desc"])
        myvcf.formats[tag] = formatHeader
    filterHeader = vcf.parser._Filter(id='orientation_bias', desc='Orientation bias (in one of the specified artifact mode(s) or complement) seen in one or more samples.')
    myvcf.filters['orientation_bias'] = filterHeader
    myvcf.metadata["orientation_bias_artifact_modes"] = [OrderedDict([('ID', "|".join(transmode)), ('Description', '"The artifact modes that were used for orientation bias artifact filtering for this VCF"')])]
    
    cf_writer = vcf.Writer(vcfout, myvcf)
    totalOrientationBiasCount = defaultdict(lambda :defaultdict(int))
    artifactrecord = defaultdict(dict)
    new_record = []
    for ln,rec in enumerate(artifactVcf.cf_record):
        FORMAT = []
        for snCall in rec.samples:           
            if (not snCall.is_variant) or (not rec.is_snp):  # 0/0, not a snv
                FORMAT.append(rec.FORMAT + ":" + ":".join(['OBAM', 'OBAMRC']))
                nd = vcf.parser.make_calldata_tuple(list(snCall.data._fields) + ['OBAM', 'OBAMRC'])
                nd = nd._make(snCall.data + ("flase","flase"))  
            else:
                FORMAT.append(rec.FORMAT + ":" + ":".join(formatdict.keys()))
                nd = vcf.parser.make_calldata_tuple(list(snCall.data._fields) + formatdict.keys())                
                alleles = [int(i) for i in snCall.gt_alleles]
                gt_bases = snCall.gt_bases.split(snCall.gt_phase_char())
                # trans_type_list = [gt_bases[0] + ">" +gt_bases[i] for i in range(1,len(alleles))]
                # trans_type_rev_list = [complements[gt_bases[0]] + ">" + complements[gt_bases[i]] for i in range(1,len(alleles))]
                calldata = list(snCall.data)
                obam_tag = []
                obamrc_tag = []
                fob = []
                pvalue = []
                obq = []
                obq_rc = []
                for i in range(1,len(alleles)):   ## 0/1, 0/1/2
                    trans_type = gt_bases[0] + ">" +gt_bases[i]
                    trans_type_rev = complements[gt_bases[0]] + ">" + complements[gt_bases[i]]
                    if trans_type in transition or trans_type_rev in transition:   
                        # trans = trans_type if trans_type in transition else trans_type_rev
                        totalOrientationBiasCount[snCall.sample][trans_type] += 1 
                        obam = FilterByOrientationBias.getOBAM([gt_bases[0],gt_bases[i]],transition)
                        try:
                            fobP = FilterByOrientationBias.getFOBandPvalue(snCall,i,*trans_type.split(">"))
                        except ZeroDivisionError:
                            fobP = [None,None]
                        fob.append(fobP[0])
                        pvalue.append(fobP[1])
                        obam_tag.append(obam[0])
                        obamrc_tag.append(obam[1])
                        if fobP[0] is not None:
                            artifactrecord[trans_type][ln] = {"FOB":fobP[0],"PVALUE":fobP[1],"rec":rec}
                    else:
                        obam_tag.append("false")
                        obamrc_tag.append("false")
                        fob.append(None)
                        pvalue.append(None)
                    obq.append(artifactQscore[trans_type]["score"])
                    obq_rc.append(artifactQscore[trans_type_rev]["score"])
                nd = nd._make(calldata + [obam_tag,obamrc_tag,fob,pvalue,obq,obq_rc])
            snCall.data = nd
        rec.FORMAT = sorted(FORMAT,key=len)[-1]
        new_record.append(rec)        
    vcfin.close()    
    artifactPOS = dict.fromkeys(artifactrecord.keys(),[])
    for t in artifactrecord:        
        # trans = t if t in transition else ">".join([complements[i] for i in t.split(">")])
        v = sorted(artifactrecord[t].items(),key=lambda x:x[1]["PVALUE"],reverse=True)
        pvalue = [i[1]["PVALUE"] for i in v]
        pre_cut_num = len(pvalue) - 1
        for p in range(len(pvalue)):
            if pvalue[p] < fdrThreshold*(p+1)/len(pvalue):
                pre_cut_num = p
                break
        # suppression = 1/(1+exp(BIASQP2*(artifactQscore[trans]-BIASQP1)))
        suppression = 1/(1+exp(BIASQP2*(artifactQscore[t]["score"]-BIASQP1)))
        post_cut_num = int(round(pre_cut_num*suppression))
        artifactPOS[t] = [i[0] for i in v[:post_cut_num]]
        print t,dict(total=len(pvalue),pre_cut_num=pre_cut_num,post_cut_num=post_cut_num) 
    filterPos = flatten(artifactPOS.values())
    for ln,rec in enumerate(new_record):
        if ln in filterPos:
            rec.add_filter("orientation_bias")
        cf_writer.write_record(rec)    
    vcfout.close()
    

