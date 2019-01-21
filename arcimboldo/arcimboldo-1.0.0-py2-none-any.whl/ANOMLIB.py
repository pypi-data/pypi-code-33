# ! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import ConfigParser
import cStringIO
import re
import glob
import numpy as np
import math
import json

#home-made modules
import unitCellTools 
import ADT # Heaps from Masimo 

#User defined constants:
CUTOFF_HA_PEAK_HEIGHT = 5.8      # Minimum ha peak height for the top ha from a lst file (DISCRIMINATIVE)
CUTOFFHA=5.5                     # Distance ha-c-beta from which the heavy atom is considered as potentially correctly placed after MR-SAD
THRESPEAKDIFF=1.0                # threshold for max difference in intensity from ha peaks from the lst file
CUTOFF_REFHA= 50.1               # Max distance from a found ha (by cross Fourier) and a reference one, in Angtroms  (DISCRIMINATIVE)
THRESHOLD_CCHA=0.01              # Min correlation coef. from ha to accept a solution (DISCRIMINATIVE)
SIGMAPATTERSON=3.0               # Retain Patterson peaks higher or equal to this standard deviation (DISCRIMINATIVE)
THRESHOLD_PATT= 30.0              #Maximum allowed Patterson scoring in evaluateExp function


GOOD_CC_TRACE = 20              # CC (percentage) above which no filtering will occur in evaluateExp and evaluateExp_CC
NBUNCH=1                         #number of autotracing cycles per bunch (normally 1)
#Path to executables
SHELXC="shelxc"
SHELXD="shelxd"
XDSCONV="xdsconv"
MTZ2SCA="mtz2sca"
F2MTZ="f2mtz"
CAD="cad"
MTZ2VARIOUS="mtz2various"
MTZDMP="mtzdmp"

#Check that all executables are presents, exit otherwise

#Regular expressionA
regexprATOMprot=re.compile(r"^(ATOM  )([\d\.\s]{5})(\s)(.{4})(.{1})(.{3})(\s)(.{1})(.{4})(.{1})(.{3})([.\d\s\-]{8})([.\d\s\-]{8})([.\d\s\-]{8})(.{6})(.{6})(\s{10})(.{2}).*")
regexprATOM=re.compile(r"^(ATOM  |HETATM)([\d\.\s]{5}).{10}(.{1}).{8}([.\d\s\-]{8})([.\d\s\-]{8})([.\d\s\-]{8}).*")
regexprATOM2=re.compile(r"(ATOM  |HETATM)([\d\.\s]{5})(\s)(.{4})(.{1})(.{3})(\s)(.{1})(.{4})(.{1})(.{3})([.\d\s\-]{8})([.\d\s\-]{8})([.\d\s\-]{8})(.{6})(.{6})(\s{10})(.{2}).*") 
regexprEND=re.compile(r"^END")
cBetaAtomLine=re.compile(r"^ATOM[\s\d]{9}CB  (\w{3}) (.)([\d\s]{4}).{4}([\-\d\s.]{8})([\-\d\s.]{8})([\-\d\s.]{8})")
cHAatomLine=re.compile(r"^HETATM.{11}HAT.{2}([\d\s]{4}).{4}([\-\d\s.]{8})([\-\d\s.]{8})([\-\d\s.]{8})")
atom_re=re.compile(r"^[\d\w]+\s+[\d]\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)")  #captures an atom line in the fractional coordinate file
ligne_hkl_re=re.compile(r"([\-\d\s]{4})([\-\d\s]{4})([\-\d\s]{4})([.\-\d\s]{8})([.\-\d\s]{8}).*")      #h k l I SIGI (as 3x int(4) 2x float(8.2))
regxyz=re.compile(r".*[XxyYzZ]")
reg_res_peak_start=re.compile(r"\s+Site    x       y       z  h\(sig\) near old  near new")

#Regexpr for finding peak heights in lst files:
reg_res_peak_list=re.compile(r"\s{0,}(\d+)\s+([.\d\-]{6})\s+([.\d\-]{6})\s+([.\d\-]{6})\s+([.\d\-]+)")
reg_res_peak_stop=re.compile(r"\s{0,}Best trace \(cycle")
regxpFreetxt=re.compile(r"\s{0,}[\d.\-]+\s+[\d.\-]+\s+[\d.\-]+")
regxp_CCpartial= re.compile(r"\s{0,}CC for partial structure against native data =\s+([\d.\-]+)")
regxp_CCpartial2=re.compile(r"\s{0,}Overall CC between native Eobs and Ecalc \(from fragment\) = \s+([.\d\-]+)")
regxp_CCha=re.compile(r"\s{0,}Overall CC between Eobs \(from delF\) and Ecalc \(from heavy atoms\) =\s+([.\d\-]+)")
regxp_wMPE=re.compile(r".*wMPE ([\d.]{3,5}) / ([\d.]{3,5})")

# This was parsed from a txt version of the periodic table: http://pastebin.com/raw/CKwm136x
NELECTRONS={ 'H':1, 'HE':2, 'LI':3, 'BE':4, 'B':5, 'C':6, 'N':7, 'O':8, 'F':9, 'NE':10, 'NA':11, 'MG':12, 'AL':13, 'SI':14, 'P':15, 'S':16, 'CL':17, 'AR':18, 'K':19, 'CA':20, 'SC':21, 'TI':22, 'V':23, 'CR':24, 'MN':25, 'FE':26, 'CO':27, 'NI':28, 'CU':29, 'ZN':30, 'GA':31, 'GE':32, 'AS':33, 'SE':34, 'BR':35, 'KR':36, 'RB':37, 'SR':38, 'Y':39, 'ZR':40, 'NB':41, 'MO':42, 'TC':43, 'RU':44, 'RH':45, 'PD':46, 'AG':47, 'CD':48, 'IN':49, 'SN':50, 'SB':51, 'TE':52, 'I':53, 'XE':54, 'CS':55, 'BA':56, 'LA':57, 'CE':58, 'PR':59, 'ND':60, 'PM':61, 'SM':62, 'EU':63, 'GD':64, 'TB':65, 'DY':66, 'HO':67, 'ER':68, 'TM':69, 'YB':70, 'LU':71, 'HF':72, 'TA':73, 'W':74, 'RE':75, 'OS':76, 'IR':77, 'PT':78, 'AU':79, 'HG':80, 'TL':81, 'PB':82, 'BI':83, 'PO':84, 'AT':85, 'RN':86, 'FR':87, 'RA':88, 'AC':89, 'TH':90, 'PA':91, 'U':92, 'NP':93, 'PU':94, 'AM':95, 'CM':96, 'BK':97, 'CF':98, 'ES':99, 'FM':100, 'MD':101, 'NO':102, 'LR':103, 'RF':104, 'DB':105, 'SG':106, 'BH':107, 'HS':108, 'MT':109, 'UUN':110, 'UUU':111, 'UUB':112, 'UUT':113, 'UUQ':114, 'UUP':115, 'UUH':116, 'UUS':117, 'UUO':118,}

currentParameters= ('hkl_fa_path', 'ins_fa_path', 'expphasing', 'nsites_expected', 'ha_present_in_native', 'recycle_ha', 'sfac', 'dsul', 'specialPos', 'rootAnom', 'dano_label', 'sigdano_label', 'nat_path', 'peak_path', 'infl_path', 'hrem_path', 'lrem_path', 'sir_path', 'sira_path', 'before_path', 'after_path', 'minusz', 'minusz_zero', 'minuso', 'evaluateAnom', 'patterson', 'referenceHA', 'hardFilter')
####General use functions
def vecIsZero(oneDarray=(0,0,0), targetVal=0):
    """ Checks wehter all elements of a vector are zero whether it is a tuple, numpy array or other iterable"""
    try:
        return  all([True if x==targetVal else False for x in oneDarray])
    except:
        return False

def anomParameters():
    """ returns a list of the current anomalous parameters for the different Arcimboldo programs"""
    return currentParameters

def launchProcess(cmd, printOut=True, output=False):
    p=subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True )
    log=p.stdout.read()

    if printOut:
        print log #if .read() is not present, the program doesn't wait for the process to finish

    if output:
        return log

def pathHAT2RESfile(c="/my/directory/8_EXP/0/1/0/truc.hat",hat2res=False, writeRes=False, ANOMDIR=None, isAlixe=False):
    """returns the final arborescence, ex: /0/1/0/truc_fa.res, useful to recover the path where .res files are stored, 
    if 'writeRes' True, it will increment the autotracing cycle number to refer to the next one 
    """
    flag=False
    out=[]
    c=os.path.normpath(c)
    c=c.split('/')

    borgesEXPdir= "11_EXP_alixe" if isAlixe else "11_EXP"

    for elem in c:
        if elem=="8_EXP_LIBRARY" or elem == borgesEXPdir:
            flag=True
        elif flag:
            out.append(elem)
    if len(out)==0:
        return None

    if hat2res:
        out[-1]=re.sub(r"\.hat",r"_fa.res",out[-1])
    if writeRes:
        try:
            out[-3]= str(int(out[-3])+1)         #This is the autotracing cycle number, we refer to the next one by incrementing it 
        except:
            print("WARNING pathHAT2RESfile: cannot increment the autotracing cycle number in the path to store the resfile")

    subpathOut=('/'.join(out))   #subpath without redundant characters
    if ANOMDIR != None:
        dirOut=os.path.join(ANOMDIR,'RESFILES')
        subpathOut=os.path.join(dirOut,subpathOut)
    return subpathOut

####Data conversion functions

def mtz2sca(anomDir,mtzFilePath):


    if not os.path.exists(anomDir):
        try:
            os.makedirs(anomDir)

        except OSError:
            print("Error","Cannot create directory %s for handling anomalous data, STOPPING NOW"%anomDir)
            return -1

    workingDir=os.getcwd()
    anomDir=os.path.abspath(anomDir)
    inputFile=os.path.abspath(mtzFilePath)
    shutil.copy(inputFile,anomDir)
    basename=os.path.basename(mtzFilePath)

    cmd=MTZ2SCA+" "+basename
    print("Converting the input MTZ with anomalous signal into sca file: ")
    print(cmd)

    os.chdir(anomDir)
    launchProcess(cmd)
    os.remove(os.path.join(anomDir,basename)) #remove the copied mtzfile in anomDir
    os.chdir(workingDir)

    outputName, ext = os.path.splitext(basename) #just to get mtzFileName.sca
    outputName += ".sca" 

    return os.path.join(anomDir,outputName)      #Returns the path to the sca file
    
def mtz2sca2(anomDir="path/To/Anomalous/Data/Dir", MTZfilePathIn="path/To/my/MTZ", label="_label"):
    """
    Handles the general case where a single MTZ file if provided, the sca file 
    and must be converted to scalepack format, which is readable by SHELXC (H K L I(+) SIGI(+) I(-) SIGI(-))
    """

    #Set the final scalepack file path
    outputName, ext = os.path.splitext(os.path.basename())
    outputName += ".sca"
    scafilePath=os.path.join(anomDir,outputName)


    convertCMD=""" %s HKLIN %s HKLOUT %s <<EOF
OUTPUT SCALEPACK
labin  I(+)=I%s(+) SIGI(+)=SIGI%s(+)
I(-)=I%s(-) SIGI(-)=SIGI%s(-)
EOF
    """%(MTZ2VARIOUS, MTZfilePathIn, scafilePath,label, label,label,label)


    return  spaceGroupNum, unitcellDim, scaFilePath

def xds2hkl(anomDir="path/To/Anomalous/Data/Dir", HKLin="path/To/My/XDS/File"):
    """
    uses XDSCONV to convert to shelx format We should not need this function but just in case...
    """

    workingDir=os.getcwd()
    anomDir=os.path.abspath(anomDir)
    inputFile=os.path.abspath(HKLin)
    shutil.copy(inputFile,anomDir)
    writebuffer=''

    #Set the final hkl path
    basename=os.path.basename(HKLin)
    outputName, ext = os.path.splitext(basename)
    outputName += ".hkl" 
    outputFilePath=os.path.join(anomDir,outputName)


    #Creating the XDSCONV.INP input file (output format SHELX)

    writebuffer = "INPUT_FILE="+inputFile+"\n"
    writebuffer += "OUTPUT_FILE="+outputName+" SHELX\n"
    writebuffer += "FRIEDEL'S_LAW=FALSE \n"
    writebuffer += "GENERATE_FRACTION_OF_TEST_REFLECTIONS=0.0  !No Rfree\n"


    #Write to the XDSCONV input file
    XDSCONVinp = open(os.path.join(anomDir,"XDSCONV.INP"),'w')
    XDSCONVinp.write(writebuffer)
    XDSCONVinp.close()
    writebuffer = ""

    os.chdir(anomDir)
    launchProcess("xdsconv")
    os.chdir(workingDir)

    for fichier in ("XDSCONV.INP","XDSCONV.LP",basename):
        try:
            os.remove(os.path.join(anomDir,fichier))
        except:
            print("Warning: cannot delete file %s"%fichier)

    return outputFilePath

def xds2mtz(anomDir="path/To/Anomalous/Data/Dir", HKLin="path/To/My/XDS/File", waveLength=0, xtalname="anomCrystal",dataname="anomData"):
    """
    Generates the MTZ file that contains Intensities, Amplitudes, DANO, F+, F- from an XDS file
    (similar to xds2mtz.pl)

    """

    #Change directory to this ANOMFILE (shelx programs don't like absolute path due to limited number of characters allowed)
    initialDir=os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(anomDir)   #changing to the local directory to run SHELXE (it doesn't like absolute paths as arguments if they are too long)

    #Set the final MTZ path
    outputName, ext = os.path.splitext(os.path.basename(HKLin))
    outputName += ".mtz" 
    MTZfilePath=os.path.join(anomDir,outputName)

    #STEP1: creating the XDSCONV.INP input file (for FIRST PASS FP, SIGFP, F+, F-, I+, I-)

    writebuffer = "INPUT_FILE="+HKLin+"\n"
    writebuffer += "OUTPUT_FILE="+os.path.join(anomDir,"temp1.hkl")+" CCP4_I+F\n"
    writebuffer += "FRIEDEL'S_LAW=FALSE \n"
    writebuffer += "GENERATE_FRACTION_OF_TEST_REFLECTIONS=0.0  !No Rfree\n"


    #Write to the XDSCONV input file
    XDSCONVinp = open("XDSCONV.INP",'w')
    XDSCONVinp.write(writebuffer)
    XDSCONVinp.close()
    writebuffer = ""

    launchProcess("xdsconv")

    #STEP2: The file F2MTZ.INP has been generated by XDSCONV, use it to get tmp1.mtz
    f2mtz_cmd += F2MTZ+" HKLOUT temp1.mtz<F2MTZ.INP"

    #Launching the F2MTZ1 command
    launchProcess(f2mtz_cmd)

    for file in ("F2MTZ.INP","XDSCONV.INP"):
        try:
            os.remove(file)
        except:
            print "Warning: file %s cannot be removed"

    #STEP3: creating the XDSCONV2.INP input file (for second pass DANO, SIGDANO, ISYM)

    writebuffer = "INPUT_FILE="+HKLin+"\n"
    writebuffer += "OUTPUT_FILE="+os.path.join(anomDir,"temp1.hkl")+" CCP4\n" #This time we get DANO SIGDANO and ISYM
    writebuffer += "FRIEDEL'S_LAW=FALSE \n"
    writebuffer += "GENERATE_FRACTION_OF_TEST_REFLECTIONS=0.0  !No Rfree\n"

        #Write to the XDSCONV input file
    XDSCONVinp = open("XDSCONV.INP",'w')
    XDSCONVinp.write(writebuffer)
    XDSCONVinp.close()
    writebuffer = ""

    launchProcess("xdsconv")

    #STEP4, again after creating F2MTZ.INP we can use it
    f2mtz_cmd += F2MTZ+" HKLOUT temp2.mtz<F2MTZ.INP"

    #Launching the F2MTZ1 command
    launchProcess(f2mtz_cmd)

    #STEP5 Now merge the 2 tmp mtz with CAD
    cad_cmd1="""cad HKLIN1 temp1.mtz HKLIN2 temp2.mtz HKLOUT temp3.mtz<<EOF
LABIN FILE 1 E1=IMEAN E2=SIGIMEAN E3=FP E4=SIGFP 
CTYP FILE 1 E1=J E2=Q E3=F E4=Q 
LABOUT FILE 1 E1=IMEAN E2=SIGIMEAN E3=F E4=SIGF 
LABIN FILE 2 E1=DANO E2=SIGDANO E3=ISYM
CTYP FILE 2 E1=D E2=Q E3=Y 
XNAME FILE 1 E1=%s E2=%s E3=%s E4=%s
DNAME FILE 1 E1=%s E2=%s E3=%s E4=%s
DWAVE FILE_NUMBER 1 %s %s %s
XNAME FILE 2 E1=%s E2=%s E3=%s E4=%s
DNAME FILE 2 E1=%s E2=%s E3=%s E4=%s
DWAVE FILE_NUMBER 2 %s %s %s
EOF
"""%(xtalname,xtalname,xtalname,xtalname,dataname,dataname,dataname,dataname,xtalname,dataname,waveLength,xtalname,xtalname,xtalname,xtalname,dataname,dataname,dataname,dataname,xtalname,dataname,waveLength)

    #Launching the CAD command
    launchProcess(cad_cmd1)

    #STEP6: reordering the column in the mtz produced by CAD:

    cad_cmd2="""%s HKLIN1 temp3.mtz HKLIN2 temp1.mtz HKLOUT %s<<EOF
LABIN FILE 1 ALL 
LABIN FILE 2  E1=I(+) E2=SIGI(+) E3=I(-) E4=SIGI(-) E5=F(+) E6=SIGF(+) E7=F(-) E8=SIGF(-) 
CTYP FILE 2  E1=K E2=M E3=K E4=M E5=G E6=L E7=G E8=L
EOF
"""%(CAD,MTZfilePath)

    #Launching the CAD command
    launchProcess(cad_cmd2)

    #Delete unecessary files:
    for fichier in ("XDSCONV.INP","temp1.hkl","F2MTZ.INP","XDSCONV.LP","temp1.mtz","temp2.hkl","temp2.mtz","temp3.mtz"):
        try:
            os.path.remove(fichier)
        except:
            print("Warning: cannot remove file %s"%fichier)


    #Go back to initial directory
    os.chdir(initialDir)

    return MTZfilePath

def hkl2mtz(anomDir="path/To/Anomalous/Data/Dir",hklin="path/To/My/Scalepack/File", spaceGroupnum=1, cell=[0,0,0,90,90,90]):
    """
    Creates a MTZ file from hkl or scalepack format for launching ARCIMBOLDO after the substructure search. 
    info about space group and unit cell dimension will have to be provided
    """

    #return MTZfilePath  #T D LATER
    pass

def filePresent(filePath):
    """ checks whether a file exists"""
    out =False
    if filePath is not None and filePath.lower() !='none':
        if os.path.exists(os.path.abspath(filePath)):
            if os.path.getsize(os.path.abspath(filePath))>0:
                out= True
            else:
                print("ERROR: file %s is present but has size zero"%os.path.abspath(filePath))

    return out


def addAnomToshelxeLine(shelxeArgLineList, nsites_expected=10, minusz=False, minusz_zero=False, minuso=False, ha_present_in_native=True, autotracing_cycle_number=1, recycle_ha=False, no_autotracing=False, provided_ha=False, hres_cutoff=0.0):
    """checking shelxe arguments and adding the ones specific to cross-Fourier map if necessary"""



    for j,arg in enumerate(shelxeArgLineList):
        if arg.startswith("-z") or arg.startswith("-h") or arg.startswith("-o") or (no_autotracing and arg.startswith("-a")):    # or arg.startswith("-K"):
            del shelxeArgLineList[j]        #remove any -z,-h argument if present


    # Make the -z0 option priority over -z
    if minusz_zero and recycle_ha and autotracing_cycle_number>1 or (provided_ha):                  #Note with the shelxe_magic, we want the -z option to be active only from the second cycle  
        shelxeArgLineList.append('-z0')    #Reads previous .res file and find/optimises new sites, a .res file MUST be present (which is ok if we provide it)

    elif (minusz and recycle_ha and autotracing_cycle_number>1) or (not recycle_ha):
        shelxeArgLineList.append('-z'+str(nsites_expected))  #optimizes sites

    if minuso and not no_autotracing:                     # We don't want -o in cycles of only HA refinement
        shelxeArgLineList.append('-o')                    #optimizes the input pda

    if ha_present_in_native:            #If heavy atoms are present in the native structure,
        shelxeArgLineList.append('-h'+str(nsites_expected))

    if no_autotracing:
        shelxeArgLineList.append('-a0')

    return shelxeArgLineList

def anomInfo(mode, inputAnomFileDic):
    """ Checks whether the files provided form the [ANOMALOUS] section of a .bor file are sufficent to generate the difference file hkl_fa with shelxc"""
    #i.e checking that a minimal information is present
    #Note the entry dictionary looks like {"NAT":"path/to/native_file.hkl", }

    if mode == "MRSAD":
        if "SAD" in inputAnomFileDic and filePresent(inputAnomFileDic['SAD']):
            return True
    elif mode == "MRMAD" and "PEAK" in inputAnomFileDic and filePresent(inputAnomFileDic['PEAK']) and "INFL" in inputAnomFileDic and filePresent(inputAnomFileDic['INFL']):
        return True
    elif mode == "SIR" and "NAT" in inputAnomFileDic and filePresent(inputAnomFileDic['NAT']) and "SIR" in inputAnomFileDic and filePresent(inputAnomFileDic['SIR']):  
        return True
    elif mode == "SIRA" and "NAT" in inputAnomFileDic and filePresent(inputAnomFileDic['NAT']) and "SIRA" in inputAnomFileDic and filePresent(inputAnomFileDic['SIRA']):  
        return True
    elif mode == "RIP" and "BEFORE" in inputAnomFileDic and filePresent(inputAnomFileDic['BEFORE']) and "AFTER" in inputAnomFileDic and filePresent(inputAnomFileDic['AFTER']):  
        return True

    return False

def infoMTZ(mtzFilePath):
    """
    Running mtzdmp -e on a file and capturing the output to extract the labels, space group and unit cell dimensions

    """

    hd=launchProcess(MTZDMP+" "+mtzFilePath+" -e",output=True,printOut=False)

    bufferout=""
    columns=[]                                     #Output variables
    columnTypes=[]
    unitcellDim=[]
    spaceGroupNum=0
    wavelength=0

    sg_re=re.compile(r"^.*Space group =.*\(number\s+(\d+)\)")
    uc_re=re.compile(r"^\s+[\d.]{5,8}\s+[\d.]{5,8}\s+[\d.]{5,8}\s+[\d.]{5,8}\s+[\d.]{5,8}\s+[\d.]{5,8}")
    wl_re=re.compile(r"^\s+[\d]\.[\d]+$")

    for line in hd.splitlines():                    #returning each line one by one

        msg=sg_re.match(line)
        muc=uc_re.match(line)
        mwl=wl_re.match(line)

        if re.match(" H K L",line):
            bufferout=line    #capture all the labels
            columns=bufferout.split()

        elif re.match(" H H H",line):
            bufferout=line    #capture all the labels
            columnTypes=bufferout.split()

        #capture unit cell dimensions
        elif msg:
            spaceGroupNum=int(msg.group(1))

        #capture  wave length
        elif muc:
            bufferout=line   
            unitcellDim=bufferout.split()
            unitcellDim=[float(x) for x in unitcellDim] #convert into float

        #capture space group
        elif mwl:
            wavelength=float(line.strip())

        #retrieve K:    intensity associated with one member of an hkl -h-k-l pair, I(+) or I(-)
        #It also checks that anomalous signal record is present in the input MTZ file (either I(+/-) or DANO)

    IplusFound=False
    danoFound=False
    Ffound=False
    ImeanFound=False

    ilabel=0
    iF=0
    iImean=0
    iDano=0
    for i,tipo in enumerate(columnTypes):
        if tipo.strip() == 'K':
            ilabel=i
            IplusFound=True

        elif tipo.strip() == 'D':
            iDano=i
            danoFound=True

        elif tipo.strip() == 'J':
            iImean=i
            ImeanFound=True

        elif tipo.strip() == 'F':
            iF=i
            Ffound=True

    if not IplusFound and not danoFound:
        print("WARNING: your mtz doesn't contain any anomalous signal record! (either I(+) I(-) or DANO)")

    #retrieving the label from the right column from the MTZ file
    labelOut=""
    if IplusFound:
        record=columns[ilabel]
        label_re=re.compile(r"^I_(.+)\([+\-]\)")
        m=label_re.match(record)
        if m:
            labelOut=m.group(1)
        else:
            print("WARNING: the mtzlabel cannot be extracted from I(+) or I(-) record")

    elif ImeanFound:
        record=columns[iImean]
        label_re=re.compile(r"^(IMEAN_|Imean_)(.+)")
        m=label_re.match(record)
        if m:
            labelOut=m.group(2)
        else:
            print("WARNING: the mtzlabel cannot be extracted from Imean record")

    elif Ffound:
        record=columns[Fmean]
        label_re=re.compile(r"^F_(.+)")
        m=label_re.match(record)
        if m:
            labelOut=m.group(1)
        else:
            print("WARNING: the mtzlabel cannot be extracted from F record")

    outputTypeDic={'Iplus':IplusFound,'Imean':ImeanFound,'dano':danoFound,'F':Ffound} #allows to know what type of information has been found in the mtz file

    return (outputTypeDic,labelOut, spaceGroupNum, wavelength, unitcellDim)


def retrieveUnitCellParameterXDS(xdsfilePath):
    """
    Retrieve the unit cell parameters from and XDS file
    """
    spacegroup_re=re.compile(r"^\!SPACE_GROUP_NUMBER=\s+([\d]+)")
    unitcell_re=re.compile(r"^\!UNIT_CELL_CONSTANTS=\s+([.\d]+)\s+([.\d]+)\s+([.\d]+)\s+([.\d]+)\s+([.\d]+)\s+([.\d]+)")
    wavelength_re=re.compile(r"^\!X-RAY_WAVELENGTH=\s+([.\d]+)")

    #output variables
    sgnum=0
    unitCellDim=[0,0,0,0,0,0]
    wavelength=0

    try:
        with open(xdsfilePath,'r') as xdsf:
            for line in xdsf:

                match_sg= spacegroup_re.match(line)
                match_unitCell= unitcell_re.match(line)
                match_wl= wavelength_re.match(line)

                if match_sg:
                    sgnum = int(match_sg.group(1))

                elif match_unitCell:
                    for i in range(0,6):
                        unitCellDim[i] = float(match_unitCell.group(i+1))

                elif match_wl:
                    wavelength = float(match_wl.group(1))

        print "Extracted parameters from the provided XDS file:"
        print "---> Space group: %s"%sgnum
        print "---> Unit cell parameters: %s"%unitCellDim
        print "---> Wavelength: %s"%wavelength
        print ""
        return sgnum, unitCellDim, wavelength

    except:
        print "Problem opening file %s"%xdsfilePath
        return -1

def prepareWithSHELXC(mode="MRSAD", format='hkl', workingDirectory="",inputFilesDic={"NAT":"path/to/my/natData.hkl", "PEAK":"path/to/my/peakData.hkl"},cell=[0,0,0,0,0,0],spaceGroupNum=1, waveLength=0, sfac='SE', dsul=0, nsites=5, ntry=5000, mind=2.5, specialPos=False,rootAnom="shlxanom"):
    """
    Calls SHELXC to prepare the input file
    It should detect the format and provides SHELXC with an hkl file (from MTZ) or directly an XDS HKL file
    possible format: hkl (scalepack intensities), HKL (XDS file), MTZ (will assume MTZ if it cannot recognize it)

    It will have also to create a directory into the Arcimboldo Working directory for storing SHELXD input files and search results

    mode: Type of experimental phasing mode, the most common will be MRSAD
    format: format of the input data, mtz, hkl, HKL 

    """

    #INITIAL CHECKS
    mode=mode.upper()

    #Put all the keys of the input files dictionary in capital letter (dictionary comprehension), and change to absolute paths
    inputFilesDic={k.upper():os.path.abspath(y) for k,y in inputFilesDic.items()}

    #Ensure to work with floats in the unit cell parameters (it can sometimes contain strings)
    cell=[float(x) for x in cell]

    #Get the absolute path to be sure
    workingDirectory=os.path.abspath(workingDirectory)

    #Create a directory to handle the anomalous files
    anomDir=os.path.join(workingDirectory,"ANOMFILES")

    if not os.path.exists(anomDir):
        try:
            print("prepareWithSHELXC: attempting creating directory %s for storing the anomalous files"%anomDir)
            os.makedirs(anomDir)

        except OSError:
            print("Error","Cannot create directory %s for handling anomalous data, STOPPING NOW"%anomDir)
            return -1

    #Change directory to this ANOMFILE (shelx programs don't like absolute path due to limited number of characters allowed)
 #   initialDir=os.path.dirname(os.path.realpath(sys.argv[0]))
    initialDir= os.getcwd()
    print("Initial directory: %s"%initialDir)
    print("Changing temporarily to %s"%anomDir)
    os.chdir(anomDir)   #changing to the local directory to run SHELXE (it doesn't like absolute paths as arguments if they are too long)

    ########## Now handle the file format for each input file (nothing to do if it is XDS, convert it if MTZ)

    #Choose an input file Root name for the SHELXE project

    # if "NAT" in inputFilesDic: 
    #     rootNameForSHELXC,extension=os.path.splitext(os.path.basename(inputFilesDic['NAT']))
    # elif "SAD" in inputFilesDic:
    #     rootNameForSHELXC,extension=os.path.splitext(os.path.basename(inputFilesDic['SAD']))
    # elif "PEAK" in inputFilesDic:  
    #     rootNameForSHELXC,extension=os.path.splitext(os.path.basename(inputFilesDic['PEAK']))
    # else:
    #     rootNameForSHELXC += "Arcimboldo"

    rootNameForSHELXC = rootAnom

    #Variables for file conversion
    hklout="none"

    #Going through each input file and converting to hkl if necessary
    #Store the converted types and file paths int inputFilesDic2
    inputFilesDic2={}

    for inputFileType,intputFilePath in inputFilesDic.items():  

        basename=os.path.basename(intputFilePath)
        fileName,extension = os.path.splitext(basename)

        if extension.lower()==".mtz":
            #In this case we have to convert to sca before running SHELXC
            scaout=mtz2sca(anomDir=anomDir, mtzFilePath=intputFilePath) #path to the converted sca file
            inputFilesDic2[inputFileType]=scaout

        elif format=="HKL": #XDS file, we need to generate an MTZ from it for direct input into Arcimboldo_Lite

            #convert to hkl with xdsconv
            #hklout=xds2hkl(anomDir=anomDir, HKLin=intputFilePath) NO NEED, shelxc recognizes XDS format directly

            #copy the XDS file into the anomDir directory
            shutil.copy(os.path.abspath(intputFilePath),anomDir)
            inputFilesDic2[inputFileType]=intputFilePath
            if inputFileType=='NAT': 
                #mtzout=xds2mtz(anomDir=anomDir, HKLin=intputFilePath, waveLength=waveLength, xtalname="XDScryst",dataname="native")
                pass

        else : #assumes hkl or sca file

            #copy the input file in the anomDir directory if not already present
            if not os.path.exists(os.path.join(anomDir,basename)):
                shutil.copy(os.path.abspath(intputFilePath),anomDir)
            inputFilesDic2[inputFileType]=intputFilePath


    ###############################CREATING THE .INS FILE
    INSfile=""

    #change to basenames
    inputFilesDic2={k:os.path.basename(y) for k,y in inputFilesDic2.items()}
    
    #Manage which mode is entered in for SHELXC
    if mode == "MRSAD" and "SAD" in inputFilesDic2:
        INSfile += "SAD %s\n"%inputFilesDic2["SAD"]

        if "NAT" in inputFilesDic2:
            INSfile += "NAT %s\n"%inputFilesDic2["NAT"]

    elif mode == "MRMAD":
        if "PEAK" in inputFilesDic2:
            INSfile += "PEAK %s\n"%inputFilesDic2["PEAK"]

            if "NAT" in inputFilesDic2:
                INSfile += "NAT %s\n"%inputFilesDic2["NAT"]

            if "INFL" in inputFilesDic2: #if inflection point file present
                INSfile += "INFL %s\n"%inputFilesDic2["INFL"]

            if "HREM" in inputFilesDic2: #if high energy remote file present (must have entered peak and inflection before)
                INSfile += "HREM %s\n"%inputFilesDic2["HREM"]

            if "LREM" in inputFilesDic2: #if high energy remote file present (must have entered peak and inflection before)
                INSfile += "LREM %s\n"%inputFilesDic2["LREM"]
        else:
            print("Error, MRMAD mode required but it seems that you haven't provided any PEAK file, quitting now.")
            sys.exit(1)

    elif mode == "MIR":
        print "MIR is not supported by SHELX, you can try SIR instead"
        return -1


    elif mode == "MIRAS":
        print "MIRAS is not supported by SHELX, you can try MAD or SIR instead"
        return -1

    elif mode == "SIR" and "NAT" in inputFilesDic2 and "SIR" in inputFilesDic2:
        INSfile += "NAT %s\n"%inputFilesDic2["NAT"]
        INSfile += "SIR %s\n"%inputFilesDic2["SIR"]

    elif mode == "SIRAS" and "NAT" in inputFilesDic and "SIRA" in inputFilesDic2:
        INSfile += "NAT %s\n"%inputFilesDic2["NAT"]
        INSfile += "SIRA %s\n"%iinputFilesDic2["SIRA"]

    elif mode == "RIP" and "BEFORE" in inputFilesDic2 and "AFTER" in inputFilesDic2:
        INSfile += "BEFORE %s\n"%inputFilesDic2["BEFORE"]
        INSfile += "AFTER %s\n"%inputFilesDic2["AFTER"]
        if "NAT" in inputFilesDic:
            INSfile += "NAT %s\n"%inputFilesDic2["NAT"]

    else:
        print("The mode you entered (%s) does not have the required dataset to work with"%mode)
        return -1



    #Common part of the INS file
    if waveLength>0:
        INSfile += "CELL %.4f %.3f %.3f %.3f %.3f %.3f %.3f \n"%(waveLength,cell[0],cell[1],cell[2],cell[3],cell[4],cell[5])
    else:
        INSfile += "CELL %.3f %.3f %.3f %.3f %.3f %.3f \n"%(cell[0],cell[1],cell[2],cell[3],cell[4],cell[5])

    INSfile += "SPAG %s\n"%unitCellTools.get_short_symbol_from_sg_number(spaceGroupNum)
    INSfile += "SFAC %s\n"%sfac
    INSfile += "FIND %d\n"%nsites
    INSfile += "NTRY %d\n"%ntry
    INSfile += "ESEL %.1f\n"%1.5
    if dsul>0:
        mind=3.5
        INSfile += "DSUL %d\n"%dsul

    if specialPos:
        INSfile += "MIND -%.1f \n"%mind
    else:
        INSfile += "MIND -%.1f -0.1\n"%mind

   # INSfile += "EOF"

    #Now write the ins file
    SHELXC_INP=open(os.path.join(anomDir,"shelxcins.inp"),'w')
    SHELXC_INP.write(INSfile)
    SHELXC_INP.close()

    
    #Launching the SHELXC job
    print("----> Preparing data files with SHELXC")
    shelxcCMD= SHELXC+" "+rootNameForSHELXC+" "+" < shelxcins.inp"
    launchProcess(shelxcCMD)
       
    #remove the XDS file that was copied in anomDir
    for fichier in inputFilesDic.values():
        toremove=os.path.join(anomDir,os.path.basename(fichier))
        try:
            os.remove(toremove)
        except:
            print("Warning: cannot remove %s"%toremove)

    #Go back to the initial directory
    print("Changing back to %s"%initialDir)
    os.chdir(initialDir)

    #SHELXC returns 3 files : myroot.hkl, myroot_fa.hkl and myroot_fa.ins, it is therefore convenient to return the string my_root_fa as well 
    #as the native and anomalous differences in a single dictionnary

    outPutNative=os.path.abspath(os.path.join(anomDir,rootNameForSHELXC+".hkl"))
    outPutDiff=os.path.abspath(os.path.join(anomDir,rootNameForSHELXC+"_fa.hkl"))
    outInsFile=os.path.abspath(os.path.join(anomDir,rootNameForSHELXC+"_fa.ins"))

    return {'rootName':rootNameForSHELXC+"_fa", 'native' : outPutNative, 'differences' : outPutDiff, 'insFile': outInsFile}


def checkAnomalousFiles(anomDir,rootName):
    """
    Checks the presence of the files output by shelxc i.e my_file.hkl my_file_fa.hkl my_file_fa.ins, check also the size
    """
    hkl= os.path.join(anomDir,rootName+'.hkl')
    hkl_fa= os.path.join(anomDir,rootName+'_fa.hkl')
    ins= os.path.join(anomDir,rootName+'_fa.ins')
    if filePresent(hkl) and filePresent(hkl_fa) and filePresent(ins):
        for fichier in (hkl_fa, hkl, ins):
            if os.path.getsize(fichier)==0:
                print("ERROR: File %s is empty!"%fichier)
                return False
        return True
    else:
        return False

def parseAnomalousParameters(configParserObject=None, ANOMDIR=None):
    """returns the anomalous parameters in the form of a dictionary anomDic to provide them to the different programs"""

    if configParserObject != None:
        Config=configParserObject

        #Parameters needed by startExpansion in shelxe_cycles 
        hkl_fa = Config.get("ANOMALOUS", "hkl_fa_path")
        ins_fa = Config.get("ANOMALOUS", "ins_fa_path")
        expphasing = Config.get("ANOMALOUS", "expphasing")  #NS ANOM, expphasing can be 'MRSAD', 'MRMAD', 'SIR', 'SIRAS', 'RIP' etc 
        nsites_expected=Config.getint("ANOMALOUS", "nsites_expected")
        sfac = Config.get("ANOMALOUS", "sfac")
        ha_present_in_native=Config.getboolean("ANOMALOUS", "ha_present_in_native")
        recycle_ha=Config.getboolean("ANOMALOUS", "recycle_ha")        #To recycle heavy atoms between cycles of autotracing
        minusz=Config.getboolean("ANOMALOUS", "minusz")        #To use the -z(+number of sites) option in shelxe
        minusz_zero=Config.getboolean("ANOMALOUS", "minusz_zero")        #To use the -z0 (special for cross frourier MRSAD)
        minuso=Config.getboolean("ANOMALOUS", "minuso")        #To use the -z(+number of sites) option in shelxe
        evaluateAnom=Config.getboolean("ANOMALOUS", "evaluateAnom")        #To use scoring function (i.e distance ha-Cbeta, pattersonmatch etc) inside evaluateExp
        patterson=Config.getboolean("ANOMALOUS", "patterson")        #To use scoring function (i.e distance ha-Cbeta, pattersonmatch etc) inside evaluateExp
        referenceHA=Config.get("ANOMALOUS", "referenceHA")
        hardFilter=Config.getboolean("ANOMALOUS", "hardFilter")             # to retain solutions that have not been either eliminated by 9.5EXP or 9_exp evaluateEcpCC in Borges, if False it will discard only solutions that have been eliminated in both
        n_HA_refine_cycles=Config.getint("ANOMALOUS", "n_HA_refine_cycles") # prior to expansion, heavy atoms get refined during n cycles without autotracing
        ha_substructure= Config.get("ANOMALOUS", "ha_substructure") #         ha substructure solution provided by the user 
        hres_cutoff= Config.getfloat("ANOMALOUS", "hres_cutoff")

        #Parameters which are not needed by StartExpansion but just by shelxc to write the ins file:
        rootAnom = Config.get("ANOMALOUS", "rootAnom")            #root file name for the anomalous files ex: xx for xx.hkl, xx_fa.hkl, xx.ins (shlxanom by default) 
        specialPos= Config.getboolean("ANOMALOUS", "specialPos")        #allow searching ha on special positions
        dsul=Config.getint("ANOMALOUS", "dsul")

        #default setting for some anomalous parameters
        hkl_fa= None if hkl_fa.lower() == 'none' else os.path.abspath(hkl_fa)
        ins_fa= None if ins_fa.lower() == 'none' else os.path.abspath(ins_fa)
        expphasing = None if expphasing.lower() == 'none' else expphasing.upper() #NS ANOM: can be SAD, MAD, SIR,SIRAS, RIP, PHASER (when a substructure from shelxd is provided), also MRSAD and PHASER (the latter for working with DANO/SIGDANO) 
        sfac = None if sfac.lower() == 'none' else sfac.upper()
        rootAnom= 'shlxanom' if rootAnom.lower() == 'none' else rootAnom.lower()
        fragAnom=True if expphasing != None else False                        ##the fraganom bool switches on the ANOMALOUS parameter on but also is used in startExpansion to know whether we are in the 'initCC' phase or in the cycles of shelxe expansion
        referenceHA=None if referenceHA.lower() == 'none' else referenceHA #list of (lists) fractional coordinates provided for reference
        ha_substructure=None if ha_substructure.lower() == 'none' else os.path.abspath(os.path.normpath(ha_substructure))


        #parameter for Lite to specify from which cycle onwards we want to filter solutions
        filterLiteFromFragNumber = Config.getint("ANOMALOUS", "filterLiteFromFragNumber") 

        #Experience type parameters
        anomFileTypes=("nat_path", "peak_path", "infl_path", "hrem_path", "lrem_path", "sir_path", "sira_path", "before_path", "after_path")
        otherAnomParamDic={'rootAnom':rootAnom, 'specialPos': specialPos, 'dsul':dsul, 'patterson': patterson, 'hardFilter': hardFilter, 'filterLiteFromFragNumber':filterLiteFromFragNumber, 'hres_cutoff': hres_cutoff}

        #populating dictionary input AnomFileDic
        for parametre in anomFileTypes:
            file_path=Config.get("ANOMALOUS", parametre)
            print("%s: %s"%(parametre,file_path))
            

            if file_path.lower() != 'none' and os.path.exists(os.path.abspath(file_path)): #check that the file path provided is valid
                abbreviation= parametre.split('_')[0].upper()                              #ex: PEAK, INFL etc 
                otherAnomParamDic[abbreviation]=os.path.abspath(file_path)

            elif file_path.lower() != 'none' and not os.path.exists(os.path.abspath(file_path)): #Stop if one of the provided file paths is wrong
                print("ERROR: the provided file %s for %s doesn't exist or is not readable (put 'none' if there isn't any), quitting now"%(file_path,parametre))
                return False

        #return the parameters for startExpansion in a dictionary:
        startExpAnomDic={'hkl_fa':hkl_fa, 'ins_fa':ins_fa,'expphasing':expphasing,'nsites_expected':nsites_expected,'sfac':sfac,'ha_present_in_native':ha_present_in_native,'recycle_ha':recycle_ha,'minusz':minusz, 'minusz_zero': minusz_zero, 'minuso' : minuso, 'ANOMDIR':ANOMDIR, 'evaluateAnom': evaluateAnom, 'referenceHA': referenceHA, 'n_HA_refine_cycles':n_HA_refine_cycles, 'ha_substructure': ha_substructure,'patt_referenceHA': None}
        

        return startExpAnomDic, otherAnomParamDic, fragAnom      #the fraganom bool switches on the ANOMALOUS parameter in Lite
    else:
        return None, None, False

def updateAnomParamDic(hkl=None, mtz=None, current_directory=None, cell_dim=None, sg_number=1,otherAnomParamDic=None, startExpAnomDic=None): #cell_dim=None, sg_number=None, expphasing=None, hkl_fa=None, ins_fa= None, sfac= None, nsites_expected=None, ha_present_in_native= None, recycle_ha=0, minusz=False, minusz_zero=False, minuso=False,  ANOMDIR=None, evaluateAnom=False):
    """In case experimental phasing is required, checks the presence of the files, set default parameters etc"""
    #have to develop here to adapt to the mode (i.e provide a dictionary with the anomalous files)

    rootAnom=otherAnomParamDic['rootAnom']
    specialPos=otherAnomParamDic['specialPos']
    dsul=otherAnomParamDic['dsul']
    if cell_dim is not None:
        cell_dim=[float(x) for x in cell_dim] # In case they are entered as string
    expphasing= startExpAnomDic['expphasing']
    hkl_fa= startExpAnomDic['hkl_fa']
    ins_fa= startExpAnomDic['ins_fa']
    sfac= startExpAnomDic['sfac']
    nsites_expected= startExpAnomDic['nsites_expected']
    ha_present_in_native= startExpAnomDic['ha_present_in_native']
    recycle_ha= startExpAnomDic['recycle_ha']
    minusz= startExpAnomDic['minusz']
    minusz_zero= startExpAnomDic['minusz_zero']
    minuso= startExpAnomDic['minuso']
    ANOMDIR= startExpAnomDic['ANOMDIR']
    evaluateAnom= startExpAnomDic['evaluateAnom']
    referenceHA=startExpAnomDic['referenceHA']
    hres_cutoff= otherAnomParamDic['hres_cutoff']

    # If a substructure known to be good is provided (only for comparison with sites found from Cross Fourier)
    if referenceHA is not None:
        startExpAnomDic['referenceHA']= parseReferenceHAFile(referenceHA, sfac=sfac, unitCellParam = cell_dim)
        print("Calculating Patterson from the reference structure provided")
        startExpAnomDic['patt_referenceHA'] = pattersonPeaksFromPDB(pdbfilePath=None, fracCoord=startExpAnomDic['referenceHA'], unitCellParam=cell_dim, sfac=sfac, spaceGroupNum=sg_number, writePDB=False, harker=True)
        if referenceHA == []:
            print("WARNING: the provided reference HA file doesn't contain any atoms!!")
            referenceHA=None

    #copy the required hkl , hkl_fa and ins_fa files to ANOMLIB
    if ANOMDIR is not None:
        if not os.path.exists(ANOMDIR):
            try:
                os.makedirs(ANOMDIR)

            except OSError:
                return False
    else:
        print("ANOMDIR is None or cannot be created")
        return False


    # If a ha substructure is provided, convert it (if different from shelx format and place it into the ANOMALOUS directory)
    if startExpAnomDic['ha_substructure'] is not None:
        parseReferenceHAFile(startExpAnomDic['ha_substructure'], sfac=sfac, unitCellParam=cell_dim, printmsg=True, writeRES=True, outputFile=os.path.join(ANOMDIR,'ha_substructure.res'), sgnum=sg_number)
        startExpAnomDic['ha_substructure']= os.path.join(ANOMDIR,'ha_substructure.res')

    try:
        shutil.copyfile(hkl,os.path.join(ANOMDIR,rootAnom+'.hkl'))                    #copying the hkl file to ANOMDIR and the hkl_fa if present (will be overwritten if shelxc is used afterwards)
        if filePresent(hkl_fa):
            try:
                shutil.copyfile(hkl_fa,os.path.join(ANOMDIR,rootAnom+'_fa.hkl'))
                hkl_fa=os.path.join(ANOMDIR,rootAnom+'_fa.hkl')
                startExpAnomDic['hkl_fa']=hkl_fa

            except:
                print("ERROR, cannot copy the hkl_fa file %s to %s"%(hkl_fa,ANOMDIR))
                return False

        if filePresent(ins_fa):
            try:
                shutil.copyfile(ins_fa,os.path.join(ANOMDIR,rootAnom+'_fa.ins'))
                ins_fa=os.path.join(ANOMDIR,rootAnom+'_fa.ins')
                startExpAnomDic['ins_fa']=ins_fa
            except:
                print("ERROR, cannot copy the ins_fa file %s to %s"%(ins_fa,ANOMDIR))
                return False
    except:
        print("Error","cannot transfer the hkl file %s to %s, STOPPING NOW"%(hkl,ANOMDIR))
        return False

    print("\n-->ANOMALOUS SIGNAL HANDLING requested, the provided parameters are: ")
    print("mode: %s, hkl_fa: %s, ins_fa: %s,nsites_expected: %s, ha_present_in_native: %s, sfac: %s, recycle_ha: %s, -z option in shelxe: %s, -o option in shelxe %s, evaluateAnom: %s"%(expphasing, hkl_fa, ins_fa,nsites_expected, ha_present_in_native,sfac, recycle_ha, minusz, minuso,evaluateAnom))
    if minusz_zero:
        print("-z0 option for shelxe activated (CROSS- FOURIER")


    #---------------generate the anomalous differences (hkl_fa) if not provided
    if not filePresent(hkl_fa) or not filePresent(ins_fa) and (expphasing == "MRSAD" or expphasing == "MRMAD"):  #Other modes than MRSAD will be accessible through ARCIMBOLDO-ANOM (to develop)

        print("REMARK: absent or bad hkl_fa or ins_fa file provided in the [ANOMALOUS] section, attempting to create those with SHELXC from the provided input files")
        if not otherAnomParamDic or not anomInfo(expphasing,otherAnomParamDic): #if no anomalous files provided (empty dictionary inputAnomFileDic), use the input mtz which must contain I(+/-) SIGI(+/-) since it will be converted to sca by mtz2sca)
            print("REMARK: Preparing the hkl_fa file from the input mtz file since not enough information was provided for mode %s in the [ANOMALOUS] section"%expphasing)
            otherAnomParamDic= {"SAD":mtz}                                         # or if there is not sufficient info. in the provided files to generate the hkl_fa                

        #prepare the hkl_fa file with the relevant files
        pathParameters = ['PEAK', 'INFL', 'HREM', ]
        inputFilesDic= {k:v  for k,v in otherAnomParamDic.items() if k in pathParameters}
        hkl_faDic=prepareWithSHELXC(mode=expphasing, format='MTZ', workingDirectory=current_directory,inputFilesDic=inputFilesDic,cell=cell_dim,spaceGroupNum=sg_number, sfac=sfac, specialPos=specialPos, nsites=nsites_expected,dsul=dsul,rootAnom=rootAnom)

        if hkl_faDic == -1:
            print("***FATAL ERROR: cannot create the ANOMFILEs directory for storing anomalous scattering files")
            return False
        else:
            hkl_fa=hkl_faDic['differences']
            ins_fa=hkl_faDic['insFile']
            startExpAnomDic['hkl_fa']=hkl_fa
            startExpAnomDic['ins_fa']=ins_fa
            print("\nREMARK: The hkl_fa file has been created as: %s"%hkl_fa)

    #Checking that all the required anomalous files are present before going furtherafter shelxc or not, including that their size is not zero
    if not checkAnomalousFiles(ANOMDIR,rootAnom):
        print("\n---ERROR: Some of the files required for the anomalous signal treatment are not available in %s"%ANOMDIR)
        print("---Files: %s.hkl, %s_fa.hkl and %s_fa.ins file from shelxc are not all present in %s"%(rootAnom, rootAnom, rootAnom, ANOMDIR))
        return False

    #Truncating the resolution of the fa file if needed
    if hres_cutoff > 0:
        print("REMARK : You requested the anomalous data to be truncated at {}A".format(hres_cutoff))
        startExpAnomDic['hkl_fa']=truncate_fa(hres_cutoff=hres_cutoff, pathTo_hkl_file=hkl_fa, unitCellParam=cell_dim)

    #Setting default values
    if sfac is None:
        print("***WARNING, you haven't set any type of scatterer for your experimental phasing in your .bor file (keyword 'sfac' in GENERAL), default set to Selenium")
        sfac='SE'
        startExpAnomDic['sfac']=sfac

    if nsites_expected == 0:
        print("***WARNING, you haven't set the number of expected sites in your .bor file (keyword 'nsites_expected' in GENERAL), default set to 10")
        nsites_expected= 10
        startExpAnomDic['nsites_expected']=nsites_expected

    #Updating the startExpAnom  dictionary to easily pass it to the startExpansion function
    return startExpAnomDic


def correct_SFAC_in_SHELXD_ins(insFile, sfac='SE'):
    """
    correct the SHELXD ins file with the correct type of scatterer before passing the file to either shelxd or shelxe
    ACTUALLY NOT NEEDED...
    """

    insfile=os.path.abspath(insFile)
    directory=os.path.dirname(insfile)
    tmpOut=os.path.join(directory,'tmp.ins')

    outputHandle=open(tmpOut,'w')

    sfac_re=re.compile(r"^SFAC")
    with open(insfile,'r') as f:
        for line in f:
            if sfac_re.match(line):
                outputHandle.write("SFAC %s\n"%sfac.upper())
            else:
                outputHandle.write(line)

    outputHandle.close()
    shutil.move(tmpOut,insfile)         #overrides the input .ins file

def launchSHELXD(workingDirectory="/path/to/workingDirectory",mode="SAD",inputFileRoot="xx_fa",ntry=100 ):
    """
    Launch the subtructure search with SHELXD, outputs a filePath to the best solution found (PDB file) and the CCALL and CCWEAK
    to see wether it is worth pursuing

    The search can be done in VARIOUS MODES, SAD, MAD, SIRAS, maybe even RIP

    """

    #Create a directory to handle the anomalous files
    anomDir=os.path.join(workingDirectory,"ANOMFILES")
    if not os.path.exists(anomDir):
        try:
            os.makedirs(anomDir)

        except OSError:
            print("Error","Cannot create directory %s for handling anomalous data, STOPPING NOW"%anomDir)
            sys.exit(1)

    #Change directory to this ANOMFILE (shelx programs don't like absolute path due to limited number of characters allowed)
#    initialDir=os.path.dirname(os.path.realpath(sys.argv[0]))
    initialDir=os.getcwd()
    print("Initial directory: %s"%initialDir)
    print("Changing temporarily to %s"%anomDir)
    os.chdir(anomDir)   #changing to the local directory to run SHELXE (it doesn't like absolute paths as arguments if they are too long)


    #output variables
    pathToSubstructureRES=""
    pathToSubstructurePDB=""
    CCALL=0
    CCWEAK=0
    CFOM=0

    #Launch the shelxd command from what was prepared by shelxc
    shelxdCMD=SHELXD+" "+inputFileRoot 
    print("Performing %d trials with shelxd, please be patient..."%ntry)
    launchProcess(shelxdCMD)

    #Parse CCALL and CCWEAK
    #Typically this corresponds to the first line of the file
    #REM Best SHELXD solution:   CC 38.75   CC(weak) 17.67   CFOM  56.42

    CC_re = re.compile(r"^REM Best SHELXD solution:\s+CC\s+([.\d]+)\s+CC\(weak\)\s+([.\d]+)\s+CFOM\s+([.\d]+)") #regular expression to catch CCALL and CCWEAK in the res file of the best shelxd solution
    with open(os.path.join(anomDir,inputFileRoot+'.res'),'r') as resfile:
        for line in resfile:
            m=CC_re.match(line)
            if m:
                CCALL=m.group(1)
                CCWEAK=m.group(2)
                CFOM=m.group(3)
                break


    #Go back to the initial directory
    print("Changing back to %s"%initialDir)
    os.chdir(initialDir)

    if CCALL <30:
        print("WARNING: your solution has a CCALL under 30%, your subtructure might be wrong")

    print("Best solution from SHELXD:")
    print("CCALL: %s, CCWEAK: %s, CFOM: %s"%(CCALL,CCWEAK,CFOM))
    return pathToSubstructureRES, pathToSubstructurePDB, CCALL, CCWEAK, CFOM

def removeHETATMfromPDB(pathToPDB, override=False):
    """Primarily intended to remove the heavy atoms that have been put in a pdb by shelxe for the next cycle of MRSAD,
       the override option keeps the same file name, whether in the same directory or not.
     """
    pathToPDB=os.path.abspath(pathToPDB)
    outputDir=os.path.dirname(pathToPDB)
    fileName, ext= os.path.splitext(os.path.basename(pathToPDB))
    outputPDB=os.path.join(outputDir,fileName+'_stripped.pdb')

    atomLine=re.compile(r"^HETATM")

    try:
        outPutFile=open(outputPDB,'w')

    except:
        print("\nERROR: %s cannot be opened with writing permissions!\n"%outputPDB)
        return -1

    with open(pathToPDB,'r') as f:
        for line in f:
            if not atomLine.match(line):
                outPutFile.write(line)

    outPutFile.close()
    if override:
        tmp=os.path.join(outputDir,fileName+ext)
        shutil.move(outputPDB,tmp)
        outputPDB=tmp

    return outputPDB

def checksEmptyHAT(pathToHATfile, sfac="SE"):
    """ Checks that a .hat or .res file has some ATOM records before the END record, returns TRUE if no atoms (hat empty)"""
    pathToHATfile = os.path.abspath(pathToHATfile)
    sfac=sfac.upper()

    if os.path.exists(pathToHATfile):
        notAtoms=('TITL','LATT','SYMM','SFAC','UNIT','HKLF')
        with open(pathToHATfile,'r') as hatfile:       
            for line in hatfile:
                atomTag=True
                line=line.upper()
                for keyw in notAtoms:     #checks that the current line doesn't start with one of the keywords from notAtoms.
                    if line.startswith(keyw):
                        atomTag=False
                        break
                if atomTag and line.startswith(sfac):
                    return False               # If an atom record is present before END, then the file is not empty
                elif line.startswith('END'):   # stop at END anyway
                    break
    else:
        print("WARNING, (function checksEmptyHAT), file %s does not exist"%pathToHATfile)
    return True


def hat2pdb(pathToHATfile, outputDir=".",sfac="SE", unitCellParam=[10,10,10,90,90,90], spaceGroupNum=1, znum=1,outputName=None, belowOne=False):
    """
    converts shelxe HAT heavy atoms format to pdb

    """
    outputDir=os.path.abspath(outputDir)
    pathToHATfile=os.path.abspath(os.path.normpath(pathToHATfile))
    #Create a directory to handle the anomalous files
    if not os.path.exists(outputDir):
        try:
            os.makedirs(outputDir)

        except OSError:
            print("Error","Cannot create directory %s for handling anomalous data, STOPPING NOW"%outputDir)
            return False

    absDir=os.path.dirname(os.path.abspath(pathToHATfile))
    rootName,ext=os.path.splitext(os.path.basename(pathToHATfile))
    if outputName is None:
        outputName = os.path.abspath(os.path.join(outputDir,rootName+"_hat.pdb"))
    else:
        outputName = os.path.abspath(os.path.join(outputDir,outputName))

    print("\nREMARK: hat2pdb, creating pdb file %s from %s"%(outputName, pathToHATfile))
    notAtoms=('TITL','LATT','SYMM','SFAC','UNIT','HKLF')

    sfac2="  "    #trailing characters of atom name (left justified in columns 15-16), whereas sfac is right-justified in columns 13-14
    if len(sfac)>2:
        sfac2=sfac[2:3]
    resname="HAT"
    chainID=' '
    #-----regular expressions
    pdbOut=open(outputName,'w')
    #Writes the crystcard in the output pdb
    if isinstance(spaceGroupNum,int) or isinstance(spaceGroupNum,float):
        sg=unitCellTools.get_full_symbol_from_sg_number(spaceGroupNum)  #space group full HM symbol
    else:
        sg=spaceGroupNum

    #pdbOut.write("CRYST1%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f %-11s%4d\n"%(unitCellParam[0],unitCellParam[1],unitCellParam[2],unitCellParam[3],unitCellParam[4],unitCellParam[5], sg, znum))
    pdbOut.write(unitCellTools.writeCRYSTCARDintoPDB(*unitCellParam, sgsymbol=sg))

    #Note, we need later to switch to orthogonal coordinates from the fractional ones, get the orthogonalization matrix
    omat=unitCellTools.Omat(*unitCellParam)
    coordFrac=np.empty([1,3])                  #the array provided is the shape (one line, three columns), it generates a random coordinates vector
    occ=[]

    atomnum=1
    #Opens the input shelxe .hat file
    with open(pathToHATfile,'r') as hatfile:       
        for line in hatfile:
            line=line.upper()         # Make it case-insensitive
            atomTag=True
            for keyw in notAtoms:     #checks that the current line doesn't start with one of the keywords from notAtoms.
                if line.startswith(keyw):
                    atomTag=False   #To continue to next line
                    break

            if line.startswith('END'):   #end the line reading when reaching the 'END' keyword
                break

            if atomTag and line.startswith(sfac.upper()):                 #If the line corresponds indeed to an atom record
                m=atom_re.match(line)   #match to the regular expression capturing an atom record
                if m:
                    #print("LINE:"+line)
                    xfrac=float(m.group(1))
                    yfrac=float(m.group(2))
                    zfrac=float(m.group(3))
                    occ.append(float(m.group(4)))
                    #bfact=m.group(5)    #replace the b-factor by 20 for the moment
                    #bfact=20

                    #conversion to orthogonal coordinates:
                    if atomnum==1:
                        coordFrac[0,:] = [xfrac, yfrac, zfrac]      #replace the first (random vector by the fractional coord. of the first atom found)
                    else:
                        coordFrac=np.append(coordFrac,[[xfrac,yfrac,zfrac]],axis=0) #add the other frac coord 
                    atomnum += 1


    #Convert the fractional coordinates to orthogonal
    coordOrth=unitCellTools.frac2Ortho(omat,coordFrac, belowOne=belowOne)

    #Writes the atom record line in the output pdb
    for i,xyz in enumerate(coordOrth):
        xOrth=xyz[0]
        yOrth=xyz[1]
        zOrth=xyz[2]
        pdbOut.write("HETATM%5s %2s%-2s %3s %1s%4s    %8.3f%8.3f%8.3f%6.2f%6.2f          %2s  \n"%(str(i+1),sfac,sfac2,resname,chainID,str(i+1),xOrth,yOrth,zOrth,occ[i],20,sfac))
                    
    pdbOut.write("END\n")
    pdbOut.close()
    return outputName

def parseReferenceHAFile(inputFile, sfac='SE', unitCellParam=(10, 10, 10, 90, 90, 90), printmsg=True, writeRES=False, outputFile=None, sgnum=1):
    """ A reference heavy atom file can be provided either as a pdb/pda file or as a .res or .hat file. 
    The function parses the coordinates, if it is a PDB file, the orthogonal coordinates a first converted to fractional
    it returns an array of coordinates of the type: [[0.5, 0.6, 0.7], [0.1, 0.9, 0.2]] 
    """

    unitCellParam=[float(x) for x in unitCellParam]
    inputFile=os.path.abspath(os.path.normpath(inputFile))
    finalCoord=[]


    if os.path.exists(inputFile):
        try:
            if inputFile.endswith('.pdb') or inputFile.endswith('.pda') or inputFile.endswith('.PDB') or inputFile.endswith('.PDA'):

                # Store the orthogonal coordinates in an numpy n x 3 array 
                _, orthCoord, _ = extractCoordinatesFromPDB(pathToPDBfile=inputFile)


                # Get the deothogonalization matrix
                deOmat= unitCellTools.deOmat(*unitCellParam)

                # Convert the array to fractional coordinates between 0 and 1
                fracCoord= unitCellTools.ortho2Frac(deOmat, orthCoord, belowOne=True)

                for v in fracCoord:
                    finalCoord.append(list(v))


            elif inputFile.endswith('.hat') or inputFile.endswith('.res') or inputFile.endswith('.HAT') or inputFile.endswith('.RES'):
                if not writeRES:
                    notAtoms=('TITL','LATT','SYMM','SFAC','UNIT','HKLF')
                    with open(inputFile,'r') as hatfile:       
                        for line in hatfile:
                            line=line.upper()         # Make it case-insensitive
                            atomTag=True
                            for keyw in notAtoms:     #checks that the current line doesn't start with one of the keywords from notAtoms.
                                if line.startswith(keyw):
                                    atomTag=False   #To continue to next line
                                    break

                            if line.startswith('END'):   #end the line reading when reaching the 'END' keyword
                                break

                            if atomTag and line.startswith(sfac.upper()):                 #If the line corresponds indeed to an atom record
                                m=atom_re.match(line)   #match to the regular expression capturing an atom record
                                if m:
                                    #print("LINE:"+line)
                                    xfrac=float(m.group(1))
                                    yfrac=float(m.group(2))
                                    zfrac=float(m.group(3))

                                    finalCoord.append([xfrac, yfrac, zfrac])

            # Otherwise assumes a free format with one set of fracional coordinates per line
            else:
                with open(inputFile,'r') as f:
                    for line in f:
                        if regxpFreetxt.match(line):
                            xfrac, yfrac, zfrac = line.split()
                            finalCoord.append([float(xfrac), float(yfrac), float(zfrac)])

            if printmsg:
                print("\nREMARK: Reference ha coordinates provided: %s\n"%finalCoord)

            if writeRES and outputFile:
                
                print("REMARK: writing res file from input ha coordinate as {}".format(outputFile))
                if inputFile.endswith('.res') or outputFile.endswith('.hat') or inputFile.endswith('.HAT') or inputFile.endswith('.RES'):
                    shutil.copyfile(inputFile, outputFile)
                else:
                    # Getting the relevant information from the space group dictionnary
                    latt_symm = unitCellTools.lines_for_writing_res(sgnum)

                    with open(outputFile,'w') as f:
                        f.write("TITL Provided HA file for Arcimboldo anomalous\n")
                        f.write("CELL 1.0000 {:.3f}    {:.3f}    {:.3f}    {:.3f}    {:.3f}    {:.3f}\n".format(*unitCellParam))
                        f.write(latt_symm)
                        f.write("UNIT 100\n")
                        for i,atom in enumerate(finalCoord):
                            f.write("{}{:03}  1  {}  {}  {}  1.0000  0.2\n".format(sfac.upper(), i, atom[0], atom[1], atom[2]))
                        f.write("HKLF 3\n")
                        f.write("END\n")

            return finalCoord

        except Exception as e:
            print("WARNING, error while parsing open the reference ha file %s"%inputFile)
            print(e)

    else:
        print("WARNING, cannot open the reference ha file %s"%inputFile)
        return []

def prepareBOR(BORLOW):
    """
    prepare the BOR file that will be sent to Arcimboldo lite

    """
    pass

def writeCOOTscript(outputDir,spaceGroup="P 1 2 1", unitCell=['10','10','10','90','90','90']):
    """ Writes a coot script that will be loaded automatically when launching COOT, reading the best trace, heavy atoms, and the two corresponding phs fiels with nice adjustments"""

    outputFile=open(os.path.join(outputDir,"0-coot.state.scm"),'w')
    toWrite="""
(handle-read-draw-molecule "best_ha.pdb")
(set-molecule-bonds-colour-map-rotation 2 63.00)
(set-draw-hydrogens 2 1)
(handle-read-draw-molecule "best.pdb")
(set-molecule-bonds-colour-map-rotation 0 21.00)
(set-draw-hydrogens 0 1)
(read-phs-and-make-map-using-cell-symm "best.phs" "%s" %s %s %s %s %s %s)
(set-last-map-colour  0.20  0.50  0.70)
(set-last-map-contour-level-by-sigma 1.0)
(set-last-map-sigma-step  0.10)
(read-phs-and-make-map-using-cell-symm "best_ha.phs" "%s" %s %s %s %s %s %s)
(set-last-map-colour  0.87  0.72  0.18)
(set-last-map-contour-level-by-sigma 4.0)
(set-last-map-sigma-step  0.10)
(set-show-unit-cell 0 1)
(set-matrix 60.00)
(set-show-symmetry-master 1)
(set-symmetry-size 25.00)
            """%(spaceGroup,unitCell[0], unitCell[1], unitCell[2], unitCell[3], unitCell[4], unitCell[5], spaceGroup, unitCell[0], unitCell[1], unitCell[2], unitCell[3], unitCell[4], unitCell[5])
    outputFile.write(toWrite)
    outputFile.close()

def replaceATOMrec(inputLine="", replaceDic={"resName": "ALA"}):
    """Easily replace a string element from an ATOM record in a ATOM line from a pdb file"""

    

    possibleArguments = (
    ("ATOM", 1, "{:>6}"), ("serial", 2, "{:>5}"), ("dummy", 3, ""), ("atomName", 4, "{:>4}"), ("altLoc", 5, "{:>1}"),
    ("resName", 6, "{:>3}"), ("dummy", 7, ""), ("chainID", 8, "{:>1}"), ("seqnum", 9, "{:4d}"),
    ("insertionCode", 10, "{:>1}"), ("dummy", 11, ""), ("x", 12, "{:8.3f}"), ("y", 13, "{:8.3f}"), ("z", 14, "{:8.3f}"),
    ("occupancy", 15, "{:6.2f}"), ("bfact", 16, "{:6.2f}"), ("dummy", 17, ""), ("element", 18, "{:>2}"))

    # generating the substitution line

    subLine = ""
    for arg in possibleArguments:
        if arg[0] in replaceDic.keys():
            subLine += arg[2].format(replaceDic[arg[0]])
        else:
            subLine += "\\g<" + str(arg[1]) + ">"

    # print "SUBLINE IS:"+subLine
    # Nowperforming the substitution
    out = regexprATOM2.sub(subLine, inputLine)
    return out

#PDB-oriented functions
def extractCoordinatesFromPDB(pathToPDBfile=None, regularExprAtom=regexprATOM2):
    """Extracts coordinates from a pdb file and outputs them in a numpy n x 3 array"""

    PDB1orthCoord=np.empty((0,3),float)   #empty array to store the coordinates the first PDB
    elemTab=[]                            #capturing also the elemt at position x,z,z to know the number of electrons
    if pathToPDBfile is not None and os.path.exists(pathToPDBfile):
        natom=0
        with open(pathToPDBfile,'r') as f:
            for line in f:
                m = regularExprAtom.match(line)
                if m:
                    natom+=1

                    #atom coordinates
                    x=float(m.group(12))
                    y=float(m.group(13))
                    z=float(m.group(14))
                    elem=m.group(18).strip().upper()
               
                    # Add lines to the current coordinates
                    PDB1orthCoord=np.append(PDB1orthCoord,np.array([[x,y,z]]),axis=0)
                    elemTab.append(elem)

        print("----- %s atom coordinates recorded from %s.-----\n"%(natom,pathToPDBfile))
        return natom, PDB1orthCoord, elemTab             # n x 3 numpy array of orthogonal coordinates
    else:
        print("Problem with your extracting coordinates from PDB file %s, the file does not exist or is not accessible"%pathToPDBfile)
        return None


def compactHA(pdbfilePath,pdbfilePath2, override=False):
    """
    calculates for each atom form PDB2 (heavy atom) which symmetric is the closest to the protein. It tries all equivalent positions in fractional coordinates

    pdbfilePath: (string) path to the protein PDB file (ex: "/my/file.pdb")
    pdbfilePath2: (string) path to the heavy atom PDB file (ex: "/my/file_ha.pdb"), THIS MUST BE A PDB OR PDB FILE, NOT HA
    override: (boolean) the outputfile heavy atom file overrides the input file (pdbfilePath2)
    """

    # PDBout
    pdbfilePath=os.path.abspath(pdbfilePath)
    _,ext=os.path.splitext(os.path.basename(pdbfilePath))     #myfile    .pdb
    if ext.lower() not in ('.pdb','.pda','.ent'):    #If a non-pdb file has been entered
        print("Problem: %s is not a valid PDB file, skipping."%pdbfilePath)
        return

    pdbfilePath2=os.path.abspath(pdbfilePath2)
    outputDir=os.path.dirname(pdbfilePath2)
    fileOutName=os.path.basename(pdbfilePath2)    #myfile.pdb
    fileOutName,ext2=os.path.splitext(fileOutName)     #myfile    .pdb

    if ext2.lower() not in ('.pdb','.pda','.ent'):    #If a non-pdb file has been entered
        print("Problem: %s is not a valid PDB file, skipping."%pdbfilePath2)
        return
    else:
        TMPoutputName=fileOutName + "_COMPACT.pdb"

    if os.path.exists(pdbfilePath) and os.path.exists(pdbfilePath2):

        # Extract orthogonal coordinates from the protein PDB input file 
        natom, PDB1orthCoord, _ =extractCoordinatesFromPDB(pdbfilePath, regularExprAtom=regexprATOMprot)   #empty array to store the coordinates the first PDB      

        #Unit cell parameters and space group
        unitCellParam=unitCellTools.extract_cryst_card_pdb(pdbfilePath)
        unitCellParam2=unitCellTools.extract_cryst_card_pdb(pdbfilePath2)


        if unitCellParam[0:7] != unitCellParam2[0:7] :     #Don't check the last (Z) number of the crystcard
            print("WARNING: the unit cell parameters for these two PDB are different, they must have the same CRYSTCARD")
            print("CRYSTCARD1: "+str(unitCellParam[0:7]))
            print("CRYSTCARD2: "+str(unitCellParam2[0:7]))
        else:
            print("CRYSTCARD: "+str(unitCellParam[0:7]))

        # Retrieve crystallographic parameters from the PDB crystcard, 
        # calculate orthogonalization and deorth. matrix to switch between orthogonal and fractional coordinates
        sgnum=unitCellTools.get_space_group_number_from_symbol(unitCellParam[6])
        symops=unitCellTools.get_symops_from_sg_dictionary(sgnum)
        print("(%s symmetry operation(s) found for space group %s (in addition to identity)\n"%(str(len(symops.keys()) - 1 ),unitCellParam[6]))
        for ope in symops.items():
            print("%s: %s"%(ope[0], ope[1])) 
        Omat=unitCellTools.Omat(*unitCellParam[0:6])
        deOmat=unitCellTools.deOmat(*unitCellParam[0:6])
        Gmat=unitCellTools.Gmat(*unitCellParam[0:6])


        # output file
        outputFile=open(os.path.join(outputDir,TMPoutputName),'w')

        # writing the ha CRYSTCARD to the output file
        outputFile.write(unitCellTools.writeCRYSTCARDintoPDB(*unitCellParam2[0:7]))
           
        print("Compacting atoms from file %s around PDB file %s, please wait.."%(pdbfilePath2,pdbfilePath))

        PDB1FracCoord=unitCellTools.ortho2Frac(deOmat,PDB1orthCoord, belowOne=True)   #fractional coordinates of the PDB, once the centre of mass has been taken out

        # Now calculate the minimal distance to the protein in fractional coordinates (kept between zero and one)
        # for each atom of PDB2 (supposed to be heavy atom file) 
        nHA=0
        pdblines=[]
        haFracCoord=[]
        for line in open(pdbfilePath2):
            m = regexprATOM.match(line)
            if m:
                nHA +=1
                #atom coordinates
                x=float(m.group(4))
                y=float(m.group(5))
                z=float(m.group(6))

                matFrac=unitCellTools.ortho2Frac(deOmat,np.array([[x,y,z]]), belowOne=True)[0]     #fractional coordinates od the current heavy atom

                haFracCoord.append(np.array([matFrac[0], matFrac[1], matFrac[2]]))

                # keep track of the current PDB heavy atom line to modify it in the end
                pdblines.append(line)                                     

##########################################
        #Going through all heavy atoms
        for i, ha in enumerate(haFracCoord):
            symmetrics=[]

            # Generate symmetrics for this heavy atom, keep fractional coordinates between one and minus one
            for operationNum in symops:
                operation=symops[operationNum]
                currentsymm=unitCellTools.rotoTranslateFracCoord(ha, operation,belowOne=True)
                symmetrics.append(currentsymm)

            # Now that all the symmetrics of PDB2 are calculated, figure out which is the closest symmetric to the centre of mass of pdb1 and write it out
            # This is where using big matrices with Numpy proves incredibly useful!
            if len(symmetrics)>0:
                currentbest=(-1,10000)


                #Going through symmetry equivalent positions for this heavy atom:
                for j,xyzha in enumerate(symmetrics):    #j will be used to chose the closest symmetric ha to centre of mass of PDB1

                    # Distance matrix in fractional coordinates
                    distMat=unitCellTools.distanceFracMat(Gmat,PDB1FracCoord,xyzha) #distance matrix between this heavy atom and all atom from the pdb file
 
                    # Index of the matrix line with minimal distance (allowing us to retrieve the PDB1 atom closest to this symmetric)
                    minidx=np.argmin(distMat,axis=0)

                    # The corresponding distance (pdb atom - ha atom)
                    distance=distMat[minidx]

                    # If this distance is inferior to the anything we had with other symmetrics, store it
                    if distance<currentbest[1]:
                        currentbest=(j,distance,minidx)                         #j is the symmetric number
                        

                # Best matches
                best_sym_frac= symmetrics[currentbest[0]]
                closest_pdb_atom_frac= PDB1FracCoord[currentbest[2]]
                closest_pdb_atom_orth=PDB1orthCoord[currentbest[2]]

                # Vector joining the closest ha symmetric and its atom on the protein structure in orthogonal 
                diff_orth=unitCellTools.frac2Ortho(Omat,best_sym_frac - closest_pdb_atom_frac)

                # Then retrieving the coordinate of the ha in orthogonal coordinates, wherever the protein was, is trivial
                new_coordOrth = closest_pdb_atom_orth + diff_orth

                # Write the output PDB file for the heavy atom
                new_line=replaceATOMrec(inputLine=pdblines[i], replaceDic={'x': new_coordOrth[0],'y': new_coordOrth[1],'z': new_coordOrth[2]})
                outputFile.write(new_line)

        outputFile.write('END')
        outputFile.close()

        if override:
            print("REMARK: OVERRIDING %s"%os.path.join(outputDir,fileOutName+'.pdb'))
            shutil.move(os.path.join(outputDir,TMPoutputName),os.path.join(outputDir,fileOutName+'.pdb'))

            return os.path.join(outputDir,fileOutName+'.pdb')
        else:
            return os.path.join(outputDir,TMPoutputName)
                    

    else:
        print("Sorry, one of the files doesn't seem to exist! Stopping now."%pdbfilePath)
        return -1

def distanceCbeta_ha(pdbfilePath="/path/to/my/PDB", haFilePath="/path/to/my/file.ha", sfac="SE", unitCellParam=[10.0,10.0,10.0,90.0,90.0,90.0], spaceGroupNum=1, znum=1, cutoff=CUTOFFHA):
    """Computes a distance matrix between cbeta and heavy atoms contained in respectively a pdb file (protein) and a .ha or .res file from shelxe

    pdbfilePath (string): path to input pdb file
    haFilePath (string): path to the input heavy atom file (this must be a .hat or .res file or a '.pdb' or '.pda')
    sfac (string): Type of heavy atom scatterer (ex: "SE")
    unitCellParam (array of floats): unit cell parameters
    spaceGroupNum(int) : space group number
    znum (int): znum record to write in the output pdb file (leave it as 1)
    cutoff: maximum distance to consider an heavy atom close to a C-beta (default: 4 Angstroms)

    """

    # Checking input files
    if os.path.exists(pdbfilePath) and os.path.exists(haFilePath):
        pdbfilePath=os.path.abspath(os.path.normpath(pdbfilePath))
        haFilePath=os.path.abspath(os.path.normpath(haFilePath))
        outputDir=os.path.dirname(pdbfilePath)              #output directory for putting the pdb files from heavy atoms


        cbetaAtomsList=[]
        haAtomsList=[]
        toDelete=False

        #open the pdb file first and collect only the coordinates of the cbeta atoms
        with open(pdbfilePath, 'r') as pdbf:
            for line in pdbf:
                m= cBetaAtomLine.match(line)                                    #match the regular expression
                if m:
                    atomName=m.group(1)+'_'+m.group(2)+'_'+m.group(3).strip()      # ex: ALA_A_201
                    coordinates=(float(m.group(4)), float(m.group(5)), float(m.group(6)))  # tuple (x,y,z)
                    cbetaAtomsList.append((atomName,np.array(coordinates)))


        #Now do the same for the ha res or pdb file containing heavy atoms
        if haFilePath.endswith('.pdb') or haFilePath.endswith('.pda'):
            pdbHA = haFilePath

        elif haFilePath.endswith('.hat') or haFilePath.endswith('.res'):
            outputDir,basename=  os.path.split(haFilePath)
            filename,ext= os.path.splitext(basename)
            outnameFA=filename+'_fa.pdb'
            pdbHA = hat2pdb(haFilePath, outputDir=outputDir,sfac=sfac, unitCellParam=unitCellParam, spaceGroupNum=spaceGroupNum, znum=1, outputName=outnameFA)
            toDelete=True

        else:
            print("ERROR: your heavy atom file extension must be either '.pdb', '.pda', '.hat' or '.res', please check it.")
            return None

        if filePresent(pdbHA):
            # The generated PDB ha file must be compacted (symmetry operations) around the pdb fragment of interest 
            pdbHA=compactHA(pdbfilePath,pdbHA, override=True)

            # Read the newly generated pdb ha file and extract coordinates
            with open(pdbHA, 'r') as pdbha:
                for line in pdbha:
                    m= cHAatomLine.match(line)                                    #match the regular expression
                    if m:
                        atomName=m.group(1).strip()      # ex: ALA_A_201
                        coordinates=(float(m.group(2)), float(m.group(3)), float(m.group(4)))  # tuple (x,y,z)
                        haAtomsList.append((atomName,coordinates))

        else:
            print("ERROR in function 'distanceCbeta_ha', the ha pdb file is absent or cannot be generated")
            return None


        # Now calculate the distance matrix between ha atoms and the C_betas (lines: PDB atoms, columns : ha atoms)
        distanceMatrix=np.zeros((len(cbetaAtomsList), len(haAtomsList)))
        for i, elemProt in enumerate(cbetaAtomsList):
            for j, elemHA in enumerate(haAtomsList):      
                distanceMatrix[i,j] = unitCellTools.distanceOrth(elemProt[1], elemHA[1])  #interatomic vector length
                
        # min distance from the protein for each heavy (columns)
        minMat=np.min(distanceMatrix,axis=0)

        #Output the distances:
        print("\n")
        print("Scoring heavy atom distance from C-beta of the protein:")
        print("HA \t DISTANCE (A):")
        for i, heavyAtomDist in enumerate(minMat):
            print("(%d) \t %.2f"%(i, heavyAtomDist))

        # Score: fractions of the heavy atoms sitting at less than x Ang. from the protein
        score = len([x for x in minMat if x<= cutoff]) / float(len(minMat))

        #print("Min distance for each heavy atom: %s"%minMat)
        print("Score: %.2f  (fraction of the input heavy atoms sitting at less than %s angstroms from a c-beta)\n"%(score,cutoff))
        if toDelete:
            try:
                os.remove(pdbHA)  #remove the temporary PDB file after having used it
            except:
                print("WARNING: distanceCbeta_ha: Cannot delete %s"%pdbHA)
        return score, len(haAtomsList)

    else:
        print("ERROR in function 'distanceCbeta_ha', one of the input PDB files doesn't exist or is corrupted")
        return None

def pattersonPeaksFromPDB(pdbfilePath=None, fracCoord=None,unitCellParam=None, spaceGroupNum=None, sfac='SE', cutoffDistance=0.1, filterMethod="relint", cutoffRelIntensity = 0.1, sigmaCutoff = 0.0, writePDB=False, harker=True):
    
    if pdbfilePath is not None and os.path.exists(pdbfilePath):

        # A structure file can be rentered directly as a .hat or .res file and be converted to pdb for the calculation to proceed
        toDelete=False
        if pdbfilePath.endswith('.hat') or pdbfilePath.endswith('.res'):
            outputDir,basename=  os.path.split(os.path.abspath(pdbfilePath))
            filename,ext= os.path.splitext(basename)
            outnameFA=filename+'_fa.pdb'
            pdbfilePath = hat2pdb(pdbfilePath, outputDir=outputDir,sfac=sfac, unitCellParam=unitCellParam, spaceGroupNum=spaceGroupNum, znum=1, outputName=outnameFA)
            toDelete=True

        natom, PDBorthCoord, elemTab =extractCoordinatesFromPDB(pdbfilePath)   #empty array to store the coordinates the first PDB
        if PDBorthCoord is None:
            print("ERROR in function 'pattersonPeaksFromPDB', coordinates from the input PDB %s cannot be parsed"%pdbfilePath)
            return None

        if unitCellParam is None:
            try:
                unitCellParam=unitCellTools.extract_cryst_card_pdb(pdbfilePath)
            except:
                print("pattersonPeaksFromPDB: error, no unit cell information available from this PDB")
                return None

        if unitCellParam is None:
            print("ERROR in function 'pattersonPeaksFromPDB', the CRYSTCARD from the input PDB %s cannot be parsed"%pdbfilePath)
            return None

        deOmat=unitCellTools.deOmat(*unitCellParam[0:6])        #de-orthogonalization matrix to work with fractional coordinates
        PDBfracCoord= unitCellTools.ortho2Frac(deOmat,PDBorthCoord)   #we have to work with fractional coordinates

    elif fracCoord is not None:
        PDBfracCoord=fracCoord
        elemTab=[sfac] * len(fracCoord)
        toDelete=False

    else:
        print("pattersonPeaksFromPDB: no suitable coordinates to calculate Paterson, skipping")
        return None


    print("############################")
    print("# PATTERSON PEAKS FROM PDB #")
    print("############################")
    print("\n-----------------------------")
    print("PDB file: %s"%pdbfilePath)
    print("-----------------------------")
    print("Space group number %s"%spaceGroupNum)

    
    omat=unitCellTools.Omat(*unitCellParam[0:6])            #orthogonalization matrix to work with orthogonal coordinates

    interatomicVectors=[]          #compute all interatomic vectors and their intensity as tuples (product of nelectrons of each atom) 
    

    if harker:
        print("MODE: filter Patterson peaks to keep only those located in HARKER SECTIONS for space group %d"%spaceGroupNum)
        harkerSections= unitCellTools.harkerSections(spaceGroupNum, returnObjectVec=True)


    for i,atom in enumerate(PDBfracCoord):
        if harker:
            for harkerVec in harkerSections:
                pk=harkerVec.applyTransfo(atom)
                height= np.square(NELECTRONS[elemTab[i]])
                interatomicVectors.append((pk,height))
        else:
            for j,atom2 in enumerate(PDBfracCoord):
                peakCoord= atom - atom2             #np arrays of coordinates
                height= NELECTRONS[elemTab[i]] * NELECTRONS[elemTab[j]]
                interatomicVectors.append((peakCoord%1,height))

    #We only want to keep "positive" Patterson peaks in fractional coordinates
    # def positiveVector(vec=np.array([0,0,0])):
    #     out=[coord%1 for coord in vec]
    #     return np.array(out)

    #And now aggregate vectors which are the same to get a patterson peak list:
    pattersonPeaks={}
    for t1 in interatomicVectors:
        vec1=t1[0]

        #Avoid taking negative vectors
        # if any(vec1 <0):
        #     vec1= positiveVector(vec1)

        clef=tuple(vec1)
        clefneg=tuple(-vec1)
        if not clef in pattersonPeaks:
            pattersonPeaks[clef] = t1[1]  #peak intensity
        elif vecIsZero(vec1) or not clefneg in pattersonPeaks:  #Adding the intensity to the already present peak, avoiding to put negative versions of vectors which are already in
            #print("peak {} found once more".format(vec1))
            pattersonPeaks[clef] += t1[1]




    sorted_peaks = sorted(pattersonPeaks.items(), key=lambda l:l[1], reverse=True)
    listeOut=[]

    # Mean and starndard deviation of the peak list
    Ilist=[t[1] for t in sorted_peaks[1:]] if not harker else  [t[1] for t in sorted_peaks]  #Note : [1:] if for excluding the origin peak
    meanI=np.mean(Ilist)         
    stdDevI=np.std(Ilist)

    if harker:
        print("\nTOTAL %d peaks originating from %d atoms in %d Harker sections"%(len(sorted_peaks), len(PDBfracCoord), len(harkerSections)))
    else:
        print("\n%d non-origin peaks: Mean Intensity: %.3f, std: %.3f\n"%(len(pattersonPeaks.values())-1, meanI, stdDevI))

    def filterBySigma(I, meanI=meanI, stddevI=stdDevI):
        if I>= meanI + sigmaCutoff * stddevI:
            return True
        else:
            return False

    def filterByRelativeIntensity(I, originI, threshold):
        if I>= originI * threshold:
            return True
        else:
            return False


    def sigmaPeak( I, meanI=meanI, stdDevI=stdDevI):
        out = (I - meanI) / stdDevI if stdDevI != 0 else 0
        return out 

    if not harker:
        if filterMethod == "sigma":
            filterI_function= filterBySigma  
        elif filterMethod == "relint":
            filterI_function= filterByRelativeIntensity
        else:
            filterI_function= lambda x,y,z:True
    else:
        filterI_function= lambda x,y,z:True

    #Fill up the final list with relative intensity
    for i, pk in enumerate(sorted_peaks):

        if i==0: #Origin peak
            originIntensity=pk[1]
            listeOut.append({"fracCoord":pk[0], "absoluteIntensity": pk[1], "sigma": 0, "relativeIntensity":1, "orthCoord":pk[0]})
        else:    #Other peaks
            if filterMethod == "sigma":
                arg2, arg3 = (meanI, stdDevI)  
            elif filterMethod == "relint":
                arg2, arg3 =(originIntensity, cutoffRelIntensity)
            
            if filterI_function(pk[1], arg2, arg3):
                relativeIntensity = float(pk[1])/originIntensity
                ortha=unitCellTools.frac2Ortho(omat, pk[0])
                listeOut.append({"fracCoord":pk[0], "absoluteIntensity": pk[1], "sigma": sigmaPeak(pk[1]), "relativeIntensity":relativeIntensity, "orthCoord":ortha})


    
    print(" n \tabsInt\t%Int.\tsigma\t\tFRAC\t\t\tORTH")
    for i, peak in enumerate(listeOut):
        xfrac, yfrac, zfrac = tuple(peak["fracCoord"])
        xorth, yorth, zorth = tuple(peak["orthCoord"]) 
        Int = peak["relativeIntensity"]
        absInt= peak["absoluteIntensity"]
        sigma= peak["sigma"]
        print("({})\t{} \t{:4} \t{: .1f} \t{: .3f} {: .3f} {: .3f} \t {: 8.2f} {: 8.2f} {: 8.2f}".format(i, absInt, Int*100, sigma,xfrac, yfrac, zfrac , xorth, yorth, zorth))
    
    if writePDB:
        writePDBfromPatterson(listeOut,unitCellParam, spaceGroupNum, fileNameOut="patterson_from_pdb.pdb")
    if toDelete:
        try:
            os.remove(pdbfilePath)  #remove the temporary PDB file after having used it
        except:
            print("WARNING: pattersonPeaksFromPDB: Cannot delete %s"%pdbfilePath)
    return listeOut


def pattersonFromData(pathTo_hkl_file=None, resolution=2.0, spaceGroupNum=1,unitCellParam=[78.240,78.240,37.28,90,90,90], cutoffDistance=1, filterMethod="sigma", cutoffRelIntensity = 0.1, sigmaCutoff = SIGMAPATTERSON, gridDivide=3, ngridMax=100000, amplitudes=False, writePDB=False, harker=True):
    """Computes Patterson peaks from hkl data on a 3D grid of resolution/3 

    pathTo_hkl_file:    string     path the the input shelxe hkl reflection file
    resolution:         float      resolution cutoff in Angtroms
    spaceGroupNum:      int        Space group number
    unitCellParam:      Array of floats, unit cell parameters
    cutoffDistance:     float      Minimal distance in angstroms that will separate two peaks
    cutoffRelIntensity: float      Threshold in percentage intensity (relative to the origin) to accept a peak
    gridDivide:         int        The number of grid points along each axis will be resolution /  gridDivide
    """

    try:
        asuDic= unitCellTools.get_asu_borders_from_sg_dictionary(spaceGroupNum)              #Dictionary containing info on the asu's limits for the space group
        symops=unitCellTools.get_symops_from_sg_dictionary(spaceGroupNum)
        unitCellParam=[float(x) for x in unitCellParam]
        Gstar=unitCellTools.Gstar(*unitCellParam)
        gridDivide=float(gridDivide)


    except Exception as e:
        print("pattersonFromData: problem while trying to retrieve the asu border information")
        return None

    #Parsing the HKL file for intensities or amplitudes and sigmas
    if pathTo_hkl_file is not None and os.path.exists(pathTo_hkl_file):

        reflectionList=[]
        with open(pathTo_hkl_file,'r') as f:
            for ligne in f:
                m=ligne_hkl_re.match(ligne)
                if m :
                    h= int(m.group(1))
                    k= int(m.group(2))
                    l= int(m.group(3))
                    resolhkl=unitCellTools.resolution(h, k, l, Gstar)
                    if resolhkl >= resolution:  #apply high resolution cutoff
                        reflectionList.append({'hkl': np.array([h, k, l]), 'I': float(m.group(4)), 'SIGI': float(m.group(5))})
       
        numberOfReflections=len(reflectionList)
        volume_squared=math.pow(unitCellTools.unitCellVolume(*unitCellParam),2)
        #set up the required matrices
        omat=unitCellTools.Omat(*unitCellParam)
        #'for' loops are SLOW, try another approach that first fills up two matrices so that their product contains all the dot products we want:
#         N x 3 reflections array dotted by 3 x m griding points

#             U1  U2 ...                                    d1  d2 ...
#             V1  V2 ...                                    d3  d4 ...
#             W1  W2 ...                                    d5  d6 ...
#                                          
#                                              
# H1  K1  L1  d1  d2 ...  n x m           
# H2  K2  L2  d3  d4 ...
# H3  K3  L3  d5  d6 ...
#   ...              ...

        #BORDERS OF THE ASYMMETRIC UNIT FOR THIS SPACEGROUP
        if 'condition' in asuDic:
            conditionAsu=asuDic['condition']
        else:
            conditionAsu=lambda x,y,z:True

        #FUNCTIONS
        def isSameVector(npvector1, npvector2=np.array([0,0,0]), limfrac=0.10):
            """Determines whether a set of coordinates refer to the origin peak, the frac coord input coordinates must lie around 0.15 of zero"""

            vectmp= [0 if abs(1-t[0]-t[1]) < limfrac or abs(t[0]-t[1]) < limfrac else 1 for t in zip(tuple(npvector1), tuple(npvector2))]  #the minus is ommited for -(1-x) since we want to know 

            if vectmp == [0,0,0]:
                return True
            return False

        def isNewVector(npmatrix, npvector2=np.array([0,0,0]), limfrac=0.10):
            """Determines whether a vector is already present in a matrix according to the notSameVector function criteria"""
            arrayResult= np.apply_along_axis(isSameVector, 1, npmatrix, npvector2=npvector2, limfrac=limfrac)
            # print npmatrix
            # print arrayResult, npvector
            # print "\n"

            if True in arrayResult:   #If the same vector is found
                return False
            return True

        def filterBySigma(I, meanI, stddevI):
            if I>= meanI + sigmaCutoff * stddevI:
                return True
            else:
                return False

        def filterByRelativeIntensity(I, originI, threshold):
            if I>= originI * threshold:
                return True
            else:
                return False

        def minBorder(t1,t2):
            """ get the minimal tuple from two tuples on each index to merge Harker sections and asymmetric unit
                ex from t1=(0,1) and t2=(0.4,0.5), will return (0,0.5)

            """
            t1=[x%1 if x<0 else x for x in t1]
            t2=[x%1 if x<0 else x for x in t2]

            if t1[0]==t1[1]:
                return t1
            elif t2[0]==t2[1]:
                return t2
            else:    #return the minimal lower and upper border
                return tuple([min(t) for t in zip(t1,t2)])

        #Limits of the the unit cell, as indicated by the space group dictionary
        #Reduce the upper limit of each dimension to avoid falling again on the origin peak

        if harker:
            sectionsToCompute=unitCellTools.harkerSections(spaceGroupNum)
            asymBorders=(((asuDic['x'][0], asuDic['x'][1]),(asuDic['y'][0], asuDic['y'][1]), (asuDic['z'][0], asuDic['z'][1])),)

            #Now restraining the Harker sections to the asymmetric unit
            newSections=[]
            for s,section in enumerate(sectionsToCompute):
                newSections.append([])
                for t1,t2 in zip(section,asymBorders[0]):
                    newSections[s].append(minBorder(t1,t2))   #Add the tuple corresponding to the intersection of the two

            sectionsToCompute=newSections
            # print(asymBorders)
            # print(sectionsToCompute)
            # print("TUTU")
            # print(newSections)
            sectionsToCompute=[((0,0), (0,0), (0,0))] + sectionsToCompute

        else:
            sectionsToCompute=(((asuDic['x'][0], asuDic['x'][1]),(asuDic['y'][0], asuDic['y'][1]), (asuDic['z'][0], asuDic['z'][1])),)

        print("\n##############################")
        print("# PATTERSON PEAKS FROM DATA: #")
        print("##############################")
        print("DATAFILE: %s"%pathTo_hkl_file)
        print("-----------------------------")

        if harker:
            print("MODE: calculate Pattersons only in HARKER SECTIONS (inside the asymmetric unit)\n")
        else:
            print("MODE: calculate Pattersons in the whole ASYMMETRIC UNIT\n")
        print("Number of reflections used: %d (high res. cutoff: %sA)"%(numberOfReflections,resolution))
        print("Grid spacing: resolution / %d = %.3f A"%(gridDivide, float(resolution)/gridDivide))
        print("Space group number %s\n"%spaceGroupNum)
        if amplitudes:
            print("NOTE: Squaring the provided amplitudes work with intensities\n")
        if resolution<2.5:
            print("Setting the cutoff resolution to 2.5A")
            resolution=2.5
        ntotpt=0
        nx=0
        ny=0
        nz=0
        print("Sections of the Patterson map to calculate:")
        for n,section in enumerate(sectionsToCompute):

            print("\n-->Section %d:"%n)    
            limxlow, limxhigh = section[0][0], section[0][1]
            limylow, limyhigh = section[1][0], section[1][1]
            limzlow, limzhigh = section[2][0], section[2][1]
            print("x from %s to %s"%(limxlow, limxhigh))
            print("y from %s to %s"%(limylow, limyhigh))
            print("z from %s to %s"%(limzlow, limzhigh))


            intervalAng=float(resolution) /gridDivide

            nxtmp= (unitCellParam[0] * (limxhigh - limxlow))/ intervalAng if (limxhigh - limxlow) !=0 else 1
            nytmp= (unitCellParam[1] * (limyhigh - limylow)) / intervalAng if (limyhigh - limylow) !=0 else 1
            nztmp= (unitCellParam[2] * (limzhigh - limzlow))/ intervalAng if (limzhigh - limzlow) !=0 else 1

            nx += nxtmp
            ny += nytmp
            nz += nztmp

            ntotpt += np.ceil(nxtmp) * np.ceil(nytmp) * np.ceil(nztmp)
            print("%s x %s x %s = %s grid points"%(nxtmp, nytmp, nztmp, ntotpt))

        print("\nTotal number of gridpoints to calculate: %d x %d x %d = %d"%(np.ceil(nx), np.ceil(ny), np.ceil(nz), ntotpt))

        while ntotpt > ngridMax:
            if gridDivide>1:
                ntotpt=0
                nx=0
                ny=0
                nz=0
                gridDivide -= 1
                if gridDivide <=0:
                    print("Too many grid points to calculate, skipping..")
                    return None

                intervalAng=resolution /gridDivide
                print("reducing the number of gridpoints since it is greater than %s, setting the spacing to %s / %s = %.1f"%(ngridMax,resolution, gridDivide, resolution / gridDivide))
                print("Sections of the Patterson map to calculate:")
                for n,section in enumerate(sectionsToCompute):
                    limxlow, limxhigh = section[0][0], section[0][1]
                    limylow, limyhigh = section[1][0], section[1][1]
                    limzlow, limzhigh = section[2][0], section[2][1]
                    print("\n-->Section %d:"%n)
                    
                    nxtmp= (unitCellParam[0] * (limxhigh - limxlow))/ intervalAng if (limxhigh - limxlow) !=0 else 1
                    nytmp= (unitCellParam[1] * (limyhigh - limylow)) / intervalAng if (limyhigh - limylow) !=0 else 1
                    nztmp= (unitCellParam[2] * (limzhigh - limzlow))/ intervalAng if (limzhigh - limzlow) !=0 else 1

                    nx += nxtmp
                    ny += nytmp
                    nz += nztmp

                    ntotpt += np.ceil(nxtmp) * np.ceil(nytmp) * np.ceil(nztmp)
                    print("%s x %s x %s = %s grid points"%(np.ceil(nxtmp), np.ceil(nytmp), np.ceil(nztmp), ntotpt))
                
                print("New number of gridpoints:  %d x %d x %d = %d\n"%(np.ceil(nx), np.ceil(ny), np.ceil(nz), ntotpt))
            else:
                print ("The number of grid points is greater than 100 000 (actually %d), the calculation might be long!"%ntotpt)
                break



        # for a in reflectionList[:10]:
        #     print(a['hkl'], a['I'], a['SIGI'])

#        print("axe 'a' : dimensions: %.2f angstroms (x %.3f), number of grid points: %d (along %.2f Ang.)"%(unitCellParam[0], (limxhigh - limxlow), np.ceil(nx), unitCellParam[0] * (limxhigh - limxlow)))
#        print("axe 'b' : dimensions: %.2f angstroms (x %.3f), number of grid points: %d (along %.2f Ang.)"%(unitCellParam[1], (limyhigh - limylow), np.ceil(ny), unitCellParam[1] * (limyhigh - limylow)))
#        print("axe 'c' : dimensions: %.2f angstroms (x %.3f), number of grid points: %d (along %.2f Ang.)"%(unitCellParam[2], (limzhigh - limzlow), np.ceil(nz), unitCellParam[2] * (limzhigh - limzlow)))

        filterI_function= filterBySigma if filterMethod == "sigma" else filterByRelativeIntensity

        translationArray=np.empty([3,0])
        # Fill in the translationArray
        counter=0
        for section in sectionsToCompute:            
            limxlow, limxhigh = section[0][0], section[0][1]
            limylow, limyhigh = section[1][0], section[1][1]
            limzlow, limzhigh = section[2][0], section[2][1]

            nx= (unitCellParam[0] * (limxhigh - limxlow))/ intervalAng if (limxhigh - limxlow) !=0 else 1
            ny= (unitCellParam[1] * (limyhigh - limylow)) / intervalAng if (limyhigh - limylow) !=0 else 1
            nz= (unitCellParam[2] * (limzhigh - limzlow))/ intervalAng if (limzhigh - limzlow) !=0 else 1

            rangex=limxhigh - limxlow if nx!=1 else 1
            rangey=limyhigh - limylow if ny!=1 else 1
            rangez=limzhigh - limzlow if nz!=1 else 1

            valuesU = [limxlow] if limxhigh == limxlow else np.arange(limxlow,limxhigh,rangex/nx)
            valuesV = [limylow] if limyhigh == limylow else np.arange(limylow,limyhigh,rangey/ny)
            valuesW = [limzlow] if limzhigh == limzlow else np.arange(limzlow,limzhigh,rangez/nz)

            for u in valuesU :
                #print("U %s"%u)
                for v in valuesV:
                    #print("\tV %s"%v)
                    for w in valuesW :
                        #print("\t\tW %s"%w)
                        if conditionAsu(u,v,w):          
                            translationArray=np.append(translationArray, [[u],[v],[w]], axis=1)     #add a column
                            counter+=1

        # setting up Numpy arrays
        totalGridPoints=counter
        reflectionArray=np.zeros((numberOfReflections,3),dtype=int)
        intensitiesArray=np.zeros(numberOfReflections)


        #fill in the reflection array:
        for i,ref in enumerate(reflectionList):
            reflectionArray[i, :] = ref['hkl']
            intensitiesArray[i] = ref['I']

        # make a column vector of all reflections
        intensitiesArray = intensitiesArray.reshape((intensitiesArray.size,1))

        if amplitudes:
            intensitiesArray = np.power(intensitiesArray,2)
            #intensitiesArray=np.abs(intensitiesArray)



        print("\nTotal number of grid points recorded: %d"%(totalGridPoints))
        print("Please wait, this can be long...\n")

        #print("reflectionArray is %s"%reflectionArray)
        #print("translationArray is %s"%translationArray)

        # CALCULATING THE PATTERSON MAP
        #Taking the product of these two matrices, then getting the cos of it and then summing these cosines over all reflections(lines)
        dotProducts=np.dot(reflectionArray, translationArray)   #get all dot products hu + kv + lw
        dotProducts=np.cos(2.0*np.pi*dotProducts)                         #get cos(hu + kv + lw)
        dotProducts=np.multiply(dotProducts,intensitiesArray)   #get Ihkl * cos(hu + kv + lw)

        pattersonPeaks=np.sum(dotProducts, axis=0)  / volume_squared   #---> we can skip the division by volume squared since it is a constant
        #print("The Patterson peaks from your data pattersonPeaks are %s"%pattersonPeaks)
        peakList=[]

        #Ordering the peaklist by intensity
        for k in range(len(pattersonPeaks)):
            argMax=np.argmax(pattersonPeaks)
            coord=translationArray[:,argMax]
            peakList.append((coord, pattersonPeaks[argMax]))     #add a tuple coordinate, peak
            pattersonPeaks[argMax]= -10000                       # 'Removes' the peak from the input list


         # If the coordinates of the top peaks are not 0, 0, 0 then we have done something wrong..
        #originPeak= peakList[0]         
        #if originPeak[0][0] != 0 or originPeak[0][1] != 0 or originPeak[0][2] != 0:
        #    return None
            
        #Filter origin peaks, the defaut argument of this function (isSameVector) implies that each row vector of the current vector with be compared with [0,0,0]
        peakList=[peakList[0]] + [pk for pk in peakList if not isSameVector(pk[0], limfrac=0.15)]
        Ilist=[pk[1] for pk in peakList]
        meanI=np.mean(Ilist[1:])
        stdDevI=np.std(Ilist[1:])

        def sigmaPeak( I, meanI=meanI, stdDevI=stdDevI):
            out = (I - meanI) / stdDevI if stdDevI != 0 else 0
            return out 

        # Now that the peaklist is ordered, we are going to rewrite it in percentage of the origin,
        # Each peak is added to an output matrix, the distance of every new peak to all the peaks in the output matrix is calculated.
        # The new peak is accepted only if the distance to all other peaks is greater than a cutoff (matrix calculation with numpy)
        

        peakPercentage=[]
        currentFracMatrixPeaks=np.array([[0,0,0]]) 
        currentOrthMatrixPeaks=np.array([[0,0,0]])  #each line of the matrix is a Patterson peak in orthogonal coordinates

        for i, pk in enumerate(peakList):
            if i==0:
                originIntensity = pk[1]
                peakPercentage.append({"fracCoord":pk[0], "absoluteIntensity": pk[1], "sigma": 0, "relativeIntensity":1, "orthCoord":pk[0]})
            else:
                ortha=unitCellTools.frac2Ortho(omat, pk[0])
                distanceMin=np.min(np.linalg.norm(ortha-currentOrthMatrixPeaks, axis=1))   #compute the norm for each line of the matrix, take the min

                if distanceMin >= cutoffDistance:
                    currentOrthMatrixPeaks=np.append(currentOrthMatrixPeaks, np.array([ortha]), axis=0)  #add a new line (new patterson peak)
                    
                    #Select peaks only if they are above 4 sigma or if the relative intensity above x% of the origin  and when it is not part of a peak already written
                    
                    arg2, arg3 = (meanI, stdDevI) if filterMethod == "sigma" else (originIntensity, cutoffRelIntensity)

                    if filterI_function(pk[1], arg2, arg3) and isNewVector(currentFracMatrixPeaks, pk[0], limfrac=0.001):
                        relativeIntensity = pk[1]/originIntensity

                        #Finally we have to ensure that we don´t have the same peak several times by symmetry
                        flagSym=True

                        for operationNum in sorted(symops.keys()):
                            operation=symops[operationNum]
                            rotoTranslatedVec = unitCellTools.rotoTranslateFracCoord(pk[0], operation, belowOne=True)
                            if not isNewVector(currentFracMatrixPeaks, rotoTranslatedVec):  #Detects that the vector is already recorded
                                flagSym=False
                                break
                        if flagSym:
                            currentFracMatrixPeaks=np.append(currentFracMatrixPeaks, np.array([pk[0]]), axis=0)  #add a new line (new patterson peak)
                            peakPercentage.append({"fracCoord":pk[0], "absoluteIntensity": pk[1], "sigma": sigmaPeak(pk[1]),"relativeIntensity":relativeIntensity, "orthCoord":ortha})

        # # print the raw peak list
        print(" n \tabsInt\t\t\t%Int.\tsigma\t\tFRAC\t\t\tORTH")
        for i, peak in enumerate(peakPercentage):
            xfrac, yfrac, zfrac = tuple(peak["fracCoord"])
            xorth, yorth, zorth = tuple(peak["orthCoord"]) 
            Int = peak["relativeIntensity"]
            absInt= peak["absoluteIntensity"]
            sigma= peak["sigma"]
            print("({})\t{} \t{:6.2f} \t{: .1f} \t{: .3f} {: .3f} {: .3f} \t {: 8.2f} {: 8.2f} {: 8.2f}".format(i, absInt, Int*100, sigma, xfrac, yfrac, zfrac , xorth, yorth, zorth))

        peakTot=len(peakPercentage) -1          #We don't count the origin peak
        plural='S' if  peakTot >1 else ''
        if filterMethod=="sigma":
            print("\nTOTAL: %d NON-ORIGIN PEAK%s (ABOVE %d STDDEV) IN THE ASYMMETRIC UNIT (peak separation filter: %.2f Ang.)"%(peakTot, plural, sigmaCutoff, cutoffDistance))

        else:
            print("\nTOTAL: %d NON-ORIGIN PEAK%s (ABOVE %d %% OF THE ORIGIN) IN THE ASYMMETRIC UNIT (peak separation filter: %.2f Ang.)"%(peakTot, plural, cutoffRelIntensity*100, cutoffDistance))

        if writePDB:
            writePDBfromPatterson(peakPercentage,unitCellParam, spaceGroupNum)
        return peakPercentage
        #The returned list of dictionnaries is of the form [{'fracCoord', 'relativeIntensity', 'orthCoord'} ]


    else:
        print("ERROR in function 'pattersonFromData', the input hkl file %s doesn't exist or is corrupted"%pathTo_hkl_file)
        return None        

def writePDBfromPatterson(PattersonPeakDic, unitCellParam, spaceGroupNum, fileNameOut="pattersons_data.pdb"):
    """ Writes a PDB file (water molecules) corresponding to the input Patterson peak list"""

    sgsymbol=unitCellTools.get_full_symbol_from_sg_number(spaceGroupNum)
    pdbout=open(fileNameOut,'w')
    lineaHOH="HETATM    1  O   HOH A   1       5.522 -10.189  35.779  1.00 19.58           O"
    crystcard=unitCellTools.writeCRYSTCARDintoPDB(*unitCellParam, sgsymbol=sgsymbol)
    pdbout.write(crystcard)

    for i, peak in enumerate(PattersonPeakDic):
        xorth, yorth, zorth = tuple(peak["orthCoord"])
        new_line=replaceATOMrec(inputLine=lineaHOH, replaceDic={'serial': i, 'x': xorth,'y': yorth,'z': zorth, 'seqnum': i})
        pdbout.write(new_line+'\n')
    pdbout.write('END')
    pdbout.close()

def distanceMatrix(coordFracList=[[0.2,0.4,0.3],[0.5,0.2,0.9]], vecFrac2=[0.5,0.2,0.9],spaceGroupNum=4, unitCellParam=[10,10,10,90,90,90],originshift=True, inversion=False, returnmin=False):
    """ Compute a distance matrix between one vector list (rows) and all the symmetry/origin/inversion possibilities of a single vector (columns) (fractional coordinates)"""

    def polarAxisCoord(vector):
        """ returns a index 0, 1,2 representing the polar axis (i.e x, y,z) to eliminate from the vectors to compare"""
        for i,coord in enumerate(vector):
            if regxyz.match(str(coord)):
                return i
        return None

    def modifV(index,vector):
        vector[index]=0.0
        return vector

    def moduloOne(vector):
        """ set all coordinates between 0 and 1"""
        return [c%1 for c in vector]

    # Set all coordinates between zero and one
    coordFracList=[moduloOne(v) for v in coordFracList]
    vecFrac2=moduloOne(vecFrac2)

    axes=('x', 'y', 'z')
    Gmat=unitCellTools.Gmat(*unitCellParam)

    #Variables
    npvec2List=[]
    originShiftList=[]

    # Dictionnary that will contain all distance matrices (one per origin shift or inversion)
    dicoVec2={}
    dicoMAT={}

    # Treating equivalent positions
    symops=unitCellTools.get_symops_from_sg_dictionary(spaceGroupNum)
    for operationNum in sorted(symops.keys()):
        operation=symops[operationNum]
        npvec2List.append(list(unitCellTools.rotoTranslateFracCoord(vecFrac2, operation, belowOne=True)))    #Add a symmetry equivalent of this vector

    #First list of vec2
    dicoVec2['0']=npvec2List[:]

    # originshift
    if originshift and unitCellTools.get_origins_from_sg_dictionary(spaceGroupNum) is not None:
        polar_bool, originShiftList=unitCellTools.get_origins_from_sg_dictionary(spaceGroupNum)


        #If the space group is polar, one of the coordinates doesn't count for comparing the vectors, then simply exclude it
        if polar_bool:
            polidx=polarAxisCoord(originShiftList[0])
            indices=[0,1,2]
            if polidx:
                print("\nPolar axis for space group %d: %s"%(spaceGroupNum,axes[polidx]))
                print("(setting each coordinate %s to zero in every vector to calculate the distance matrix)"%axes[polidx])
                #del(indices[polidx])

            #setting to zero the coordinate of the polar axis, we then deal with 2D vectors ()
            originShiftList=[modifV(polidx, v) if polidx is not None else v for v in  originShiftList]
            coordFracList=[modifV(polidx, v) if polidx is not None else v  for v in  coordFracList]
            npvec2List=[modifV(polidx, v) if polidx is not None else v for v in  npvec2List]

        # Now adding all the possible origin-shifted vectors to the list2
        for origin in originShiftList:
            if not vecIsZero(origin):   #We already have this origin
                npvec2Listplus=[]

                for v2 in npvec2List:
                    v2prime=[a+b for a,b in zip(v2 ,origin)]
                    #print("V2PRIME %s"%v2prime)
                    #print("npvec2Listplus %s"%npvec2Listplus)
                    if v2prime not in npvec2Listplus:
                        npvec2Listplus.append(v2prime)
                #First list of vec2
                dicoVec2[str(origin)]=npvec2Listplus[:]

    # Inversion, here we have to invert all origin shifts lists as well
    if inversion:      
        for origin in dicoVec2.keys():
            npvec2Listplus=[]
            for v2 in dicoVec2[origin]:
                v2inv=[-1*x for x in v2]
                if v2inv not in npvec2Listplus:
                    npvec2Listplus.append(v2inv)
            dicoVec2[str(origin)+'_i']=npvec2Listplus[:]

        npvec2Listplus=[]  # free memory

    # Now the matrix itself. NEW04Oct 2108 :We want one distance matrix per origin shift or inversion, putting into a dictionnary

    bestMat=('none',1000,None)   #Minimal mean distance between experimental and cross fourrier peaks among all matrices (origins)
    #BestMindist=1000   #Minimal  distance between experimental and cross fourrier peaks among minimal distances between all matrices (origins)
    for origin,npvec2List in dicoVec2.items():
        distmat=np.ones((len(coordFracList), len(npvec2List)))
        coordFracList=np.array(coordFracList)
        npvec2List=np.array(npvec2List)
        for i,v1 in enumerate(coordFracList):
            for j,v2 in enumerate(npvec2List):
                distmat[i,j]=unitCellTools.distanceFrac(Gmat,v1,v2)

        dicoMAT[origin]=distmat
        minmat=np.min(distmat, axis=1)    #returns the minimum distance in each line
        meanMinmat=np.mean(minmat)
        if meanMinmat< bestMat[1]:
            bestMat=(origin,meanMinmat,minmat)      # store the origin name, mean distance and corresponding matrix of minimal mdistances in a tuple

    if returnmin:
        return bestMat[2]
    else:
        return dicoMAT(bestMat[0])

    #except Exception as e:
        # print("WARNING: problem in function distanceMatrix")
        # print(e)
        # return None


def compare2pattersons(peaklistDATA, peaklistPDB, spaceGroupNum=1,unitCellParam=(10,10,10,90,90,90)):
    """
    This function basically compares the Patterson peak list from the data to the one obtained from a list of atoms in PDB formats
    It compute a distance matrix for the peaks from data and PDB and looks on each line how many peaks are considered close (the same)
    """

    #Peaks from the data Patterson, placed along lines
    peaksFromData=[]
    for pk in peaklistDATA:
        if not vecIsZero(pk["fracCoord"]): #Exclude the origin peak if present
            peaksFromData.append(pk["fracCoord"])

    #Initialize with -1 the final min distance matrix, for each peak in the data Paterson, it will give the distance to the closest peak of the PDB Patterson
    overallMatMin= np.full((len(peaksFromData),1),50,dtype=float)

    #Peaks from the PDB (each one will be used in a distance matrix, with its symmetry/origin shift equivalent position and compared with all peaks in the data)
    for pkpdb in peaklistPDB:
        frac= np.array(pkpdb["fracCoord"])
        if not vecIsZero(frac) : #Exclude the origin peak if present
            distMatMin=distanceMatrix(coordFracList=peaksFromData, vecFrac2=frac,spaceGroupNum=spaceGroupNum, unitCellParam=unitCellParam,originshift=False, inversion=False, returnmin=True)

        #Now for each of the data peak, we have the closest symmetry equivalent of that particular peak in the PDB

        for i in range(len(peaksFromData)):    # update the overall minimal distance matrix
            if distMatMin[i] < overallMatMin[i]:
                overallMatMin[i] = distMatMin[i]


        # Patterson scoring, compute the mean of the average minimal distance 

        score=np.mean(overallMatMin)

        print("\nPatterson score: %.2f (average minimum distance between patterson peaks from data and structure)\n"%score)
        return score

    else:
        return -1

def compareWithReferenceHA(atomlistREF=[[0.5,0.2,0.3]], atomlistPDB=[[0.5,0.8,0.4], [0.1,0.2,0.6]], spaceGroupNum=1,unitCellParam=(10,10,10,90,90,90), sfac=None, hatFile=None):
    """
    Almost the same function as 'compare2pattersons', takes a list of reference heavy atoms fractional coordinates and compares it to all possible symmetry/origin-shift
    It compute a distance matrix for the peaks from reference and from the PDB. Optionally it can return the minimum distance for each line( minimum distance among all possible symmetrics)
    """

    #Note if atomListPDB is None but haFile is given, then the coordinates for atomlistPDB are extracted from haFile
    if atomlistPDB is None and hatFile is not None and sfac is not None:
        atomlistPDB=parseReferenceHAFile(hatFile, sfac=sfac, printmsg=False)

    #Peaks from the data Patterson, placed along lines
    peaksFromREF=[]
    for frac in atomlistREF:
            peaksFromREF.append(frac)

    #Initialize with -1 the final min distance matrix, for each peak in the data Paterson, it will give the distance to the closest peak of the PDB Patterson
    overallMatMin= np.full((len(peaksFromREF),1),50,dtype=float)

    #Peaks from the PDB (each one will be used in a distance matrix, with its symmetry/origin shift equivalent position and compared with all peaks in the data)
    for fracpdb in atomlistPDB:
        distMatMin=distanceMatrix(coordFracList=peaksFromREF, vecFrac2=fracpdb,spaceGroupNum=spaceGroupNum, unitCellParam=unitCellParam,originshift=True, inversion=True, returnmin=True)

        #Now for each of the data peak, we have the closest symmetry equivalent of that particular peak in the PDB

        for i in range(len(peaksFromREF)):    # update the overall minimal distance matrix
            if distMatMin[i] < overallMatMin[i]:
                overallMatMin[i] = distMatMin[i]

        # Patterson scoring, compute the mean of the average minimal distance 

        scoreav=np.mean(overallMatMin)
        scoremin=np.min(overallMatMin)

        print ("\nREF-HA min: %.2f (minimum distance found between 2 ha from reference and structure)"%scoremin)
        print("REF-HA average: %.2f (average minimum distance between ha from reference and structure)\n"%scoreav)
        return scoremin, scoreav

    else:
        return -1

def peakHeightHA(lstfile):
    """ Extracts the peak height and the main difference between them"""
    #reg_res_peak_list=re.compile(r"\s+(\d)\s+([.\d]{6})\s+([.\d]{6})\s+([.\d]{6})\s+([.\d]+)")

    lstfile=os.path.abspath(lstfile)

    if os.path.exists(lstfile) and lstfile.endswith('.lst'):
        atomTag=False
        haList=[]
        CC_partial_struc = None
        CCha = None
        wMPE = None

        with open(lstfile,'r') as lst:
            for line in lst:
                mstart=reg_res_peak_start.match(line)
                m =reg_res_peak_list.match(line)
                mCC=regxp_CCpartial.match(line)
                mCCha=regxp_CCha.match(line)
                mCC2=regxp_CCpartial2.match(line)
                mstop =reg_res_peak_stop.match(line)
                mMPE= regxp_wMPE.match(line)

                if mstart:
                    atomTag=True

                elif m and atomTag:      #Here we collect the coordinates but we're not doing anything with them right now, maybe later
                    rank=int(m.group(1))
                    xfrac=float(m.group(2))
                    yfrac=float(m.group(3))
                    zfrac=float(m.group(4))
                    height=float(m.group(5))

                    # Exclude peaks with negative height
                    if height>0:
                        haList.append({'rank':rank, 'frac': (xfrac, yfrac, zfrac), 'height': height})

                elif mCC:
                    CC_partial_struc = float(mCC.group(1))

                elif mCC2:
                    CC_partial_struc = float(mCC2.group(1))

                elif mCCha:
                    CCha = float(mCCha.group(1))

                elif mMPE:
                    wMPE= float(mMPE.group(1))

                elif mstop:
                    atomTag=False
                    break


        # We return in the end the number of peaks, top-peak height, max difference and the first index of this max difference (ex 1 for diff1-2)

        if len(haList)>1:
            differences = []
            for i in range(len(haList)):
                if i< len(haList) -1:       #Don't take the last index
                    differences.append( (haList[i]['rank'], haList[i]['height'] - haList[i+1]['height']))  #rank, difference between two successive peaks 

            # Finding the maximum difference 
            diffMax_idx=np.argmax([x[1] for x in differences])     #index of the greatest difference

            CCha_str='none' if CCha is None else "%.2f"%CCha
            CC_partial_struc_str='none' if CC_partial_struc is None else "%.2f"%CC_partial_struc
            wMPE='none' if wMPE is None else wMPE

            print("\nFile: %s --> CC partial structure: %s %%, CCha: %s %%, number of ha-sites: %d, top-peak height: %.2f, maxDifference: %.2f [between heavy atom peaks %d (%.2f) and %d (%.2f)]\n"%(lstfile,CC_partial_struc_str, CCha_str, len(haList), haList[0]['height'], differences[diffMax_idx][1], differences[diffMax_idx][0], haList[diffMax_idx]['height'], differences[diffMax_idx][0]+1, haList[diffMax_idx+1]['height']))
            return len(haList), haList[0]['height'], differences[diffMax_idx][1], differences[diffMax_idx][0], CC_partial_struc, CCha, wMPE

        else:
            print("\nOne heavy atom peak with height %.2f\n"%haList[0]['height'])
            return 1, haList[0]['height'], -1, -1, CC_partial_struc, CCha, wMPE

    else:
        print("WARNING: peakHeightHA--> cannot open %s, the file does exist or does not have a .lst extension or is corrupted"%lstfile)

def filterCluAll(CluAllIn, DicOfBadGuys, LIMIT_CLUSTER=None, convNamesDic=None):
    """ Removes the 'bad' solutions (listed in DicOfBadGuys) from the Heap dictionnary (those filtered out by the Anomalous scoring)"""
    CluAllOut=[]

    for i,dic in enumerate(CluAllIn):
        
        heapIn=dic["heapSolutions"]
        flag = i if LIMIT_CLUSTER is None else LIMIT_CLUSTER

        if i==flag:                                            # index of the cluster to filter, if LIMIT_CLUSTER if None, all the clusters are filtered
            CluAllOut.append({"heapSolutions": ADT.Heap()})
            for tup in heapIn.asList():
                ensembleName= tup[1]['name']

                # In Borges, I need a correspondence ensemble name --> pdb name  to recognize the heap name form the list of discarded sol
                if convNamesDic:
                    ensembleName = convNamesDic[ensembleName]

                #print("-->TESTING %s"%ensembleName)
                for clef in DicOfBadGuys:
                    currentSet=set(DicOfBadGuys[clef])
                    if ensembleName not in currentSet:
                            #print("---------NOT IN eliminated")                    
                        CluAllOut[i]["heapSolutions"].push(tup[0],tup[1])
                #else:
                #    print("REMOVED: %s"%ensembleName)

        else:
            CluAllOut.append(dic)

    return CluAllOut

def intersectCCVal(CCValListofLists=[]):
    """ remove entries which are not communal to two CCVal dics (intersection of the two dictionaries
        Here the idea is to keep only solutions that have not been rejected by either 9.5EXP or 9_EXP in BORGES
    """
    setList=[]
    out=[]
    for ccval in CCValListofLists:
        names=[]
        for dico in ccval:
            names.append(os.path.basename(dico['corresp']))
            #print(os.path.basename(dico['corresp']),)
        setList.append(set(names))

    setFinal=setList[0]

    for i in range(len(setList)):
        if i<len(setList)-1:
            setFinal = setFinal.intersection(setList[i+1])   #intersection

    # Now filtering each CCVal
    for ccval in CCValListofLists:
        out.append([dic for dic in ccval if os.path.basename(dic['corresp']) in setFinal])

    return tuple(out)     # which will be a list of filtered ccval lists

def intersectionFilteredSol(CCValListofLists=[], listOfExcludedPDB=[]):
    """ To get a list of pdb which are neither in the two lists CC_Val1, CC_Val2
        The idea is to exclude solutions only when they are both rejected during the 9.5Exp and 9_exp filtering in A_BORGES

        If a PDB is present in any of the CC_Val dictionnary (entry 'corresp'), then it will be removed from the excluded list

    """
    #remove all possible duplicated entries in the list of excluded pdb
    listOfExcludedPDB=list(set(listOfExcludedPDB))

    for ccval in CCValListofLists:
        for dico in ccval:
            if 'corresp' in dico:
                pdbfile=os.path.basename(dico['corresp'])
                if pdbfile in listOfExcludedPDB:
                    listOfExcludedPDB.remove(pdbfile)
                    print("INFO SOFT ANOM FILTER: removing %s from the list of excluded pdb files since it has been selected at least once"%pdbfile)

    return listOfExcludedPDB



def saveFilteredSol(pathToSaveFile, solutions_filtered_out={}):
    """ export the list of filtered solution names as a json file in ANOMLIB"""
    pathToSaveFile = os.path.abspath(pathToSaveFile)
    with open(pathToSaveFile, 'w') as f:
        json.dump(solutions_filtered_out, f)


def retrieveFilteredSol(pathTojsonFile):
    """ retrieve the list of filtered solution names from a json file in ANOMLIB"""
    pathTojsonFile=os.path.abspath(pathTojsonFile)
    outDic={}
    if os.path.exists(pathTojsonFile):
        with open(pathTojsonFile, 'r') as f:
            outDic=json.load(f)
    else:
        print("WARNING in ANOMLIB.retrieveFilteredSol: cannot retrieve the json file %s"%pathTojsonFile) 
    return outDic

def llgdic(convNames, CluAll, isLite=False):
    """ retrieve LLG and zscores from solutions so that I can print them in the output of evaluateExp_cc
        code stolen from unifyCC2 in SELSLIB2
    """
    if isLite:
        convNames=dict([(os.path.basename(val)[:-4], val) for _,val in convNames.items()])
    inter = [item[1] for sublist in map(lambda y: y["heapSolutions"].asList(), CluAll) for item in sublist]  # all solutions (NS: note list of dics ) among all clusters
    llgd = {os.path.basename(convNames[dizio["name"]]): (dizio["llg"], dizio["zscore"]) for dizio in inter}

    return llgd

def truncate_fa(hres_cutoff=0, pathTo_hkl_file=None, unitCellParam=[78.240,78.240,37.28,90,90,90]):
        #Parsing the HKL file for intensities or amplitudes and sigmas
    if pathTo_hkl_file is not None and os.path.exists(pathTo_hkl_file):

        
        pathTo_hkl_file = os.path.abspath(os.path.normpath(pathTo_hkl_file))
        basedir= os.path.dirname(pathTo_hkl_file)
        Gstar=unitCellTools.Gstar(*unitCellParam)
        outputFile=os.path.join(basedir,"haTrunc_A_fa.hkl")
        outputFileHANDLE= open(outputFile,'w')

        if hres_cutoff>0:
            print("REMARK: Truncating {} to {} A resolution".format(pathTo_hkl_file,hres_cutoff))
            with open(pathTo_hkl_file,'r') as f:
                for ligne in f:
                    m=ligne_hkl_re.match(ligne)
                    if m :
                        h= int(m.group(1))
                        k= int(m.group(2))
                        l= int(m.group(3))
                        resolhkl=unitCellTools.resolution(h, k, l, Gstar)
                        #print("resolhkl: {}".format(resolhkl))
                        #print("h: {}, k: {}, l: {}".format(h,k,l))
                        if resolhkl >= hres_cutoff:  #apply high resolution cutoff
                            outputFileHANDLE.write(ligne)
                            #print("accepted")
                        # else:
                        #     print("rejected")

        else:
            outputFile=pathTo_hkl_file

        outputFileHANDLE.close()
        return outputFile
    else:
        return pathTo_hkl_file


def cleanSummary(pathToSummaryFile, nameJob):
    """ Used in EvaluateExp to remove filtering records in ANOMDIR/EVALUATION from a previous run that would have been interrupted"""

    out= ""

    pathToSummaryFile = os.path.abspath(os.path.normpath(pathToSummaryFile))
    if os.path.exists(pathToSummaryFile):
        okToWrite=True
        with open(pathToSummaryFile,'r') as f:
            for line in f:
                if line.startswith("----------"+nameJob):
                    okToWrite = False
                elif line.startswith("----------"):   # End of the section with the results to rewrite
                    okToWrite=True

                if okToWrite:
                    out += line

        #Wrting the output file replacing the input one
        fileOut = open(pathToSummaryFile,'w')
        fileOut.write(out)
        fileOut.close()

def deleteSubsequentFiles(root):
    """ In case of interruption at the 9_EXP or 9.5_EXP stage in Borges, delete 10* 11_EXP* deirectories and other subsequent files/folders in the flow"""

    target = ["10*", "11*", "best*"]
    todel=[]
    for t in target:
        todel.extend(glob.glob(os.path.join(root,t)))

    for f in todel:
        try:
            shutil.rmtree(f)
            print("Deleted: {}".format(f))
        except:
            print("REMARK: no file {} to delete".format(f))


###########CHECK FUNCTIONS HERE:

#start from an MTZ file, extract spacegroup, unit cell parameters and labels
#mtzfile=sys.argv[1]
#outputTypeDic,labelOut, spaceGroupNum, wavelength, unitcellDim =infoMTZ(mtzfile)
#print("%s %s %s %s %s"%(outputTypeDic,labelOut, spaceGroupNum, wavelength, unitcellDim))
#scafile= mtz2sca(".",mtzfile)
#hatfile=sys.argv[2]
#workingDir=os.getcwd()
#shelxcDic= prepareWithSHELXC(mode="SAD", format='sca', workingDirectory=workingDir,inputFilesDic={"SAD":scafile},cell=unitcellDim,spaceGroupNum=spaceGroupNum, waveLength=wavelength, sfac='S',nsites=9, ntry=1000, mind=2.5, specialPos=False)
#hat2pdb(hatfile, sfac="S", anomDir=".",unitCellParam=unitcellDim, spaceGroupNum=spaceGroupNum, znum=1)

#pdbfile=sys.argv[1]
#removeHETATMfromPDB(pdbfile)

# if len(sys.argv)>2:
#     inputPDB=sys.argv[1]
#     inputPDB2=sys.argv[2]
#     compactHA(inputPDB,inputPDB2, override=False)

# else:
#     print("USAGE: python compactHA.py pdb1.pdb pdbHA.pdb (where pdbHA.pdb contains the heavy atoms to comact around pdb1.pdb)")
#distanceCbeta_ha(pdbfile=sys.argv[1], haFilePath=sys.argv[2], sfac="S", unitCellParam=[78.240,78.240,37.280,90,90,90], spaceGroupNum=96, znum=1)
#pattersonPeaksFromPDB(pdbfilePath=sys.argv[1])
#pattersonFromData(pathTo_hkl_file=sys.argv[1], spaceGroupnum=96, resolution=1.86)

if __name__ == '__main__':
    #unitCellParam= (109.1140,   29.9280,   89.6810,   90.0000,   90.1010,   90.0000) # Cinthia's DNA 4
    #unitCellParam= (78.2390,   78.2390,   37.2810,   90.0000,   90.0000,   90.0000)  #lyzozyme native 96 resol 1.87
    # #unitCellParam= (78.1100,   78.1100,   37.0100,   90.0000,   90.0000,   90.0000)        #lyzozyme iodide 96
    #unitCellParam= (129.829,  129.829,  103.994,  90.00,  90.00,  90.00) #kouranom, spacegroup 4
    #pk1=pattersonFromData(pathTo_hkl_file=sys.argv[1], spaceGroupNum=4, resolution=2.0, unitCellParam=unitCellParam, filterMethod="sigma", sigmaCutoff=4.0, cutoffRelIntensity = 0.1 , gridDivide=3, amplitudes=True, writePDB=False, harker=True)
    #pk2=pattersonPeaksFromPDB(pdbfilePath=sys.argv[2], unitCellParam=unitCellParam, spaceGroupNum=96, writePDB=False, harker=True)
    #compare2pattersons(pk1, pk2, spaceGroupNum=96, unitCellParam=unitCellParam)
    #compareWithReferenceHA(atomlistREF=[[0.5,0.2,0.3], [0.55,0.1,0.22]], atomlistPDB=[[0.5,0.8,0.3], [0.1,0.2,0.6]], spaceGroupNum=4,unitCellParam=unitCellParam)
    #pdbha=hat2pdb(sys.argv[1], sfac="I",unitCellParam=unitCellParam, spaceGroupNum=97, znum=1, outputName="truc.pdb")
    #inputPDB=sys.argv[1]
    #pdbha=sys.argv[2]
    #compactHA(inputPDB,pdbha, override=False)
    #distanceCbeta_ha(pdbfile=sys.argv[1], haFilePath=sys.argv[2], sfac="FE", unitCellParam=unitCellParam, spaceGroupNum=4, znum=1)
    #distanceMatrix(coordFracList=[[0.2,0.4,0.3],[0.5,0.2,0.9]], vecFrac2=[0.5,0.2,0.9],spaceGroupNum=4, unitCellParam=unitCellParam,originshift=False, inversion=False)
    #peakHeightHA(sys.argv[1])
    #parseReferenceHAFile(sys.argv[1], sfac='S',unitCellParam=unitCellParam )
    unitCellParam=[67.8400,   67.8400,  101.7700,   90.0000,   90.0000,   90.0000]    # 3gt3
    a=truncate_fa(hres_cutoff=2.5, pathTo_hkl_file=sys.argv[1], unitCellParam=unitCellParam)
