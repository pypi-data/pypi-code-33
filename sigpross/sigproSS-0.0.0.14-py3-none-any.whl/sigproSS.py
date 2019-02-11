# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 13:33:06 2018

@author: compactmatter
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from sigproSS import signatures_optimizer as sigopt
import os
import shutil
os.chdir(sys.path[-1])
import multiprocessing as mp
import xml.etree.ElementTree as ET  
from lxml import etree
from SigProfilerMatrixGenerator.scripts import SigProfilerMatrixGeneratorFunc as matGen
from sigproextractor import subroutines as sub
import sigproSS as cosmic

def get_connected_alwaysinclude_signatures(signatureRulesXML, signatures):
    tree = ET.parse(signatureRulesXML)      
    root = tree.getroot()
    
    #Connected
    csList = [] 
    csIDs = []      
    setList = []
    csLength = []
    connectedSignatures = []
    connectedSignaturesIDs = []

    for conn in root.find('connectedSignatures').findall('connected'):
        csLength.append(len(conn))
        setList.append(conn.get("Set"))
        for i in conn.findall('signature'):
            csList.append(i.text)

    csLengthCumSum = np.cumsum(csLength)
    for j in range(len(csList)):
        csIDs.append(signatures.index(csList[j]))
    for i in range(len(csLength)):
        if i == 0:
            connectedSignatures.append(csList[0:csLengthCumSum[i]])
            connectedSignaturesIDs.append(csIDs[0:csLengthCumSum[i]])
        else:
            connectedSignatures.append(csList[csLengthCumSum[i-1]:csLengthCumSum[i]])
            connectedSignaturesIDs.append(csIDs[csLengthCumSum[i-1]:csLengthCumSum[i]])
    
    #Always Include
    allowEverywhere = []
    for ai in root.find('alwaysIncludeSignatures').findall('signature'):
        allowEverywhere.append(ai.text)
    
    allowEverywhereIDs = [i for i, x in enumerate(signatures) if x in allowEverywhere]
    
    return[connectedSignaturesIDs, allowEverywhereIDs]
    


def check_signature_rules(signaturesInSample,
                          signatures,
                          sampleID,
                          seqType,
                          totalMutations,
                          C_to_A_p,
                          C_to_A_d,
                          C_to_G_p,
                          C_to_G_d,
                          C_to_T_p,
                          C_to_T_d,
                          T_to_A_p,
                          T_to_A_d,
                          T_to_C_p,
                          T_to_C_d,
                          T_to_C_ATN_p,
                          T_to_C_ATN_d,
                          T_to_G_p,
                          T_to_G_d,
                          signatureRulesXML,
                          signatureRulesXMLSchema):
    
    totalSignatures = len(signaturesInSample)  
    

    tree = ET.parse(signatureRulesXML)  
    
    #Validate XML file against schema
    xml = etree.parse(signatureRulesXML)

    schema_doc = etree.parse(signatureRulesXMLSchema)
    schema = etree.XMLSchema(schema_doc)

    if (schema.validate(xml) == False):
        print(schema.assertValid(xml))
    
    root = tree.getroot()

    signaturesList = []    
    for i in range(totalSignatures):
        for signature in root.findall('signatureName'):
            signaturesList.append(signature.get("signatureSBS"))
            
        if(signatures[i] in signaturesList):
            if (root.find(".//strandBias/..[@signatureSBS='" + signatures[i] + "']") is not None):
                strandbias = root.find(".//strandBias/..[@signatureSBS='" + signatures[i] + "']").find('strandBias').findall('mutationType')
                for sb in range(len(strandbias)):
                    if( eval(strandbias[sb].get('mutType').replace('>','_to_') + "_p") > float(strandbias[sb][1].text) or
                       eval(strandbias[sb].get('mutType').replace('>','_to_') + "_d") != float(strandbias[sb][0].text)):
                       signaturesInSample[i] = 0
                       
            if (root.find(".//totalMutations/..[@signatureSBS='" + signatures[i] + "']") is not None):
                totalmutations = root.find(".//totalMutations/..[@signatureSBS='" + signatures[i] + "']").find('totalMutations').findall('seqType')
                for st in range(len(totalmutations)):
                    if( totalmutations[st].get('type') == seqType):
                        if( float(totalMutations) < float(totalmutations[st][0].text) ):
                            signaturesInSample[i] = 0
                
    return signaturesInSample



def parallel_for_loop(iSample, inputSamples, allGenomeSignatures, allExomeSignatures, cancerType,
                      seqType, totalMutations, sampleNames, samplePvalue,
                      longSampleNames, totalSignatures, useRules, sigNames, idsToAdd, connected,
                      exposuresNew, accr_org, kl_div_org, frob_rel_div_org, norm_one_dif_org):
    
    
    
    #get the path for files
    paths = cosmic.__path__[0]
    
    genome = inputSamples[:,iSample]
    genome = genome.reshape(96,1) #Uncomment for other functions
    if (seqType[iSample] == 'WGS'):
        allSignatures =  allGenomeSignatures
    else:
        allSignatures =  allExomeSignatures
        
    #Identify signatures in cancer type and apply signature rules
    
    
                  

    longSampleName = cancerType[iSample] + '::' + sampleNames[iSample]

    signaturesInSamples = np.zeros([allSignatures.shape[1], inputSamples.shape[1]])
        
    exposures = signaturesInSamples[:, longSampleNames.index(longSampleName)]
    #print(exposures.shape)
    if ( exposures.size == 0 ):
        exposures = np.zeros((totalSignatures, 1))
    
      
    
    C_to_A_p = samplePvalue.iloc[0][0]
    C_to_A_d = samplePvalue.iloc[0][1]
    C_to_G_p = samplePvalue.iloc[1][0]
    C_to_G_d = samplePvalue.iloc[1][1]
    C_to_T_p = samplePvalue.iloc[2][0]
    C_to_T_d = samplePvalue.iloc[2][1]
    T_to_A_p = samplePvalue.iloc[3][0]
    T_to_A_d = samplePvalue.iloc[3][1]
    T_to_C_p = samplePvalue.iloc[4][0]
    T_to_C_d = samplePvalue.iloc[4][1]
    T_to_C_ATN_p = samplePvalue.iloc[5][0]
    T_to_C_ATN_d = samplePvalue.iloc[5][1]
    T_to_G_p = samplePvalue.iloc[6][0]
    T_to_G_d = samplePvalue.iloc[6][1]
    
    if ( useRules == True ):
        #print("Using rules")
        exposures = check_signature_rules(exposures,
                                          sigNames,
                                          iSample,
                                          seqType,
                                          totalMutations,
                                          C_to_A_p,
                                          C_to_A_d,
                                          C_to_G_p,
                                          C_to_G_d,
                                          C_to_T_p,
                                          C_to_T_d,
                                          T_to_A_p,
                                          T_to_A_d,
                                          T_to_C_p,
                                          T_to_C_d,
                                          T_to_C_ATN_p,
                                          T_to_C_ATN_d,
                                          T_to_G_p,
                                          T_to_G_d,
                                          paths+'input/20181108_Signature_Rules.xml',
                                          paths+'input/Signature_Rules_Schema.xsd')
    
    
    #print("Total Mutations", totalMutations[0])
    
    #Remove all signatures in the sample: one by one
    #Add signatures that are allowed everywhere    
    if (idsToAdd != False):
        exposures[idsToAdd] = 1 
    
    #Add connected signatures
    if (len(connected) > 0):
        for iConnect in range(len(connected)):
            if ( sum(exposures[connected[iConnect]]) > 0 ):
                exposures[connected[iConnect]] = 1
    
    #print(exposures)
    ##########################################################[exposures, accr, kl_div, frob_rel_div, norm_one_dif] = remove_all_single_signatures(exposures, allSignatures, genome, sigNames)

    
    IDs = [i for i,x in enumerate(exposures) if x > 0]
    processes = allSignatures[:,IDs]

    exposure =   sigopt.initial_optimization(processes, genome) #processes, sample 

    pool = mp.Pool(processes=1)
    results = [pool.apply_async(sigopt.remove_signatures, args=(x,processes,exposure,genome,)) for x in range(genome.shape[1])]
    
    output = [p.get() for p in results]
    pool.close()
    
    exposureAfterRemovingSignatures = np.zeros(exposure.shape)
    for i in range(len(output)):
        exposureAfterRemovingSignatures[:,i]=output[i] 

    np.put(exposures, IDs, exposureAfterRemovingSignatures.ravel())
    #Add all remaining signatures to the sample: one by one
    #Add signatures that are allowed everywhere
    #print(exposures)
    
    if (idsToAdd != False):
        for i in idsToAdd:
            exposures[i] = 1
       
    #Add connected signatures
    if (len(connected) > 0):
        for iConnect in range(len(connected)):
            if ( sum(exposures[connected[iConnect]]) > 0 ):
                exposures[connected[iConnect]] = 1

    #print(exposures)
    IDs = [i for i,x in enumerate(exposures) if x > 0] #Changed i to i+1 
    
    #print(exposureAfterRemovingSignatures) ###############
    
    
    ######################################################exposures = add_all_single_signatures(exposures, allSignatures, genome, sigNames) #No eval single sample now
    ## ## ## ##processes = allSignatures[:,IDs]
    
    ####################print(IDs) 
    #pd.DataFrame(processes).to_csv("processes_file.txt", sep = "\t")
    #pd.DataFrame(genome).to_csv("genome_file.txt", sep = "\t")
    #print("done")
    exposureAfterAddingSignatures = sigopt.add_signatures(allSignatures, genome, 0.025, IDs)[0]
    #print(len(exposureAfterAddingSignatures))
    #Add signatures that are allowed everywhere
    exposures = exposureAfterAddingSignatures
    ## ## ## ## np.put(exposures, IDs, exposureAfterAddingSignatures.ravel())
    #print(exposures)
    
    
    #print(exposures)#####################
    
    
    if (idsToAdd != False):
        exposures[idsToAdd] = 1

    #Add connected signatures
    if (len(connected) > 0):
        for iConnect in range(len(connected)):
            if ( sum(exposures[connected[iConnect]]) > 0 ):
                exposures[connected[iConnect]] = 1
    
    #print(exposures)
    IDs = [i for i,x in enumerate(exposures) if x > 0]
    
    ################################################################[exposures, accr_org[iSample], kl_div_org[iSample], frob_rel_div_org[iSample], norm_one_dif_org[iSample]] = eval_single_sample(exposures, allSignatures, genome)

    #IDs = [i for i,x in enumerate(exposures) if x > 0] #BEWARE
    #processes = allSignatures[:,IDs]#BEWARE

    #exposure =   initial_optimization(processes, genome)#BEWARE
    #exposures = np.zeros((totalSignatures, 1)) #BEWARE
    #np.put(exposures, IDs, exposure.ravel()) #BEWARE
    #print(exposures)
    exposuresNew[:, iSample] = exposures.ravel() #exposures
    #print(exposuresNew)
    indices = np.nonzero(exposuresNew)[0] 
    #print(exposuresNew[list(indices)])
    
    
    #fit the signatures 
    print("\n")
    sigNames=np.array(sigNames)
    exposures = sigopt.fit_signatures(allSignatures[:,list(indices)], genome)
    
    #print(indices)
    print(sigNames[list(indices)])
    #print(exposures) ##################
    
    
    
    #Dispay summary output data
    #out_str = ['Sample #' + str(iSample+1) + ': ' + str(inputSamples['cancerType'][iSample][0]) + ' ' + str(inputSamples['sampleNames'][iSample][0]) + ' with ' + str(sum(exposuresNew[:, iSample]>0)) + ' signatures and an accuracy of ' + str(round(accr_org[iSample][0],2))] #BEWARE ,'%.2f' removed
    out_str = ['Sample #' + str(iSample+1) + ': [' + str(cancerType[iSample]) + '] [' + str(sampleNames[iSample]) + '] with ' + str(sum(exposuresNew[:, iSample]>0)) + ' signatures']
    print(out_str)
    return([indices,exposures,sigNames, allSignatures])               


def analysis_individual_samples(#signaturesSet,
                                #signaturesInSamples,
                                samples,
                                #outputFolder,
                                #outputFile,
                                useRules,
                                #allowSigsEverywhere,
                                #connected,
                                newSignatures_file,
                                genomeSignatures_file,
                                exomeSignatures_file,
                                sampleNames,
                                sampleCancerTypes,
                                cancerType,
                                seqType,
                                totalMutations,
                                p_value,
                                signatureRulesXML):

    #Analysis of data
    #Loading samples
    
    inputSamples = samples
    
    
    
    #print(inputSamples)
    #print("\n")
    try:
        totalSamples = inputSamples.shape[1] 
    except:
        inputSamples = inputSamples[:,np.newaxis]
        totalSamples = inputSamples.shape[1] 
        
    accr_org = np.zeros((totalSamples, 1))
    kl_div_org = np.zeros((totalSamples, 1))  
    frob_rel_div_org = np.zeros((totalSamples, 1))
    norm_one_dif_org = np.zeros((totalSamples, 1)) 
    #print(inputSamples)
    #Loading signatures
    newSignatures = open(newSignatures_file,'r').read().split('\n')
    

    
    allGenomeSignatures = np.loadtxt(genomeSignatures_file)  
    allExomeSignatures  = np.loadtxt(exomeSignatures_file)
    sigNames = newSignatures
    totalSignatures = allGenomeSignatures.shape[1]
    exposuresNew = np.zeros((totalSignatures, totalSamples))
    #Loading signatures in samples
    
    
    
    
    
    longSampleNames = ["" for x in range(len(sampleNames))]
    
    for i in range(len(sampleNames)): #MATLAB CODE for i = 1 : size(sigsInCanType.sampleNames, 1)
       longSampleNames[i] = sampleCancerTypes[i] + '::' + sampleNames[i]

    

    #print(Parallel(n_jobs = num_cores)(delayed(parallel_for_loop)(iSample, inputSamples, allGenomeSignatures, allExomeSignatures, cancerType_file, seqType_file, totalMutations_file, sampleNames, signaturesInSamples_file, longSampleNames, totalSignatures, useRules, sigNames, idsToAdd, connected, saOptions, exposuresNew, accr_org, kl_div_org, frob_rel_div_org, norm_one_dif_org) for iSample in range(totalSamples)))
    #print(sigNames)
    [connected, allowSigsEverywhere] = get_connected_alwaysinclude_signatures(signatureRulesXML, sigNames)
    #print(connected)
    #print(allowSigsEverywhere)
    
    if(dir().count('allowSigsEverywhere') > 0 and len(allowSigsEverywhere) > 0):
        print('Allow these signatures in all samples:')
        for i in range(len(allowSigsEverywhere)):
            print(newSignatures[allowSigsEverywhere[i]])
            idsToAdd = allowSigsEverywhere
    else:
        idsToAdd = False 
    
    if (dir().count('connected') > 0 and len(connected) > 0):
        print('These mutational signatures are connected:')
        for i in range(len(connected)):
            dispStr = 'Set ' + str(i+1) + ':' + newSignatures[connected[i][0]]
            for j in range(1, len(connected[i])):
                dispStr = dispStr + '; ' + newSignatures[connected[i][j]]
            print(dispStr)

    #idsToAdd[:] = [x - 1 for x in idsToAdd] #To account for differences in MATLAB and Python array indexing
    #for iConnect in range(len(connected)): #To account for differences in MATLAB and Python array indexing
    #        connected[iConnect][:] = [x - 1 for x in connected[iConnect]]
    
    for iSample in range(totalSamples):
        samplePvalue = p_value.iloc[:,iSample]
        results = parallel_for_loop(iSample, inputSamples, allGenomeSignatures, allExomeSignatures, cancerType,
                                seqType, totalMutations, sampleNames, samplePvalue,
                                longSampleNames, totalSignatures, useRules, sigNames, idsToAdd, connected
                                , exposuresNew, accr_org, kl_div_org, frob_rel_div_org, norm_one_dif_org)
        #Select cancer sample and set of signatures      
        #if ( exist(outputFolder,'dir') == 0 ):
        #   mkdir(outputFolder)
        #save([outputFolder filesep outputFile])
    return results



def sigproSS(vcf, exome=False):
    
    #get the path for files
    paths = cosmic.__path__[0]
    
    data = matGen.SigProfilerMatrixGeneratorFunc(vcf, "GRCh37", vcf, exome=False)
    
    # make the totalExposure dataframe which have dimention of totalsignatures and totalsamples
    
    totalExposures = np.zeros([65,data["96"].shape[1]])
    listOfSamples = list(data["96"].head(0))
    
    for i in range(data["96"].shape[1]):
        print("##########################################################")
        print("Profile for "+str(i+1)+"th Sample" )
        index = i
        samples = data["96"].iloc[:,index:index+1]
        p_value = data["7_pvalue"]
        samples = np.array(samples)
        sampleNames = list(data["96"].head(0))[index:index+1]
        cancerType = ['Breast Cancer']*samples.shape[1]
        seqType = ['WGS']*samples.shape[1]
        totalMutations= np.sum(samples, axis=0)
        
        
        
        
        results = analysis_individual_samples(samples, 
                                    True,
                                    paths+'input/signaturesSet.txt',
                                    paths+'input/genomeSignatures.txt',
                                    paths+'input/exomeSignatures.txt',
                                     sampleNames,
                                     cancerType,
                                     cancerType,
                                     seqType,
                                     totalMutations,
                                     p_value,
                                    paths+'input/20181108_Signature_Rules.xml') 
        totalExposures[results[0],i]=results[1]
        listOfSignatures = results[2]
        signatures = pd.DataFrame(results[3])
        print("##########################################################")
        print("\n\n")
    
    #results variable contains [indices,exposures, signatureNames, allSignatures]
    
    #prepare the exposures dataframe
    
    totalExposures = pd.DataFrame(totalExposures)
    totalExposures = totalExposures.set_index(listOfSignatures)
    totalExposures.columns = listOfSamples
    totalExposures = totalExposures.rename_axis("Samples", axis="columns")
    #Convert the floats to integers
    totalExposures[listOfSamples] = totalExposures[listOfSamples].applymap(np.int64)
    
    
    
    #remove the rows with all zeros to create the final exposure dataframe
    exposures = totalExposures.loc[~(totalExposures==0).all(axis=1)]
    
    #presure the signatures dataframe
    signatures = pd.DataFrame(results[3])
    signatures.columns = listOfSignatures
    signatures = signatures.set_index(data["96"].index)
    signatures = signatures.rename_axis("Signatures", axis="columns")
    
    #Filter the signatures by the exposures rows to get the final signature dataframe
    signatures = signatures.loc[:,list(exposures.index)] 
    
    #create the probalities 
    probability = sub.probabilities(signatures, exposures)
    probability = probability.set_index("Sample")
    probability = probability.rename_axis("", axis="columns")
    
    try:
        #create the dedrogrames
        Y, dn = sub.dendrogram(exposures, 0.05, os.getcwd())
    except:
        pass
        
    #export results
    signatures.to_csv(os.getcwd()+"/signatures.txt", "\t", index_label=[signatures.columns.name]) 
    exposures.to_csv(os.getcwd()+"/exposures.txt", "\t", index_label=[exposures.columns.name]) 
    probability.to_csv(os.getcwd()+"/probabilities.txt", "\t")

def importdata():
    
    """
    Imports the path of example data.
    
    parameters
    ----------
            
    
    Returns:
    -------

    The path of the example data.

    Example: 
    -------
    >>> from sigproSS import sigproSS as sigSS
    >>> data = sigSS.importdata()
    
    This "data" variable can be used as a parameter of the "project" argument of the sigProfilerExtractor function
        
    """
    
    
    
    paths = cosmic.__path__[0]
    directory = os.getcwd()
    dataold = paths+"/input/vcf"
    datanew = directory+"/vcf"
    if not os.path.exists(datanew):
        shutil.copytree(dataold , datanew) 
    data="vcf"
    return data


if __name__ == "__main__":
    sigproSS("vcf", exome=False)
