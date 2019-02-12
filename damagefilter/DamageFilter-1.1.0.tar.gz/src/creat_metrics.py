#!/usr/bin/emv python
#coding:utf-8

import pysam
import time
import os
from collections import defaultdict,Counter
from math import log10
from tqdm import tqdm

from utils import reverseComp,create_dirs
from defaults import *


    
def getAlignedBlock(rdaln):   ### 根据cigai值获取比对reads的match或mismatch的区域，返回区域的一个列表
    alignmentBlocks = []
    cigartuple = rdaln.cigartuples
    readBase = 0                              ### 0-base
    refBase = rdaln.reference_start
    for t,n in cigartuple:
        if t in [5,6]:   ## H, P
            continue
        elif t in [4,1]:  ## S, I
            readBase += n
        elif t in [3,2]:    ## N, D
            refBase += n
        elif t in [0,7,8]: ## M, =, X
            alignmentBlocks.append((readBase,refBase,n))
            refBase += n
            readBase += n
        else:
            raise Exception("Error: cann't deal with cigar")
    return alignmentBlocks            

def run_creat_metrics(args):
    refa = pysam.FastaFile(args.ref)
    bam = pysam.AlignmentFile(args.input,"rb")
    contextFullLength = 2 * CONTEXT_SIZE + 1
    pre_metrics = defaultdict(lambda :defaultdict(Counter))
    bait_metrics = defaultdict(lambda :defaultdict(Counter))
    #for rdaln in tqdm(bam,total=bam.mapped+bam.unmapped):
    for rdaln in bam:
        if rdaln.is_unmapped or (not rdaln.is_paired):
            continue
        if any([rdaln.is_duplicate, rdaln.is_secondary, rdaln.is_qcfail, rdaln.mapping_quality < MINIMUM_MAPPING_QUALITY, 
                abs(rdaln.template_length) > MAXIMUM_INSERT_SIZE, abs(rdaln.template_length) < MINIMUM_INSERT_SIZE]):
            continue
        alignmentBlocks = getAlignedBlock(rdaln)
        readQuals = rdaln.query_qualities
        readBases = rdaln.query_sequence.upper()
        
        if (rdaln.is_read1 and rdaln.is_reverse) or (rdaln.is_read2 and (not rdaln.is_reverse)):      ### R1- or R2+
            for block in alignmentBlocks:
                refseq = refa.fetch(rdaln.reference_name,block[1]-CONTEXT_SIZE,block[1]+block[2]+CONTEXT_SIZE).upper()
                for offset in range(block[2]):
                    context =  refseq[offset:(offset+contextFullLength)] 
                    if "N" in context:
                        continue   
                    readPos = block[0] + offset
                    qual = readQuals[readPos]
                    if qual < MINIMUM_QUALITY_SCORE:
                        continue
                    readBase = readBases[readPos]
                    if readBase == "N":
                        continue                        
                    pre_metrics[readBase][context]["CON"] += 1
                    bait_metrics[readBase][context]["FWD"] += 1                          
        elif (rdaln.is_read1 and (not rdaln.is_reverse)) or (rdaln.is_read2 and rdaln.is_reverse):     ### R1+ or R2-
            for block in alignmentBlocks:
                refseq = refa.fetch(rdaln.reference_name,block[1]-CONTEXT_SIZE,block[1]+block[2]+CONTEXT_SIZE).upper()
                for offset in range(block[2]):
                    context =  refseq[offset:(offset+contextFullLength)] 
                    if "N" in context:
                        continue
                    readPos = block[0] + offset
                    qual = readQuals[readPos]
                    if qual < MINIMUM_QUALITY_SCORE:
                        continue
                    readBase = readBases[readPos]
                    if readBase == "N":
                        continue
                    pre_metrics[readBase][context]["PRO"] += 1
                    bait_metrics[readBase][context]["FWD"] += 1                                                
                        
    group = bam.header.get("RG")[0]
    SAMPLE_ALIAS = group.get("SM")
    LIBRARY = group.get("LB")
    bam.close()
    fo1 = open(os.path.join(args.outdir,args.prefix + ".pre_adapter_detail_metrics.txt"),"w")
    fo2 = open(os.path.join(args.outdir,args.prefix + ".bait_bias_detail_metrics.txt"),"w")
    fo1.write("SAMPLE_ALIAS\tLIBRARY\tREF_BASE\tALT_BASE\tCONTEXT\tPRO_REF_BASES\tPRO_ALT_BASES\tCON_REF_BASES\tCON_ALT_BASES\tERROR_RATE\tQSCORE\n")
    fo2.write('SAMPLE_ALIAS\tLIBRARY\tREF_BASE\tALT_BASE\tCONTEXT\tFWD_CXT_REF_BASES\tFWD_CXT_ALT_BASES\tREV_CXT_REF_BASES\tREV_CXT_ALT_BASES\tFWD_ERROR_RATE\tREV_ERROR_RATE\tERROR_RATE\tQSCORE\n')
    for ref in "ACGT":
        for alt in "ACGT":
            if alt == ref:
                continue
            for r1 in "ACGT":
                for r2 in "ACGT":
                    text = r1+ref+r2                    
                    pro_ref = pre_metrics[ref][text]["PRO"] + pre_metrics[complements[ref]][reverseComp(text)]["CON"]
                    pro_alt =  pre_metrics[alt][text]["PRO"] + pre_metrics[complements[alt]][reverseComp(text)]["CON"]
                    con_ref = pre_metrics[ref][text]["CON"] + pre_metrics[complements[ref]][reverseComp(text)]["PRO"]
                    con_alt = pre_metrics[alt][text]["CON"] + pre_metrics[complements[alt]][reverseComp(text)]["PRO"]
                    out = [SAMPLE_ALIAS,LIBRARY,ref,alt,text,pro_ref,pro_alt,con_ref,con_alt]
                    err_rate = max(pow(10,-10),float(out[-3]-out[-1])/sum(out[-4:])) if sum(out[-4:])>0 else pow(10,-10)
                    qscore = int(round(-10*log10(err_rate)))
                    err_rate = "%.6f"%err_rate if err_rate > pow(10,-10) else 0
                    out = map(str,out+[err_rate,qscore])                    
                    fo1.write("\t".join(out) + "\n")                    
                                       
                    #fwd_ref = bait_metrics[ref][text]["FWD"] + bait_metrics[complements[ref]][reverseComp(text)]["REV"]
                    #fwd_alt = bait_metrics[alt][text]["FWD"] + bait_metrics[complements[alt]][reverseComp(text)]["REV"]
                    #rev_ref = bait_metrics[ref][text]["REV"] + bait_metrics[complements[ref]][reverseComp(text)]["FWD"]
                    #rev_alt = bait_metrics[alt][text]["REV"] + bait_metrics[complements[alt]][reverseComp(text)]["FWD"]
                    fwd_ref = bait_metrics[ref][text]["FWD"]
                    fwd_alt = bait_metrics[alt][text]["FWD"]
                    rev_ref = bait_metrics[complements[ref]][reverseComp(text)]["FWD"]
                    rev_alt = bait_metrics[complements[alt]][reverseComp(text)]["FWD"]
                    bait_out = [SAMPLE_ALIAS,LIBRARY,ref,alt,text,fwd_ref,fwd_alt,rev_ref,rev_alt]
                    fwd_err_rate = max(pow(10,-10),float(bait_out[-3])/(bait_out[-3]+bait_out[-4])) if (bait_out[-3]+bait_out[-4]) > 0 else pow(10,-10)
                    rev_err_rate = max(pow(10,-10),float(bait_out[-1])/(bait_out[-1]+bait_out[-2])) if (bait_out[-1]+bait_out[-2]) > 0 else pow(10,-10)
                    err_rate = max(pow(10,-10),fwd_err_rate-rev_err_rate)
                    qscore = int(round(-10*log10(err_rate)))
                    err_rate = "%.6f"%err_rate if err_rate > pow(10,-10) else 0 
                    fwd_err_rate = "%.6f"%fwd_err_rate if fwd_err_rate > pow(10,-10) else 0 
                    rev_err_rate = "%.6f"%rev_err_rate if rev_err_rate > pow(10,-10) else 0 
                    bait_out = map(str,bait_out+[fwd_err_rate,rev_err_rate,err_rate,qscore])
                    fo2.write("\t".join(bait_out) + "\n")
    fo1.close()                   
    fo2.close() 

