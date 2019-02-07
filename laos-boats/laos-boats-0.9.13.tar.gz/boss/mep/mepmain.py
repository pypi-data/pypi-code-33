import numpy as np
import os

from .mep import MEP
from .space import Space
from ..io import DataOutput, IOutils, Parse
from ..pp import recreate_bo, Plot

class MEPmain:
    def __init__(self, STS, ipt_rstfile, minimafile, mainOutput):
        # create needed directories
        if os.path.isdir('mep'):
            print("warning: overwriting directory 'mep'")
        os.system('rm -rf mep')
        os.system('mkdir -p mep')

        # recreate model and read local minima
        self.get_model(STS, ipt_rstfile, mainOutput)
        self.get_minima(minimafile, mainOutput)
        self.get_space(STS)

        # initialize and run
        mep = MEP(self.bo, self.space, self.minima, STS.mep_precision,
                  STS.mep_rrtsteps, STS.mep_nebsteps, STS.mep_maxe)
        mep.run_mep(mainOutput)

        # write to file
        for path in mep.fullpaths:
            DataOutput.dump_mep(path)

        # plot
        if self.minima.shape[1] == 2: self.plot2D(STS, mep)

    def get_model(self, STS, ipt_rstfile, mainOutput):
        acqs, mod_par = Parse.rst(STS, ipt_rstfile)
        self.bo = recreate_bo(STS,
                              acqs[:, 1:],
                              mod_par[mod_par.shape[0]-1, 1:],
                              mainOutput,
        )

    def get_minima(self, minimafile, mainOutput):
        self.minima = Parse.minima(minimafile)
        self.minima = self.minima[:, :-1]

    def get_space(self, STS):
        bounds = np.transpose(STS.bounds)
        pbc = (np.array(STS.kerntype) == 'stdp')
        if not np.all(STS.periods == (bounds[1,:] - bounds[0,:])):
            print('warning: MEP currently assumes periods to match ' + 
                  'boundlength')
        self.space = Space(bounds, pbc)

    def plot2D(self, STS, mep):
        it = np.max(STS.pp_iters)
        npts = STS.initpts + it
        fname = ('postprocessing/data_models/' +
                    'it%.4i_npts%.4i.dat'%(it,npts))
        if not files_ok([fname]):
            print('Model data of the last iteration is required for '+
                  "automatic 2D plotting, check\nthe 'pp_models' " +
                  "and 'pp_iters' options, then try rerunning postprocessing.")
            return
        mdata = IOutils.readCols(fname, skiprows=2)
        xhat = None
        xnext = None
        minima = self.minima
        truef = None

        Plot.model(STS,
            'mep/minpaths.png',
            mdata,
            minima=self.minima,
            incl_uncert=False,
            paths=mep.fullpaths,
        )

def files_ok(filenames):
    """
    Checks that the given files exist and can be opened.
    """
    for fname in filenames:
        try:
            f = open(fname, 'r')
            f.close()
        except FileNotFoundError:
            print("Could not find file '" + fname + "'")
            return(False)
    return(True)

