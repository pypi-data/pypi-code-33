import math
import numpy as np
import os
import sys
import importlib

from ..utils import Distributions
from .main_output import MainOutput
from ..bo.acq import elcb, lcb, explore, exploit, ei

class Settings:
    """
    Reads, interprets and defines the code internal settings based on input.
    """

    def __init__(self, ipfile, timer):
        """
        Sets all settings by reading first the input file, filling in defaults
        and calculating implicit settings.
        """
        self.ipfile = ipfile
        self.timer = timer
        self._read_ipfile()
        # self.set_keywds, self.is_rst and self.input_lines are now defined

        ### SET SETTINGS DIRECTLY (overridden w/ defaults if not given by user)

        # files
        self.userfn = self._setopt('userfn', None, str)
        self.outfile = self._setopt('outfile', 'boss.out', str)
        self.rstfile = self._setopt('rstfile', 'boss.rst', str)

        # general
        self.bounds = self._setopt('bounds', None, '2Dfloatarray')
        self.dim = len(self.bounds)
        self.kerntype = self._setopt(
                            'kernel', ['stdp']*self.dim, 'strlist')
        self.periods = self._setopt('periods', 
                            self.bounds[:,1] - self.bounds[:,0], 'floatlist')
        self.yrange = self._setopt('yrange', [-10.,10.], 'floatlist')
        self.ygrads = self._setopt('ygrads', False, bool) 

        self.inittype = self._setopt('inittype', 'sobol', str)
        self.initpts = self._setopt('initpts', 5, int)
        self.iterpts = self._setopt('iterpts', int(15*self.dim**1.5), int)
        self.verb = self._setopt('verbosity', 1, int)
        self.dxhat_tol = self._setopt('gm_tol', None, 'floatlist')

        # data acquiring
        self.acqfn_name = self._setopt('acqfn', 'elcb', str).lower()
        self.acqfnpars = self._setopt('acqfnpars', [], 'floatlist')
        self.acqtol = self._setopt('acqtol', 0.001, float)

        # hyperparameters
        self.noise = self._setopt('noise', 1e-12, float)
        self.thetainit = self._setopt('thetainit', None, 'floatlist')
        self.thetabounds = self._setopt('thetabounds', None, '2Dfloatarray')
        self.thetaprior = self._setopt('thetaprior', 'gamma', str)
        self.thetapriorpar = self._setopt(
                                    'thetapriorparam', None, '2Dfloatarray'
                                         )

        # hyperparameter optimization
        self.updatefreq = self._setopt('updatefreq', 1, int)
        self.initupdate = self._setopt('initupdate', True, bool)
        self.updateoffset = self._setopt('updateoffset', 0, int)
        self.updaterestarts = self._setopt('updaterestarts', 2, int)
        self.hmciters = self._setopt('hmc', 0, int)
        self.cores = self._setopt('cores', 1, int)

        # post-processing
        self.pp_iters = self._setopt('pp_iters', list(range(self.iterpts+1)),
                        'intlist')
        self.pp_models = self._setopt('pp_models', False, bool)
        self.pp_acqfs = self._setopt('pp_acq_funcs', False, bool)
        self.pp_truef_npts = self._setopt('pp_truef_npts', None, int)
        self.pp_m_slice = self._setopt('pp_model_slice', None, 'intlist')
        self.pp_x_defaults = self._setopt('pp_var_defaults', None, 'floatlist')
        self.pp_true_hats = self._setopt('pp_truef_at_xhats', False, bool)
        self.pp_local_mins = self._setopt('pp_local_minima', None, float)

        # minimum energy paths
        self.mep_precision = self._setopt('mep_precision', 25, int)
        self.mep_rrtsteps = self._setopt('mep_rrtsteps', 10000, int)
        self.mep_nebsteps = self._setopt('mep_nebsteps', 20, int)
        self.mep_maxe = self._setopt('mep_maxe', None, int)

        # hard coded - related to minimizing the model in search of xhat
        self.minzacc = 15
        self.min_dist_acqs = 0.01*min(self.periods)

        if len(self.set_keywds) > 0:
            print('ERROR:', self.set_keywds)
            raise ValueError(
                "Unknown settings given in input file '" + self.ipfile + "'"
                    )
        if self.bounds is None:
            raise ValueError(
                "ERROR: keyword 'bounds' has to be defined in input file"
                    )

        ### IMPLICIT OPTIONS

        # Current working directory
        self.dir = os.getcwd()

        # The user-defined objective function
        if self.userfn is not None:
            path, filename = os.path.split(self.userfn)
            sys.path.append(path)
            user_script = importlib.import_module(filename[0:-3])
            self.f = user_script.f
        else:
            self.f = None

        # modify dxhat_tol formats
        if self.dxhat_tol is not None:
            self.dxhat_tol = [float(self.dxhat_tol[0]),
                              int(self.dxhat_tol[1])]

        # select acquisition functions
        if self.acqfn_name == 'elcb':
            self.acqfn = elcb
        elif self.acqfn_name == 'lcb':
            self.acqfn = lcb
            if len(self.acqfnpars) < 1: self.acqfnpars = [2.] # explr_weight
        elif self.acqfn_name == 'explore':
            self.acqfn = explore
        elif self.acqfn_name == 'exploit':
            self.acqfn = exploit
        elif self.acqfn_name == 'ei':
            self.acqfn = ei
        else:
            raise TypeError("ERROR: Unknown acquisition function selected: '"
                            + self.acqfn_name + "'")

        # kernel type
        if len(self.kerntype) == 1 and self.dim > 1:
            self.kerntype = self.kerntype * self.dim

        # default initial hyperparameters
        if self.thetainit is None:
            self.thetainit = [0.5 * (self.yrange[1] - self.yrange[0])] # sig
            for i in range(self.dim): # lengthscales
                if self.kerntype[i] == 'stdp': # pbc
                    self.thetainit.append(np.pi/10)
                else: # nonpbc
                    self.thetainit.append(self.periods[i]/20)

        #-- default hyperparameter constraints
        if self.thetabounds is None and self.thetaprior is None:
            self.thetabounds = [[self.thetainit[0]/1000.,
                                 self.thetainit[0]*1000.]] # variance
            for i in range(self.dim):                      # lengthscale
                self.thetabounds.append([self.thetainit[i+1]/100.,
                                         self.thetainit[i+1]*100.])
            self.thetabounds = np.array(self.thetabounds)
        

        #-- default hyperparameter priors
        if self.thetapriorpar is None and self.thetaprior is not None:
            diff = self.yrange[1] - self.yrange[0]
            if self.thetaprior == "gamma":
                shape, rate = Distributions.gammaparams(
                    (diff/4)**2, (10*diff/4)**2, 0.5, 0.99)
#                    shape = 1.0    # NORMALIZATION
#                    rate = 1.5     # NORMALIZATION
                self.thetapriorpar = [[shape, rate]]
            else:
                raise TypeError("Unknown options set for thetaprior: '"
                                + self.thetaprior + "'.")

            for i in range(self.dim):
                if self.thetaprior == "gamma":
                    if self.kerntype[i] == 'stdp': # pbc
                        shape = 3.3678
                        rate = 9.0204
                    else: # nonpbc
                        shape, rate = Distributions.gammaparams(
                            self.periods[i]/20, self.periods[i]/2
                                                 )
                    self.thetapriorpar.append([shape, rate])
                else:
                    raise TypeError("Unknown options set for \
                                    K_priortype: '" + self.thetaprior + "'.")

        # model slice and number of points
        if self.pp_m_slice is None:
            self.pp_m_slice = list(range(self.dim))[:2]
            if len(self.pp_m_slice) == 1:
                self.pp_m_slice.append(self.pp_m_slice[0])
                self.pp_m_slice.append(50)
            else:
                self.pp_m_slice.append(25)
        else:
            self.pp_m_slice[0] -= 1 # user expected not to use python indexing
            self.pp_m_slice[1] -= 1

        # some sanity checks
        if self.pp_acqfs and self.verb < 2:
            self.verb = 2 # to have xnexts printed
        

        ### END OF IMPLICIT OPTIONS

    def _read_ipfile(self):
        """
        Reads the input file and saves the found keywords to self.keywds dict.
        Additionally kicks off handling of an rst file
        """
        self.set_keywds = {}
        self.is_rst = False
        self.rstvals = np.array([])
        with open(self.ipfile) as ipf:
            for line in ipf:
                line = line.split('#', maxsplit=1)[0]
                line = line.replace('\n', '').split(maxsplit=1)
                if len(line) > 0 and not self.is_rst:
                    if line[0].startswith('RESULTS'):
                        self.is_rst = True
                        self._read_iterations(ipf)
                    else:
                        self.set_keywds[line[0]] = line[1]

    def _read_iterations(self, ipf):
        """
        Reads the ensebles (x, y, theta) given in an rst-file.
        """
        rst = np.array([]).reshape((0,0))
        line = ipf.readline()
        while len(line) > 1: # is not just \n
            l = line.replace('\n', '')
            l = line.split(' ')
            a = np.array([])
            for s in l:
                if s != '' and s != '\n':
                    a = np.hstack((a, float(s)))
            if a.shape[0] > rst.shape[1]:
                z = np.zeros((rst.shape[0], a.shape[0]-rst.shape[1]))
                z = np.nan * z
                rst = np.hstack((rst, z))
            elif a.shape[0] < rst.shape[1]:
                z = np.nan * np.zeros(rst.shape[1] - a.shape[0])
                a = np.hstack((a, z))
            rst = np.vstack((rst, a))

            line = ipf.readline()

        self.rstvals = rst

    def _setopt(self, keyword, default, type_):
        """
        Returns the value of the setting/option variable by first looking for
        it in self.keywds dictionary and otherwise using default.
        """
        if keyword in self.set_keywds.keys():
            val = self._convertstr(self.set_keywds[keyword], type_)
            del self.set_keywds[keyword]
            return val
        else:
            return default

    def _convertstr(self, value, type_):
        """
        Converts the parameter value into the requested type type_
        and returns it. Supported types are python's str, bool, int, float
        as well as custom types 'intlist', 'floatlist', 'strlist', 'boollist'
        and '2Dfloatarray', where the last is a numpy 2D array.
        """
        if value.lower() == 'none':
            return None
        elif type_ == str:
            return(value)
        elif type_ == bool:
            v = value.lower()
            return(bool(v != 'false' and v != 'f' and v != '0' and v != 'no'))
        elif type_ == int:
            return(int(value))
        elif type_ == float:
            return(float(value))
        elif type_ == np.ndarray:
            return(np.fromstring(value, dtype='float', sep=' '))
        elif type_ == 'intlist':
            value = value.split()
            a = []
            for v in value: a.append(int(v))
            return(a)
        elif type_ == 'floatlist':
            value = value.split()
            a = []
            for v in value: a.append(float(v))
            return(a)
        elif type_ == 'strlist':
            value = value.split()
            a = []
            for v in value: a.append(str(v))
            return(a)
        elif type_ == 'boollist':
            value = value.split()
            a = []
            for v in value: a.append(self._convertstr(v,bool))
            return(a)
        elif type_ == '2Dfloatarray':
            a = []
            value = value.split(';')
            for v in value: a.append(v.split())
            for i in range(len(a)):
                for j in range(len(a[i])):
                    a[i][j] = float(a[i][j])
            return(np.atleast_2d(a))
        else:
            raise NotImplementedError('Type conversion to ' + str(type_) +
                                      ' not implemented yet.')



