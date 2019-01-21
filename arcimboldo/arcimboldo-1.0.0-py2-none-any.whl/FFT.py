#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import sys, math, re, os

import unitCellTools

# 3D plotting 
#from mpl_toolkits import mplot3d

#------------- REGULAR EXPRESSION
regexprCRYST1=re.compile(r"^CRYST1")
regexprATOM2=re.compile(r"(ATOM  |HETATM)([\d\.\s]{5})(\s)(.{4})(.{1})(.{3})(\s)(.{1})(.{4})(.{1})(.{3})([.\d\s\-]{8})([.\d\s\-]{8})([.\d\s\-]{8})(.{6})(.{6})(\s{10})(.{2}).*") 
reHKL= re.compile(r"([\-\d\s]{4})([\-\d\s]{4})([\-\d\s]{4}) ([\-\.\d\s]{8})([\-\.\d\s]{8})([\-\.\d\s]{8})([\-\.\d\s]{8})")

#------------- CONSTANTS
NELECTRONS={ 'H':1, 'HE':2, 'LI':3, 'BE':4, 'B':5, 'C':6, 'N':7, 'O':8, 'F':9, 'NE':10, 'NA':11, 'MG':12, 'AL':13, 'SI':14, 'P':15, 'S':16, 'CL':17, 'AR':18, 'K':19, 'CA':20, 'SC':21, 'TI':22, 'V':23, 'CR':24, 'MN':25, 'FE':26, 'CO':27, 'NI':28, 'CU':29, 'ZN':30, 'GA':31, 'GE':32, 'AS':33, 'SE':34, 'BR':35, 'KR':36, 'RB':37, 'SR':38, 'Y':39, 'ZR':40, 'NB':41, 'MO':42, 'TC':43, 'RU':44, 'RH':45, 'PD':46, 'AG':47, 'CD':48, 'IN':49, 'SN':50, 'SB':51, 'TE':52, 'I':53, 'XE':54, 'CS':55, 'BA':56, 'LA':57, 'CE':58, 'PR':59, 'ND':60, 'PM':61, 'SM':62, 'EU':63, 'GD':64, 'TB':65, 'DY':66, 'HO':67, 'ER':68, 'TM':69, 'YB':70, 'LU':71, 'HF':72, 'TA':73, 'W':74, 'RE':75, 'OS':76, 'IR':77, 'PT':78, 'AU':79, 'HG':80, 'TL':81, 'PB':82, 'BI':83, 'PO':84, 'AT':85, 'RN':86, 'FR':87, 'RA':88, 'AC':89, 'TH':90, 'PA':91, 'U':92, 'NP':93, 'PU':94, 'AM':95, 'CM':96, 'BK':97, 'CF':98, 'ES':99, 'FM':100, 'MD':101, 'NO':102, 'LR':103, 'RF':104, 'DB':105, 'SG':106, 'BH':107, 'HS':108, 'MT':109, 'UUN':110, 'UUU':111, 'UUB':112, 'UUT':113, 'UUQ':114, 'UUP':115, 'UUH':116, 'UUS':117, 'UUO':118,}
RESO_CUTOFF=2.5
GRID_DIVIDE= 2   # how many times we divide the resolution to get the grid spacing
PDBLINE_C= "ATOM      1  C   ALA A   1      15.570  14.283  40.555  1.00  7.75           C"
PDBLINE_O= "ATOM      1  O   ALA A   1      15.570  14.283  40.555  1.00  7.75           O"

def tronque(floatnumArray):
    return [ int(math.ceil(x)) if x%1 >= 0.5 else int(math.floor(x)) for x in floatnumArray]

#PDB-oriented functions

def extract_cryst_card_pdb(pdbfilePath):  #modified from Claudia's alixe library

    for line in open(pdbfilePath):
        m = regexprCRYST1.match(line) # E.G. CRYST1   30.279   91.989   32.864  90.00 112.60  90.00 P 1 21 1      2
        if m:

            unitCellParam=line
            a=float(line[6:15])
            b=float(line[15:24])
            c=float(line[24:33])
            alpha=float(line[33:40])
            beta= float(line[40:47])
            gamma=float(line[47:54])
            spacegroup=line[55:66].strip()
            symbol=1
            try:
                symbol=line[66:70].strip()
            except:
                pass
            out=(a,b,c,alpha,beta,gamma,spacegroup,symbol)

            return out   #returns [a,b,c,alpha,beta,gamma,spacegroup,symbol]
    return None


def extractCoordinatesFromPDB(pathToPDBfile=None, regularExprAtom=regexprATOM2):
    """Extracts coordinates from a pdb file and outputs them in a numpy n x 4 array"""

    PDBorthCoord=np.empty((0,3),float)   #empty array to store the coordinates the first PDB
    nelec_tab=[]
    if pathToPDBfile is not None and os.path.exists(pathToPDBfile):
        natom=0
        unitCellParam=[0,0,0,0,0,0]
        sgnumber = 1
        with open(pathToPDBfile,'r') as f:

            gotCryst = False
            for line in f:
               
                m = regularExprAtom.match(line)

                if not gotCryst:
                    mcryst = regexprCRYST1.match(line) # E.G. CRYST1   30.279   91.989   32.864  90.00 112.60  90.00 P 1 21 1      2
                    if mcryst:
                        a=float(line[6:15])
                        b=float(line[15:24])
                        c=float(line[24:33])
                        alpha=float(line[33:40])
                        beta= float(line[40:47])
                        gamma=float(line[47:54])
                        spacegroup=line[55:66].strip()
                        symbol=1
                        try:
                            symbol=line[66:70].strip()
                        except:
                            pass
                        unitCellParam=(a,b,c,alpha,beta,gamma,spacegroup,symbol)
                        sgnumber = unitCellTools.get_space_group_number_from_symbol(spacegroup)
                        gotCryst  =True
                        print("Unit cell parameters: {} {} {} {} {} {}".format(a,b,c,alpha,beta,gamma))
                        print("Space group {} (number {})".format(spacegroup, sgnumber))
                        print("----------------------")

                elif m:
                    natom+=1

                    #atom coordinates

                    x=float(m.group(12))
                    y=float(m.group(13))
                    z=float(m.group(14))
                    elem=m.group(18).strip().upper()
               
                    # Add lines to the current coordinates
                    PDBorthCoord=np.append(PDBorthCoord,np.array([[x,y,z]]),axis=0)

                    # If the element is not is NELECTRONS, add a density of 1 
                    if elem in NELECTRONS:
                        nelec_tab.append(NELECTRONS[elem])
                    else:
                        nelec_tab.append(1)

        print("----- %s atom coordinates recorded from %s.-----\n"%(natom,pathToPDBfile))
        return natom, PDBorthCoord, nelec_tab, unitCellParam, sgnumber             # returns a 1) the number of atoms, 2) a n x 3 numpy array of orthogonal coordinates and 3) the corresponding electron density at these points
    else:
        print("Problem with your extracting coordinates from PDB file %s, the file does not exist or is not accessible"%pathToPDBfile)
        return None

def fracCoord2electronDensity(orthCoord=None, electronD_array = None, unitCellParam=[50,50,50,90,90,90], resolution = RESO_CUTOFF, sgnumber =1, writePDB=False):
    """ Outputs a numpy 3D array representing the electron density in the unit cell, takes into account space group symmetry operations"""

    gridSpacing = resolution / GRID_DIVIDE

    if orthCoord is not None and electronD_array is not None:

        # Converts input orthogonal coordinates to Fractional coordinates
        deOmat = unitCellTools.deOmat(*unitCellParam[:6])
        omat = unitCellTools.Omat(*unitCellParam[:6])
        symopDic = unitCellTools.get_symops_from_sg_dictionary(sgnumber)
        #print(symopDic)
        fracCoord = unitCellTools.ortho2Frac(deOmat,coordMat=orthCoord, belowOne=True)

        # Fill the unit cell with electron density values (0 if no atom, otherwise the corresponding electron density)
        # First, initialize the Numpy array

        nx = int(float(unitCellParam[0]) / gridSpacing) 
        ny = int(float(unitCellParam[1]) / gridSpacing)
        nz = int(float(unitCellParam[2]) / gridSpacing)

        print("Grid spacing along a: {} pt, b: {} pt, c: {} pt".format(nx, ny, nz))

        unitCellArray = np.zeros((nx,ny,nz), dtype=float)

        # Fill up unitCellArray with Density when a voxel corresponds to an atomic position
        nvox=0
        if writePDB:
            pdbfile= open("frac2ed.pdb",'w')
            sgsymbol=unitCellTools.get_full_symbol_from_sg_number(sgnumber)
            cryst1= unitCellTools.writeCRYSTCARDintoPDB(*unitCellParam,sgsymbol=sgsymbol)
            pdbfile.write(cryst1)

        for operation in symopDic.values():
            # fill up the electron density at all symmetry-equivalent positions

            fracCoordSym = unitCellTools.rotoTranslateFracCoordMat(fracCoord,operation, belowOne=True)
            for i in range(len(fracCoordSym)):
                nvox += 1
                a = fracCoordSym[i,0] * nx
                b = fracCoordSym[i,1] * ny 
                c = fracCoordSym[i,2] * nz

                a, b, c = tronque((a,b,c))    # Voxel coordinates of unitCellArray

                #Make a mirror image of the electron density (because of the sign of the Python FFT)
                unitCellArray[a-1, b-1, c-1] = electronD_array[i]


                if writePDB:
                    orthCoordSym = unitCellTools.frac2Ortho(omat,np.array([[float(a)/nx, float(b)/ny, float(c)/nz]]))
                    line=unitCellTools.replaceATOMrec(inputLine=PDBLINE_C, replaceDic={"serial": nvox, 'x':orthCoordSym[0][0], 'y': orthCoordSym[0][1], 'z':orthCoordSym[0][2] })
                    pdbfile.write(line+"\n")
                


        print("number of voxels assigned : {}".format(nvox))
        if writePDB:
            print("PDB file from fracCoord2electronDensity written as frac2ed.pdb")
            pdbfile.close()
        return unitCellArray #, xdata, ydata, zdata, colors

    else:
        return None

def FT_map2SF(edMap=None,writePHS =False, unitCellParam=None, resolution=RESO_CUTOFF):
    """Fourier transforms a map to a structure factor list, optionally writes a phs file"""
    if edMap is not None:
        #SF=np.fft.fftshift(np.fft.fftn(edMap))
        SF=np.fft.rfftn(np.flip(edMap))
        amplitudes  = np.abs(SF)
        phases = np.angle(SF, deg=True)%360
 
        Gstar = unitCellTools.Gstar(*unitCellParam[:6])
       

        if writePHS:
            with open('map2sf.phs','w') as f:
                for h in range(0, amplitudes.shape[0]):
                    for k in range(0, amplitudes.shape[1]):
                        for l in range(0, amplitudes.shape[2]):
                            #print(phases[h,k,l])
                            resol= unitCellTools.resolution(h,k,l,GstarMatrix=Gstar)
                            #print("h: {}, k: {}, l: {}, resolution: {}".format(h,k,l, resol))
                            if resol >=resolution:
                                indices=(h,k,l)
                                f.write("{:4d}{:4d}{:4d} {:8.2f}{:8.4f}{:8.1f}{:8.2f}\n".format(indices[0], indices[1], indices[2], amplitudes[indices], 0.9, phases[indices], np.sqrt(amplitudes[indices])))

                print("PHS file from map2sf file written as map2sf.phs (cut at {}A resolution)".format(resolution))

        return SF 

def PHS_2_SFarray(phsFilePath=None, unitCellParam=None, resolution=2.0):
    """ Parses a PHS file to create a 3d array of structure factors HKL"""

    if phsFilePath is not None and os.path.exists(phsFilePath) and unitCellParam is not None:

        gridSpacing = resolution / GRID_DIVIDE
        nx = int(float(unitCellParam[0]) / gridSpacing) 
        ny = int(float(unitCellParam[1]) / gridSpacing)
        nz = int(float(unitCellParam[2]) / gridSpacing)

        hmax=0
        kmax=0
        lmax=0

        print("Grid spacing along a: {} pt, b: {} pt, c: {} pt".format(nx, ny, nz))

        hklDic={}
        fomDic={}

        # Retrieving the structure factors from the PHS file:
        with open(phsFilePath, 'r') as f:
            found=False
            nref=0
            for line in f:
                found=True
                m= reHKL.match(line)
                if m:
                    h= int(m.group(1))
                    k= int(m.group(2))
                    l= int(m.group(3))
                    amplitude= float(m.group(4))
                    fom=float(m.group(5))
                    phase = float(m.group(6))
                    sf = amplitude * np.exp(1j*np.radians(phase))
                    nref+=1

                    hmax = h if h>hmax else hmax
                    kmax = k if k>kmax else kmax
                    lmax = l if l>lmax else lmax

                    try:
                        if h>=nx or k>=ny or l>=nz: 
                            print("h: {}, k: {}, l: {}, A: {}, phi: {} fom: {}".format(h,k,l,amplitude, phase,fom))
                        hklDic[(h,k,l)] = sf
                        fomDic[(h,k,l)] = fom
                    except Exception as e:
                        print("problem with indices {}{}{}".format(h,k,l))
                        print(e)

        if found:
            HKLarray = np.zeros((hmax+1,kmax+1,lmax+1), dtype=complex)
            for (hkl_tuple, sf) in hklDic.items():
                HKLarray[hkl_tuple] = sf   # store the structure factor if the indices exist
            print("PHS_2_SFarray: hmax+1: {}, kmax+1: {}, lmax+1: {}".format(hmax+1,kmax+1,lmax+1))
            print("{} reflections parsed from {}".format(nref, phsFilePath))

            return HKLarray, (nx,ny,nz), fomDic
        else:
            print("PHS_2_SFarray: No reflections found in phs file {}".format(phsFilePath))
            return None, None, None

    else:
        print("ERROR PHS_2_SFarray, file {} cannot be opened!".format(phsFilePath))
        return None, None, None

def FT_SF2electronDens(SFarray=None, writeMAP=False,unitCellParam=None,sgnumber=1, shape=(50,50,50)):
    """Fourier transforms a structure factor file to an electron density map, optionally writes a (Binary map) """ 
    if SFarray is not None:
        electronDensity = np.fft.irfftn(SFarray, s=shape)
        print("shape of HKL input:", SFarray.shape)
        print("shape of electron density:", electronDensity.shape)

        # Note it has to be inverted because of the python FT conventions ?
        electronDensity = np.flip(electronDensity)

        nrow, ncol, nsec = electronDensity.shape

        omat = unitCellTools.Omat(*unitCellParam[:6])


        # test: Write a PDB file out of this density
        if writeMAP:

            pdbfile= open("sf2ed.pdb",'w')
            sgsymbol=unitCellTools.get_full_symbol_from_sg_number(sgnumber)

            cryst1= unitCellTools.writeCRYSTCARDintoPDB(*unitCellParam[:6],sgsymbol=sgsymbol)
            pdbfile.write(cryst1)
            nvox=0
            edMEAN = np.mean(electronDensity)
            edSTD = np.std(electronDensity)
            threshold= edMEAN + 1.5*edSTD

            for x in range(nrow):
                for y in range(ncol):
                    for z in range(nsec):

                        if electronDensity[x,y,z] >= threshold:
                            nvox +=1
                            xfrac, yfrac, zfrac = (1.0+x) /nrow, (1.0*y)/ncol, (1.0*z) /nsec
                            orthCoordSym = unitCellTools.frac2Ortho(omat,np.array([[xfrac, yfrac, zfrac]]))
                            line=unitCellTools.replaceATOMrec(inputLine=PDBLINE_O, replaceDic={"serial": nvox, 'x':orthCoordSym[0][0], 'y': orthCoordSym[0][1], 'z':orthCoordSym[0][2] })
                            pdbfile.write(line+"\n")
                        
            print("MAP (PDB file) from FT_SF2electronDens written as sf2ed.pdb")
            pdbfile.close()

        return electronDensity

def wMPD(SFarray1, SFarray2, all=True, fomDic=None, noweight=True):
    """ 
    Compute the mean phase difference between phases extracted from arrays of structure factors, make the weights later
    SFarray1 will come from a PDB file while SFarray2 from a PHS file
    """
    print("\n----> MPD calculation")
    print("shape of structure factor array 1: {}".format(SFarray1.shape))
    print("shape of structure factor array 2: {}".format(SFarray2.shape))
    commonshape= [min(x,y) for x,y in zip(SFarray1.shape,SFarray2.shape)]
    print("Common shape: {}\n".format(commonshape))
    SFarray1 = SFarray1[:commonshape[0], :commonshape[1],:commonshape[2]]
    SFarray2 = SFarray2[:commonshape[0], :commonshape[1],:commonshape[2]]

    phaseSet1 = np.angle(SFarray1, deg=True)%360
    phaseSet2 = np.angle(SFarray2, deg=True)%360

    if fomDic is None:
        weights= np.abs(SFarray2)                     # Amplitudes of the PHS file used as weights
    else:
        weights=np.zeros(commonshape,dtype=float)
        for h in range(commonshape[0]):
            for k in range(commonshape[1]):
                for l in range(commonshape[2]):
                    if (h,k,l) in fomDic:
                        try:
                            weights[h,k,l] = fomDic[(h,k,l)]
                        except:
                            pass


    if noweight:
        weights[:,:,:]=1

    del(SFarray1)
    del(SFarray2)

    #print(phaseSet2 - phaseSet1)

    if all:
        return np.absolute(np.sum(np.multiply((phaseSet1 - phaseSet2), weights))  / np.sum(weights))

    else:
        deltaPhiSum=0
        weightSum=0
        for h in range(commonshape[0]):
            for k in range(commonshape[1]):
                for l in range(commonshape[2]):
                    if weights[h,k,l] != 0:
                        deltaPhiSum += (phaseSet1[h,k,l] - phaseSet2[h,k,l]) * weights[h,k,l]
                        weightSum += weights[h,k,l]

        return np.absolute(deltaPhiSum / weightSum)


def map2mapCC(electronDens1, electronDens2, all=False):
    """ 
    Calculate the correlation coefficient between 2 maps, given as voxel 3d arrays
    if all is False, it will only consider voxels which have a density greater than 1 sigma in absolute value
    all True uses Numpy (faster)
    """

    # The formula for the Pearson CC is E[ (X-mean(X)) (Y-mean(Y))] / (sigmaX*sigmaY)

   # print(zip(electronDens1.shape,electronDens2.shape))
    #Only keep the common parts of the two eletron densities
    print("\n----> CC map / model calculation")
    print("shape of electron density 1: {}".format(electronDens1.shape))
    print("shape of electron density 2: {}".format(electronDens2.shape))
    commonshape= [min(x,y) for x,y in zip(electronDens1.shape,electronDens2.shape)]
    electronDens1 = electronDens1[:commonshape[0], :commonshape[1],:commonshape[2]]
    electronDens2 = electronDens2[:commonshape[0], :commonshape[1],:commonshape[2]]

    print("Common shape: {}\n".format(commonshape))
    # substract the mean
    electronDens1 -= np.mean(electronDens1)
    electronDens2 -= np.mean(electronDens2)

    if all:
        if electronDens1.shape == electronDens2.shape:
            return np.mean(np.multiply(electronDens1, electronDens2)) / (np.std(electronDens1) * (np.std(electronDens2)))

        else:
            print("Shapes are not equal: {} and {}".format(electronDens1.shape, electronDens2.shape))
            return None
    else:
        # compare only voxels who have a standardized density superior to 1
        #divide by std:
        electronDens1 /= np.std(electronDens1)
        electronDens2 /= np.std(electronDens2)
        liste1=[]
        liste2=[]
        for i in range(commonshape[0]):
            for j in range(commonshape[1]):
                for k in range(commonshape[2]):
                    if np.absolute(electronDens1[i,j,k])>=1 and np.absolute(electronDens2[i,j,k])>1:
                        liste1.append(electronDens1[i,j,k])
                        liste2.append(electronDens2[i,j,k])
        #print(liste1)
        #print("---\n\n\n")
        #print(liste2)
        liste1 = np.array(liste1)
        liste2 = np.array(liste2)
        liste1 -= np.mean(liste1)
        liste2 -= np.mean(liste2)
        return np.mean(np.multiply(liste1, liste2)) / (np.std(liste1) * (np.std(liste2)))

    


#---------------------- MAIN PROGRAM
if __name__ == '__main__':

    if len(sys.argv)>2 and os.path.exists(sys.argv[1]):
        PDBfile=sys.argv[1]
        PHSfile=sys.argv[2]

        RESOLUTION= 2.5

        # Extract info from the input PDB file
        natom, orthCoord, ed_raw, unitCellParam, sgnumber = extractCoordinatesFromPDB(PDBfile)

        # Create the corresponding electron density array
        electronDensPDB = fracCoord2electronDensity(orthCoord=orthCoord, electronD_array = ed_raw, unitCellParam=unitCellParam[:6], resolution = RESOLUTION, sgnumber= sgnumber, writePDB=True)
        SFarrayPDB= FT_map2SF(edMap=electronDensPDB,writePHS = True, unitCellParam=unitCellParam[:6], resolution=RESOLUTION)

        # Transforming to SF
        SFarrayPHS, shape, fomDic = PHS_2_SFarray(phsFilePath=PHSfile, unitCellParam=unitCellParam[:6], resolution=RESOLUTION)

        # Now transforming back to electron density
        electronDensPHS = FT_SF2electronDens(SFarray=SFarrayPHS, writeMAP=True,unitCellParam=unitCellParam[:6],sgnumber=sgnumber,shape=shape)
        mpd = wMPD(SFarrayPDB, SFarrayPHS, fomDic=fomDic)
        del(SFarrayPHS)
        del(SFarrayPDB)
        
        #CC
        cc =  map2mapCC(electronDensPDB, electronDensPHS, all=True)

        print("MPD id {}".format(mpd))
        print("CC is {}".format(cc))

    else:
        print("Please enter a PDB file and a PHS file to compare")

