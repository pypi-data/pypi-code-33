from pySAXS.models.model import Model
from pySAXS.LS.LSsca import *
import numpy

class Core_shell_Cylinder(Model):
    '''
    Core-shell cylinder in solvent
    by OS : 10/11/2011
    '''
    
    def PCylinder_2L(self,q,par):
        """
        q array of q (A-1)
        par[0] inner radius (in 1/q)
        par[1] outer radius (in 1/q)
        par[2] length (in 1/q)
        par[3] SLD inner cylinder (cm-2)
        par[4] SLD outer shell (cm-2)
        par[5] SLD medium (cm-2)
        par[6] number density (cm-3)
        """
        R=[par[0],par[1]]
        L=par[2]
        rho = [par[3],par[4],par[5]]
        n=par[6]        

        f = Pcylmulti(q,R,rho,L,n)
        return f

    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PCylinder_2L #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,200.)                                     #q range(x scale)
        self.Arg=[30.,35.,200.,9.8e10,9.8e11,9.8e10,1e10]                   #list of parameters
        self.Format=["%f","%f","%f","%1.3e","%1.3e","%1.3e","%1.3e"]       #list of c format
        self.istofit=[True,True,True,False,False,False,False]              #list of boolean for fitting
        self.name="Core-shell cylinder"                                    #name of the model
        self.Doc=["Inner radius ",\
             "Outer radius ",\
             "Length ",\
             "scattering length density of the core cylinder (cm-2)",\
             "scattering length density of the shell cylinder (cm-2)",\
             "scattering length density of medium (cm-2)",\
             "Number density (cm-3)"]           #list of description for parameters
        self.Description="Core-shell cylinder"  # description of model
        self.Author="Olivier Spalla"                 #name of Author
    
