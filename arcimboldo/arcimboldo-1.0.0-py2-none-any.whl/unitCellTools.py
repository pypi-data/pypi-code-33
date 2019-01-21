#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import json
from sklearn.neighbors import KernelDensity
plt.switch_backend('agg')   #To avoit Matplotlib error when launching from a distant machine
import re
import os
import sys
#from itertools import combinations as combinaisons
from SPACE_GROUPS import *

###SET OF UTILITIES TO MAKE VARIOUS CALCULATIONS FROM UNIT CELL PARAMETERS
###Nicolas August 2017


def Omat(a=234.5780,b=234.5780,c=406.1230,alpha=90.0,beta=90.0,gamma=120):
    """returns the orthogonalization matrix of the unit cell (to converte fractional coordinates into orthogonal)"""

    #converting the input angles in radiants
    (alpha,beta,gamma)=[float(x)*np.pi/180.0 for x in (alpha,beta,gamma)]

    b1=float(b*np.cos(gamma))
    b2=float(b*np.sin(gamma))
    c1=float(c*np.cos(beta))
    c2=float(c*(np.cos(alpha) - np.cos(gamma)*np.cos(beta))/np.sin(gamma))
    c3=float(c*np.sqrt(1 - np.square(np.cos(beta)) - np.square((np.cos(alpha) - np.cos(gamma)*np.cos(beta))/np.sin(gamma) ) ))

    #rounding to zero for very small number (numpy doesn't do it by default)
    (b1,b2,c1,c2,c3)=[x if not np.allclose(0,x) else 0.0 for x in (b1,b2,c1,c2,c3)]

    #The orthogonalization matrix
    OrthoMat=np.array([ [a, b1, c1], [0.0, b2, c2], [0.0, 0.0, c3]])

    return OrthoMat

def deOmat(a=234.5780,b=234.5780,c=406.1230,alpha=90.0,beta=90.0,gamma=120.0):
    """Returns the deorthogonalization matrix (inverse of Omat) to convert from cartesian to fractional coordinates"""
    return np.linalg.inv(Omat(a=a,b=b,c=c,alpha=alpha,beta=beta,gamma=gamma))

def Gmat(a=234.5780,b=234.5780,c=406.1230,alpha=90.0,beta=90.0,gamma=120):
    """returns the metric tensor, to calculate all sorts of things in the unit cell (Volume, distances, d-spacing etc) working in FRACTIONAL coordinates"""

    #converting the input angles in radiants
    (alpha,beta,gamma)=[x*np.pi/180.0 for x in (alpha,beta,gamma)]

    #Scalar products to fill the matrix
    aa=np.square(a)
    ab=a*b*np.cos(gamma)
    ac=a*c*np.cos(beta)
    bb=np.square(b)
    bc=b*c*np.cos(alpha)
    cc=np.square(c)

    #rounding to zero for very small number (numpy doesn't do it by default)
    (aa,ab,ac,bb,bc,cc)=[x if not np.allclose(0,x) else 0 for x in (aa,ab,ac,bb,bc,cc)]

    #The metric tensor itself
    Gmatrix=np.array([ [aa,ab,ac], [ab,bb,bc], [ac,bc,cc]])

    return Gmatrix


def Gstar(a=234.5780,b=234.5780,c=406.1230,alpha=90.0,beta=90.0,gamma=120):
    """returns the metric tensor of the reciprocal lattice (which turns out to be the inverse of G)"""

    return np.linalg.inv(Gmat(a,b,c,alpha,beta,gamma))

def unitCellVolume(a=234.5780,b=234.5780,c=406.1230,alpha=90.0,beta=90.0,gamma=120):
    """Volume of the unit cell"""
    det=np.linalg.det(Gmat(a,b,c,alpha,beta,gamma))
    return np.sqrt(det)

def resolution(h,k,l,GstarMatrix=Gstar(a=5,b=6,c=5.41,alpha=90,beta=90,gamma=115)):
    """resolution of a reflection hkl i.e [hkl]G*[hkl]T"""
    vecteur=np.array([h,k,l])

    prod1=np.dot(GstarMatrix,vecteur)
    prod2=np.dot(vecteur,prod1)

    if (prod2 !=0):
        return np.sqrt(1/prod2)
    else:
        return 0

def magnitude(Gmat,fracCoord=np.array([0.071,0.182,0])):
    """Magnitude of a vector in fractional coordinates ie: sqrt of v G v"""
    prod2=np.dot(Gmat,fracCoord)
    prod1=np.dot(fracCoord,prod2)
    return np.sqrt(prod1)

def distanceFrac(Gmat,fracCoord1=np.array([0.2,0.4,0.6]),fracCoord2=np.array([0.3,0.5,0.2])):
    """Calculation of distances in A between two points (vectors in the fractional coordinate system)ie: sqrt ofv1 G v2"""
    difference= fracCoord2  - fracCoord1
    prod2=np.dot(Gmat,difference)
    prod1=np.dot(np.transpose(difference),prod2)
    return np.sqrt(prod1)

def distanceFracMat(Gmat,Matcoord=np.array([[0.2,0.4,0.6], [0.5,0.5,0.6], [0.2,0.5,0.6]]),fracCoord=np.array([0.3,0.5,0.2])):
    """from a column of coordinate vectors, and an external coordinate vector, returns an array of the distance vec1 vec2"""
    Matcoord=Matcoord - fracCoord
    prod2=np.dot(Gmat,np.transpose(Matcoord))
    prod1=np.dot(Matcoord,prod2)
    return np.sqrt(np.diagonal(prod1))


def distanceOrth(vec1=np.array([0,1,2]),vec2=np.array([3,4,5])):
    """Distance between two points (vectors) given in orthogonal coordinates (a simple dot product) the result should be the same as within the orthogonal basis"""
    return np.linalg.norm(vec2-vec1)


####PDB related tools

def ortho2Frac(deOmat,coordMat=np.array([[1,2,3],[4,5,6],[7,8,9],[10,11,12]]), belowOne=False):
    """transform cartesian coordinates following a space group symmetry operation
    if belowOne is True, all the fractional coordinates will be brought back to their equivalent (modulo 1) before output
    """
    matrixOut = np.transpose(np.dot(deOmat,np.transpose(coordMat)))
    if belowOne:
        matrixOut= matrixOut %1
    return matrixOut

def frac2Ortho(Omat,FracCoordMat=np.array([[0.1,0.2,0.3],[0.4,0.5,0.6],[0.7,0.8,0.9],[0.1,0.11,0.12]]), belowOne=False):
    if belowOne:
        FracCoordMat= FracCoordMat %1
    return np.transpose(np.dot(Omat,np.transpose(FracCoordMat)))

# Outdated see rotoTranslateFracCoordMat
# def generate_symmetric(fracCoordMAt=np.array([[0,0.2,0.5],[0.1,0.4,0.9],[0.7,0.2,0.3]]),rotVec=[0,0,0],transVec=[0,0,0]):

#     rotation=np.array(rotVec)
#     translation=np.array(transvec)
#     outVec=np.dot(fracCoordMAt,rotation)
#     outVec=np.add(outVec,translation)

#     return outVec

def centreOfMass(coordMat=np.array([[2,3,4],[1,2,3],[4,7,6],[8,9,10]])):
    """Compute the centre of mass of a protein from cartesian coordinates (given as a n x 3 numpy matrix where rows are x y z)"""

    return np.average(coordMat,axis=0)


def writeCRYSTCARDintoPDB(a,b,c,alpha,beta,gamma,sgsymbol='P 1 2 1',znum=1):
    """from a list such as the one output by extract_cryst_card_pdb, format it to write a PDB record"""
    return "CRYST1%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f %-11s%4d\n"%(a,b,c,alpha,beta,gamma, sgsymbol, znum)

def extract_cryst_card_pdb(pdbfilePath):  #modified from Claudia's alixe library

    for line in open(pdbfilePath):
        m = regexprCRYST1.match(line) # E.G. CRYST1   30.279   91.989   32.864  90.00 112.60  90.00 P 1 21 1      2
        if m:

            unitcellParam=line
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

def rotoTranslateFracCoord(npvecFrac, operation,belowOne=False):
    """ applies a translation and a rotation from a spacegroup symop value"""

    vecTra= np.array(operation['tra'])
    matRot= np.array(operation['rot'])
    rotatedVec= np.dot(matRot,npvecFrac)   #back with a row vector
    rotoTranslatedFracCord = rotatedVec + vecTra
    if belowOne:
        rotoTranslatedFracCord %=1

    return rotoTranslatedFracCord

def rotoTranslateFracCoordMat(npMatFrac, operation, belowOne=False):
    """ applies a translation and a rotation from a spacegroup symop value, to a matrix o nx3 fractional coordinates"""

    vecTra= np.array(operation['tra'])
    matRot= np.array(operation['rot'])

    rotatedFracMat= np.dot(matRot,npMatFrac.T)   #back with a row vector
    rotoTranslatedFracCord =rotatedFracMat.T + vecTra
    if belowOne:
        rotoTranslatedFracCord %=1

    return rotoTranslatedFracCord

####Regular expression to parse a PDB file line
regexprATOM=re.compile(r"(.{6})([\d\.\s]{5})(\s)(.{4})(.{1})(.{3})(\s)(.{1})(.{4})(.{1})(.{3})(.{8})(.{8})(.{8})(.{6})(.{6})(\s{10})(.{2}).*")
def replaceATOMrec(inputLine="", replaceDic={"resName": "ALA"}):
    """NS, Easily replace a string element from an ATOM record in a ATOM line from a pdb file"""

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
    out = regexprATOM.sub(subLine, inputLine)
    return out
#########################""
# G= Gmat(a=9.010,b=8.926,c=5.344,alpha=44.27,beta=116.43,gamma=119.34)

# #print resolution(2,1,0,Gs)

# print magnitude(G)

#print(centreOfMass)


######REGULAR EXPRESSIONS
regexprCRYST1=re.compile(r"^CRYST1")
regexprATOM2=re.compile(r"(ATOM  |HETATM)([\d\.\s]{5}).{10}(.{1}).{8}(.{8})(.{8})(.{8}).*")
#regx=re.compile(r"(([\-\+])?(\d)?[Xx]([\+\-\d/\.]+)?)?\s*(([\-\+])?(\d)?[Yy]([\+\-\d/\.]+)?)?\s*(([\-\+])?(\d)?[Zz]([\+\-\d/\.]+)?)?")
regx=re.compile(r"((?:[\+\-])?[\d\./]+)?(([\+\-])?([/.\d]{0,})[xX])?(([\+\-])?([/.\d]{0,})[yY])?(([/\+\-])?([.\d]{0,})[zZ])?([\+\-\d\./]+)?$")
######SPACE GROUPS functions

def harkerSections(space_group_key=96, returnObjectVec=False):
    """ Derives and outputs the Harker sections for any spacegroup"""
    #operations=dictio_space_groups[space_group_key]['symm_cards'].rstrip()  #removes the '\n' at the end
    #listSym= operations.split(',')
    #Transform the x,y,z notation into vectors
    class Vecxyz:
        """ vectors describing either equivalent positions or Harker sections"""
        def __init__(self, vec=('2x+y+0.5', '-2y+1/3', '-2z+0.5'), tens=None, tra=None):
            if tens is not None and tra is not None:
                self.tenseur=tens
                self.tra=tra
                self.vec=self.makelineVecFromArrays(tens,tra)
            else:
                self.vec=vec
                self.tenseur, self.tra=self.makeTensor(vec)
            self.vecsimple= self.makelineVecFromArrays(self.tenseur,self.tra,precision=False)  #This one is for printing out (short numbers)

        def __str__(self):
            """ """
            out=""
            for elem in self.vecsimple:
                out+=str(elem)+'\t'
            return out

        def __add__(self,other):
            """ Adds up the numpy matrices of each object together"""
            sumTens=np.add(self.tenseur,other.tenseur)
            sumTra=np.add(self.tra, other.tra)
            sumTra %=1
            #vec=self.makelineVecFromArrays(sumTens,sumTra)
            return Vecxyz(vec=None, tens=sumTens, tra=sumTra)

        def __sub__(self,other):
            """ subtract the numpy matrices of each object together"""
            sumTens=np.subtract(self.tenseur,other.tenseur)
            sumTra=np.subtract(self.tra,other.tra)
            sumTra %=1
            #vec=self.makelineVecFromArrays(sumTens,sumTra)
            return Vecxyz(vec=None, tens=sumTens, tra=sumTra)

        def constantCoord(self):
            """ Outputs the coordinates that don't vary (which define then a line or a plane in Patterson space"""
            out={}
            axes=('x','y','z')
            for i, coord in enumerate(self.vecsimple):
                if not re.match(r".*[XxYyZz]",coord):
                    out[axes[i]]=coord

            return out

        def harkerSec(self):
            """ outputs a tuple defining the plane of the Harker section, ex : for z=0.5, it would output ((0,1), (0,1), (0.5,0.5))"""
            out=[]
            for i,coord in enumerate(self.vec):
                if not re.match(r".*[XxYyZz]",coord):
                    coord=self.tra[i,i]
                    out.append((coord,coord))
                else:
                    out.append((0,1))

            return tuple(out)

        def applyTransfo(self,xyzVec=np.array([1,1,1])):
            """ Apply the Patterson vector to a set of  fractional coordinates x,y,z"""
            matrot=self.tenseur
            vecTra=np.sum(self.tra,axis=1)   #column translation vector
            outvec=np.dot(matrot,xyzVec) +  vecTra
            return outvec%1           
    
        @staticmethod
        def makelineVecFromArrays(tenseur,tra,precision=True):
            out=['','','']
            letters=('x','y','z')
            for i in range(3):
                for j in range(3):
                    if tenseur[i,j] != 0:
                        if tenseur[i,j] not in (-1, 1):
                            out[i] += "{:+d}".format(tenseur[i,j])
                        elif tenseur[i,j] == 1:
                            out[i] +='+'
                        elif tenseur[i,j] == -1:
                            out[i] +='-'
                        out[i] += letters[j]
                if tra[i,i] != 0:
                    signe = '+' if tra[i,i]>0 else ''
                    if precision:
                        out[i] += "{}{:f}".format(signe,tra[i,i])
                    else:
                        out[i] += "{}{:.2f}".format(signe,tra[i,i])

            #add zero if a box is empty (precisely because it is 0x + 0y + 0z)
            out=['0' if s =='' else s for s in out]
            #print(out)
            return out

        #regx=re.compile(r"(([\+\-])?([\+\-\d\./]+)?([/.\d]{0,})[xX])?(([\+\-])?([\+\-\d\./]+)?([/.\d]{0,})[yY])?(([/\+\-])?([\+\-\d\./]+)?([.\d]{0,})[zZ])?([\+\-\d\./]+)?$")
        @staticmethod
        def makeTensor(vec):
            """ Analyses the pattern and produce an equivalent tensor + translation representation"""
            outTens=np.ones((3,3), dtype=int)
            outTrans=np.zeros((3,3))

            for i,item in enumerate(vec):
                item=re.sub('\s+', '', item)          #remove spaces from the line
                m= regx.match(item)                   #match a record of the type -2y+1/3
                if m:

                    traforwd=m.group(1)

                    letterX=m.group(2)
                    firstSignX=m.group(3) 
                    multX=m.group(4)

                    letterY=m.group(5)
                    firstSignY=m.group(6)
                    multY=m.group(7)

                    letterZ=m.group(8)
                    firstSignZ=m.group(9)
                    multZ=m.group(10)

                    tra=m.group(11)

                    for j, signe in enumerate((firstSignX, firstSignY, firstSignZ)):
                       # print("j,signe is %s %s"%(j,signe))
                        if signe == '-':
                            outTens[i,j] *= -1

                    for j, mult in enumerate((multX, multY, multZ)):
                       # print("j, mult is %s %s"%(j,mult))
                        if mult:
                            outTens[i,j] *= float(mult)

                    for j, letter in enumerate((letterX, letterY, letterZ)):
                       # print("j, letter is %s %s"%(j,letter))
                        if letter:
                            outTens[i,j] *= 1
                        else:
                            outTens[i,j] *= 0

                    if traforwd:
                        if '/'in traforwd:
                            num=traforwd.split('/')
                            tra=float(num[0]) / float(num[1])
                        outTrans[i,i] += float(traforwd)%1

                    if tra:
                        if '/'in tra:
                            num=tra.split('/')
                            tra=float(num[0]) / float(num[1])
                        outTrans[i,i] += float(tra)%1
                else:
                    print("no match, %s"%list(vec))

            return outTens, outTrans
    #-------------------------------------------MAIN FUNCTION HARKER SECTIONS

    v=Vecxyz(('x', 'y', 'z'))
    listeHarker=[]
    centeringpoints=get_centering_points(space_group_key)
    symmPosList=dictio_space_groups[space_group_key]['symm_cards']

    # Goes through the symm card and substract equivalent position from ('x', 'y', 'z') to see if that leads to vector bearing constant coordinates (Harker sections)
    if symmPosList:     #list of equivalent position for that space group
        for centeringpt in centeringpoints:
            pt=[str(x) for x in centeringpt]
            v2= v + Vecxyz(pt)
            for position in symmPosList:
                vec=position.rstrip() #removes the \n
                vec=re.sub('SYMM','',vec)
                vec=re.sub('\s+','',vec)
                vec=Vecxyz(vec.split(','))
                listeHarker.append(v2 -vec)

            # print(v)
            # print(vec)
            # print("-----------------------")
            # print(v-vec)
            # print("\n")

    print("\n-------------------------------------------------------")
    print("Harker sections for space group %s (number %s)"%(get_full_symbol_from_sg_number(space_group_key), space_group_key))
    print("-------------------------------------------------------")
    print("Section\t\tPatterson vector")

    # Filtering the output (remove if there is no vector with constant coordinate)
    listeHarker = [v for v in listeHarker if v.constantCoord()]

    #Now sorting
    def cmp_hark(v1,v2):
        a=v1.constantCoord().keys()[0]
        b=v2.constantCoord().keys()[0]
        if a=='x' and b !='x':
            return -1
        elif a=='y' and b =='z':
            return -1
        elif a ==b:
            return 0
        else:
            return 1
    listeHarker.sort(cmp_hark)

    harkerListOut=[]
    listcheckout=[]
    for harkervec in listeHarker:
        constcoord=harkervec.constantCoord()
        if returnObjectVec:                     #Here we return the object as a whole so that we can access to its transformations matrices to apply to fractional coordinates
            harkerListOut.append(harkervec)
        else:                           
            if not constcoord in listcheckout:
                listcheckout.append(constcoord)
                harkerListOut.append(harkervec.harkerSec())     # return a tuple ((0,1), (0,1), (0.25,0.25)) defining the Haeker plane, add it to the output list that will be returned
        
        print("{}\t{}".format(constcoord,harkervec))            #print out constant sections and the corresponding Patterson vectors

 
    return harkerListOut


def get_symops_from_sg_dictionary(space_group_key):
    if isinstance(space_group_key, int):
        symops = dictio_space_groups[space_group_key]['symops']
    elif isinstance(space_group_key, str):
        space_group_key = int(space_group_key)
        symops = dictio_space_groups[space_group_key]['symops']
    else:
        print "get_symops_from_sg_dictionary: Space group key is not valid"
        sys.exit(0)
    return symops

def get_asu_borders_from_sg_dictionary(space_group_key):
    if isinstance(space_group_key, int):
        asu = dictio_space_groups[space_group_key]['asymmetric_unit']
    elif isinstance(space_group_key, str):
        space_group_key = int(space_group_key)
        asu = dictio_space_groups[space_group_key]['asymmetric_unit']
    else:
        print "get_asu_borders_from_sg_dictionary: Space group key is not valid"
        sys.exit(0)
    return asu

def get_origins_from_sg_dictionary(space_group_key):
    # EXAMPLE: 'origins_list': [[0.0, 0.0, 0.0], [1/2.0, 1/2.0, 1/2.0]],'polar': False
    if isinstance(space_group_key, int):
        origins = dictio_space_groups[space_group_key]['origins_list']
        polar_bool = dictio_space_groups[space_group_key]['polar']
    elif isinstance(space_group_key, str):
        space_group_key = int(space_group_key)
        origins = dictio_space_groups[space_group_key]['origins_list']
        polar_bool = dictio_space_groups[space_group_key]['polar']
    else:
        print "Space group key is not valid"
        return None
    return polar_bool, origins


def get_latt_from_sg_dictionary(space_group_key):
    if isinstance(space_group_key, int):
        latt = dictio_space_groups[space_group_key]['latt']
    elif isinstance(space_group_key, str):
        space_group_key = int(space_group_key)
        latt = dictio_space_groups[space_group_key]['latt']
    else:
        print "Space group key is not valid"
        sys.exit(0)
    return latt


def get_space_group_number_from_symbol(space_group_string):
    for _, key in enumerate(dictio_space_groups.iterkeys()):
        search_string = ''.join(space_group_string.split())
        current_string = ''.join(dictio_space_groups[key]["symbol"].split())
        if search_string == current_string:
            print "\n Space group string given: ", space_group_string, "has been found in the dictionary as number", key
            return key
    # Only if we didn't return any value
    print "Space group not found"
    return None

def get_short_symbol_from_sg_number(sgnumber):
    return dictio_space_groups[sgnumber]['short_symbol']

def get_full_symbol_from_sg_number(sgnumber):
    return dictio_space_groups[sgnumber]['symbol']

def get_multiplicity_from_sg_dictionary(space_group_symbol):
    m=0
    space_group_key = get_space_group_number_from_symbol(space_group_symbol)
    if isinstance(space_group_key, int):
        symops = dictio_space_groups[space_group_key]['multiplicity']
    elif isinstance(space_group_key, str):
        space_group_key = int(space_group_key)
        symops = dictio_space_groups[space_group_key]['multiplicity']
    else:
        print "Space group key is not valid"
        sys.exit(0)
    return symops

def lines_for_writing_res(sgnumber):
    """  Retrieve the 'short_symbol', symm_cards' and 'latt' entries for a spacegroup
     in order to write a RES or HAT file, outputs it as a multiline string to put into a file"""

    clefs=['latt', 'symm_cards']
    sgSubDic= {k:dictio_space_groups[sgnumber][k] for k in clefs if k in dictio_space_groups[sgnumber]}

    out=""
    out+= '-'+ sgSubDic['latt']+'\n'    # lattice type (put a minus in front for non centrosymmetric sg)
    for symm in sgSubDic['symm_cards']:   #symmetry
        out+= symm.upper()
        out+='\n'
    return out


def get_centering_points(space_group_key):
    """ NS: I need this to calculate Harker sections"""
    centerings={'P': ((0,0,0),), 'A': ((0,0,0), (0, 0.5,0.5)), 'B': ((0,0,0), (0.5, 0, 0.5)), 'C':((0,0,0), (0.5,0.5,0)), 'I': ((0,0,0), (0.5, 0.5, 0.5)), 'F': ((0,0,0), (0.5,0.5,0), (0.5,0,0.5), (0,0.5,0.5)), 'H': ((0,0,0), (2./3, 1./3,1./3), (1./3, 2./3, 2./3)), 'R': ((0,0,0),) }
    if isinstance(space_group_key, int):
        symbol = get_full_symbol_from_sg_number(space_group_key)[0]
        #print ("LATTICE TYPE:%s"%symbol)
        #print("Centering points:")
        #print(centerings[symbol])
        return(centerings[symbol])
    else:
        try:
            return(centerings[space_group_key[0]])
        except:
            return ((0,0,0))

def shift_origin(pdbfilePath):
    """Shift the coordinates of a given PDB file along all possible origin shifts"""

    crystcard=extract_cryst_card_pdb(pdbfilePath)    #returns [a,b,c,alpha,beta,gamma,spacegroup,symbol]
    if crystcard==None:
        print "Problem: %s is not a valid PDB file, skipping."%pdbfilePath
        return
    (a,b,c,alpha,beta,gamma)=crystcard[0:6]
    space_group_key=get_space_group_number_from_symbol(crystcard[6])
    (polarbool,origins)=get_origins_from_sg_dictionary(space_group_key)

    #Don't take identity:
    origins=origins[1:]
    print "Origins shifts are %s"%origins

    Omatrix=Omat(a,b,c,alpha,beta,gamma)
    deOmatrix=deOmat(a,b,c,alpha,beta,gamma)

    for i,orig in enumerate(origins):
        #pdbout
        fileOut=os.path.basename(pdbfilePath)    #myfile.pdb
        fileOut=os.path.splitext(fileOut)     #myfile
        if fileOut[1].lower() not in ('.pdb','.pda','.ent'):    #If a non-pdb file has been entered
            print "Problem: %s is not a valid PDB file, skipping."%pdbfilePath
            return
        else:
            fileOut=fileOut[0] + "SHIFTED"+str(i+1)+".pdb"
            out = open(fileOut, 'w')

        #########
        towrite="REMARK   1 ORIGIN SHIFT:%s\n"%orig
        orig=[x if type(x) in (int,float) else 0 for x in orig ]    #don  move along the polar axis if there is any


        for line in open(pdbfilePath):
            m=regexprATOM2.match(line)
            if m:
                orthVec=np.array([float(m.group(4)), float(m.group(5)), float(m.group(6))])
                fracVec=ortho2Frac(deOmatrix,orthVec)
                fracVec= fracVec + orig
                orthVecShifted=frac2Ortho(Omatrix,fracVec)
                line = replaceATOMrec(line, {'x': orthVecShifted[0],'y': orthVecShifted[1], 'z': orthVecShifted[2]})

            towrite+= line

        #Writing the output file for this origin
        out.write(towrite)
        out.close()

#Unit cell content analysis functions:
def kde_sklearn(x, x_grid=np.linspace(0,100, 500), bandwidth=1.8, **kwargs):
    """Kernel Density Estimation with Scikit-learn"""
    kde_skl = KernelDensity(bandwidth=bandwidth, **kwargs)
    kde_skl.fit(x[:, np.newaxis]) #One datapoint per line

    # score_samples() returns the log-likelihood of the samples
    log_pdf = kde_skl.score_samples(x_grid[:, np.newaxis])
    return np.exp(log_pdf)

def unitCellcontent(MW=136163.42, unitCellParam=[115.629, 116.96, 401.554, 90, 90, 90], multiplicity=4, resolution=3.94, moleculeType="protein", outputFig=True, outputDir="."):

    #paramters for calculating the Matthews coefficient
    unitCellVol=unitCellVolume(unitCellParam[0],unitCellParam[1],unitCellParam[2],unitCellParam[3],unitCellParam[4],unitCellParam[5])
    asVolume=unitCellVol / float(multiplicity)

    maxAllowedVs=87
    minAllowedVs=12
    delta=0.75
    
    #Now import the data (protein-type only by default)
    

    if moleculeType == "mix":
        VSfile="mattprob_data_tables_2013/pdb_02_06_2013_mix_sorted_flagged_highest_cs.json"

    elif moleculeType == "nucleicAcid":
        VSfile="mattprob_data_tables_2013/pdb_02_06_2013_nuc_sorted_flagged_highest_cs.json"
        #dataProt=pd.read_csv(os.path.join(os.path.abspath(sys.path[0]),"mattprob_data_tables_2013/pdb_02_06_2013_nuc_sorted_flagged_highest_cs.csv"))
    else:         #protein by default
        VSfile="mattprob_data_tables_2013/pdb_02_06_2013_pro_sorted_flagged_highest_cs.json"
        #dataProt=pd.read_csv(os.path.join(os.path.abspath(sys.path[0]),"mattprob_data_tables_2013/pdb_02_06_2013_mix_sorted_flagged_highest_cs.csv"))

    with open(os.path.join(os.path.abspath(sys.path[0]),VSfile)) as f:        #load the json file into a dictionary
        dataProt=json.load(f)


    #and choose all those whose resolution is smaller (better) than what we have. Use dictionary comprehension to replace Pandas dataframe slicing
    #dataProtTrunc= dataProt[float(dataProt['resol'])<=resolution]

    #Extract only the 'vs' column
    #VsData= dataProtTrunc['vs']
    #take all the structures within more or less one angstrom
    VsData=np.array([float(val['vs']) for val in dataProt.values() if (float(val['resol'])>= (resolution -delta) and float(val['resol'])<= (resolution+delta))])
    nEntriesRetained=len(VsData)
    print("REMARK: number of total entries for %s: %s"%(moleculeType, len(dataProt.keys())))
    print("REMARK: kernel distribution calculated from %s entries with resolution in between %s and %s angstroms."%(nEntriesRetained, resolution +delta, resolution -delta))

    #Plot the distribution and kernel-smooth
    x_grid=np.linspace(0,100, 500) #500 points from 0 to 100
    kernelDensity = kde_sklearn(VsData,x_grid)


    #Find the max of your density
    maxDens= np.amax(kernelDensity)
    indexMax= np.argmax(kernelDensity)
    solventPeak=x_grid[indexMax]

    #Now from the max solvent value find the closest ones that match your protein
    nsolventContentTab=[(nmol,100*(1 - 1.230/(asVolume/(nmol * MW)))) for nmol in range(1,201)] # list of tuples, all possible solvent content values from n=1 to n=200 molecules per asu

    #check if the MW is not too big or too lowfor this unit cell
    if (nsolventContentTab[0][1]< minAllowedVs):
        return {"unitCellVol": 0}

    elif (nsolventContentTab[0][1]> 100):
        return {"unitCellVol": -1}

    #filter out improbable solvent contents (i.e below 10 of above 90%)
    nsolventContentTab=[tuplenmol for tuplenmol in nsolventContentTab if (tuplenmol[1] >=minAllowedVs and tuplenmol[1]<=maxAllowedVs)]

    #get a list with only the solvent content (easier to manipulate)
    pointsToPlot=np.array([tuplevs[1] for tuplevs in nsolventContentTab])


    #Getting the values of the density kernel that corresponds to the points we want to plot
    pointsToPlotDens=kde_sklearn(VsData,pointsToPlot)

    #Find the search order from highest to least probable
    tripleTuple=[]

    for i, t in enumerate(nsolventContentTab):      #now we have a list of triplets (nmol,Vs,density) to work with
        tripleTuple.append((t[0],t[1],pointsToPlotDens[i]))


    #custom sort function to compare my tripletuples (sorting them by density value)
    def cmp_tripleTuples(ta, tb):
        if ta[2] > tb[2]:
            return -1
        elif ta[2] == tb[2]:
            return 0
        else:
            return 1

    tripleTuple.sort(cmp_tripleTuples)

    #print the search order 
    print "\n--->Unit cell content analysis: suggested search order"
    for i,t in enumerate(tripleTuple):
        print("%s) nmol= %s, Vs= %s"%(i+1, t[0], round(t[1])))
    print("\n")

    #plot kernelDensity----------------------------------------------
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(0,100)
    ax.set_ylim(0,maxDens+0.005)
    ax.set_xlabel('Unit cell solvent content (%)')

    #Draw a line at the peak
    plt.plot((solventPeak, solventPeak), (0, maxDens), linestyle='--',color='tab:orange')
    plt.title(str(nEntriesRetained)+" PDB entries with resolution in between"+str(resolution+delta)+" and "+str(resolution-delta)+" A\nsolvent content distribution")


    #Draw the density itself
    ax.plot(x_grid,kernelDensity,linewidth='2.5',color='tab:blue')

    #Add the points to plot
    ax.plot(pointsToPlot,pointsToPlotDens,'ro')


    #Arrange where the coordinates will be displayed
    textCoord=[]
    for i in range(len(pointsToPlot)):
        val= -13.5 if pointsToPlot[i]<= solventPeak else +2.5
        textCoord.append(val)


    #annotate the peak
    ax.annotate("Peak: Vs= "+str(int(round(solventPeak)))+"%",xy=(solventPeak,maxDens),xytext=(solventPeak,maxDens+0.001))

    #Annotate the graph with our points
    for i,nombre in enumerate(pointsToPlot):
        ax.annotate("n="+str(nsolventContentTab[i][0])+"\nVs="+str(int(round(nombre)))+"%", xy=(nombre, pointsToPlotDens[i]), xytext=(nombre+textCoord[i], pointsToPlotDens[i]))

    if outputFig:
        plt.savefig(os.path.join(outputDir,'solventcontent.png'))

    #Output dictionary to write the results in HTML
    #the tripleTuple tab contains triplets (nmol, Vs, density)
    outDic={"unitCellVol": unitCellVol, "asuVol":asVolume, "multiplicity":multiplicity, "result":tripleTuple, "MW":MW}

    return outDic

#Trying functions:    
if __name__ == '__main__':
    harkerSections(20)