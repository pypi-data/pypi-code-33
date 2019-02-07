import datetime
import numpy as np
import os
import pkg_resources

from . import IOutils as io

class MainOutput:
    """
    Functionality to write to the main output (*.out) file.
    """
    def __init__(self, STS):
        self.ipfile = STS.ipfile
        self.outfile = STS.outfile
        self.verbosity = STS.verb

        if os.path.isfile(self.outfile):
            print("warning: overwriting file '" + self.outfile + "'")

        self.header()
        self.ipfile_repeat(STS)
        self.settings(STS)
        self.utils = io

    def header(self):
        """
        Writes a header to main output file overwriting a possibly existing
        old output file at the same filepath.
        """
        version = pkg_resources.require("laos-boats")[0].version
        s = "\n-----------------------------   Welcome to ....   ----------" \
            + "--------------------\n" \
            + "                      _______  _______ _______ _______ \n" \
            + "                     |   _   \|   _   |   _   |   _   |\n" \
            + "                     |.  1   /|.  |   |   1___|   1___|\n" \
            + "                     |.  _   \|.  |   |____   |____   |\n" \
            + "                     |:  1    |:  1   |:  1   |:  1   |\n" \
            + "                     |::.. .  |::.. . |::.. . |::.. . |\n" \
            + "                     `-------'`-------`-------`-------'\n\n" \
            + "{:^80s}\n".format("Version " + str(version)) \
            + "{:^80s}\n".format(datetime.datetime.now().strftime(
                                            "%d-%m-%Y %H:%M:%S")) \
            + "------------------------------------------------------------" \
            + "--------------------\n\n"
#        io.append_write(self.outfile, s)
        io.overwrite(self.outfile, s)


    def footer(self, totaltime):
        """
        Writes a footer to main output file
        """
        text = "BOSS is done! Have a nice day :)"
        s = "\n\n--------------------------------------------------------" \
            + "------------------------\n"
        s += "{:^80s}\n\n".format(text)
        s += "{:^40s}".format(datetime.datetime.now().strftime(
                                        "Datetime %d-%m-%Y %H:%M:%S"))
        s += "{:^40s}".format("Total time [s] %s"%(
                            totaltime)) # code total time
        s += "\n---------------------------------------------------------" \
            + "-----------------------\n"
        io.append_write(self.outfile, s)

    def ipfile_repeat(self, is_rst):
        """
        Repeats the input file near the beggining of the main output file.
        """
        if self.verbosity > 0:
            self.progress_msg('Reading BOSS input file from: '
                                + self.ipfile, 0)
            self.progress_msg('Initializing...\n', 0)
            #if is_rst:
            #    self.progress_msg('Input file recognized as' \
            #                      + ' a restart file.', 0)
            self.section_header('INPUT FILE')
            s = ""
            f = open(self.ipfile)
            line = f.readline()
            while len(line) > 0:
                s += line
                line  = f.readline()
            f.close()
            io.append_write(self.outfile, s)

    def settings(self, STS):
        """
        Outputs the interpreted code variable settings to main output file.
        """
        if self.verbosity > 0:
            self.section_header('SIMULATION OPTIONS')
            s =  "|| File input/output \n"
            s += "ipfile         %s\n"%(STS.ipfile)
            s += "userfn         %s\n"%(STS.userfn)
            s += "outfile        %s\n"%(STS.outfile)
            s += "rstfile        %s\n\n"%(STS.rstfile)

            s += "|| Key settings \n"
            s += "bounds        "  + io.twoDfloatarray_line(STS.bounds,STS.dim,2)\
                                 + "\n"
            s += "kerntype      " + io.oneDarray_line(STS.kerntype, STS.dim, str)\
                                + "\n"
            if np.any(STS.kerntype == 'stdp'):
                s += "periods      " + io.oneDarray_line(STS.periods,
                                            STS.dim, float) + "\n"
            s += "yrange        " + io.oneDarray_line(STS.yrange, 2, float) \
                                 + "\n"
            s += "noise          %8.3E\n"%(STS.noise)
            if not STS.is_rst: s += "inittype       %s\n"%(STS.inittype)
            s += "initpts   %i    iterpts   %i\n"\
                            %(STS.initpts, STS.iterpts)
            if STS.dxhat_tol is not None:
                s += "gm_tol         %8.3E   %i\n"%(STS.dxhat_tol[0],STS.dxhat_tol[1])
            else: s += "gm_tol         none\n"
            s += "verbosity      %i\n\n"%(STS.verb)

            s += "|| Data acquisition \n"
            s += "acqfn                %s\n"%(STS.acqfn_name)
            s += "acqtol               "
            if STS.acqtol is None: s += "none\n"
            else:                    s += "%8.3E\n"%(STS.acqtol)
            s += '\n'

            s += "|| GP hyperparameters \n"
            s += "thetainit      " + io.oneDarray_line(STS.thetainit,
                                      STS.dim, float) + "\n"
            s += "thetabounds    " + io.twoDfloatarray_line(STS.thetabounds,
                                       STS.dim+1, 2) + "\n"
            s += "thetaprior      %s\n"%(STS.thetaprior)
            s += "thetapriorpar  " + io.twoDfloatarray_line(STS.thetapriorpar,
                                       STS.dim+1, 2) + "\n\n"

            s += "|| Hyperparameter optimization\n"
            s += "updatefreq   %i  initupdate      %s\n"\
                            %(STS.updatefreq, str(STS.initupdate))
            s += "updateoffset %i  updaterestarts  %i\n\n"\
                            %(STS.updateoffset, STS.updaterestarts)

            if STS.doing_pp:
                s += "| postprocessing\n"
                #s += "pp_iters          ="
                #s += io.oneDarray_line(STS.pp_iters,len(STS.pp_iters),int)+"\n"
                s += "pp_models         = %s\n"%(STS.pp_models)
                s += "pp_acq_funcs      = %s\n"%(STS.pp_acqfs)
                s += "pp_truef_npts     = "
                if STS.pp_truef_npts is None: s += "none\n"
                else: s += "%i\n"%(STS.pp_truef_npts)
                s += "pp_m_slice        ="
                s += io.oneDarray_line(STS.pp_m_slice,len(STS.pp_m_slice),int)\
                            +"\n"
                if STS.pp_x_defaults is not None:
                    s += "pp_var_defaults   ="
                    s += io.oneDarray_line(STS.pp_x_defaults,
                                len(STS.pp_x_defaults), float) +"\n"
                s += "pp_truef_at_xhats = %s\n"%(STS.pp_true_hats)
                s += "pp_local_minima   = "
                if STS.pp_local_mins is None: s += "none\n\n"
                else: s += "%i\n\n"%(STS.pp_local_mins)

            io.append_write(self.outfile, s)

    def progress_msg(self, msg, priority, preceding_bl=False, nospace=False):
        """
        Announce progress message to main output file depending on verbosity.
        """
        m = ""
        if self.verbosity >= priority:
            if preceding_bl: m = m + '\n'
            m = m + '|'
            if not nospace: m = m + ' '
            m = m + msg + '\n'
        io.append_write(self.outfile, m)

    def convergence_stop(self):
        """
        Announces BO stop due to global minimum convergence
        """
        msg = "Stopped BO due to global minimum prediction convergence"
        self.progress_msg(msg, 0, True)

    def iteration_start(self, itNo, initpts):
        """
        Output section header for the new iteration.
        """
        if itNo <= initpts: text = "INITIAL DATAPOINT " + str(itNo)
        else: text = "BO ITERATION " + str(itNo - initpts)
        s = "\n--------------------------------------------------------" \
            + "------------------------\n"
        s += "{:^80}".format(text)
        s += "\n---------------------------------------------------------" \
            + "-----------------------\n"
        io.append_write(self.outfile, s)

    def iteration_summary(self, datasize, newXs, newYs, convergence, xnext, est_yrange,
                          model_params, timer):
        """
        Outputs info about one BO iteration to main output file
        """
        iterno = convergence.shape[0]-1
        xbest, ybest, xhat, muhat, nuhat = convergence[iterno,:]
        d_xhat, d_muhat = np.nan, np.nan
        if iterno > 1:
            prev_xhat, prev_muhat = convergence[iterno-1, [2,3]]
            d_xhat = np.linalg.norm(xhat - prev_xhat)
            d_muhat = np.linalg.norm(muhat - prev_muhat)/est_yrange

        #self.progress_msg("-Iteration summary-", 0, True)
        s = "| Data point added to dataset (x y): \n"
        newXs = np.atleast_2d(newXs)
        newYs = np.atleast_1d(newYs)

        for i in range(len(newYs)):
            s += io.data_line(newXs[i], [newYs[i]], fstr="%18.10E")
        s += "\n| Total ensemble size: %i\n" % datasize

        # Model
        if not np.any(model_params == None): # Only BO iterations
            if self.verbosity > 0:
                s += "| Best acquisition, x_best y_best:\n"
                s += io.data_line(xbest.flatten(), ybest.flatten(),
                                  fstr="%18.10E")
            s += "| Global minimum prediction, x_hat mu_hat +- nu_hat:\n"
            s += io.data_line(xhat.flatten(), [muhat, nuhat],
                              fstr="%18.10E")
            # Convergence
            if self.verbosity > 1 and not np.any(np.isnan([d_xhat, d_muhat])):
                s += "| Global minimum convergence, d_xhat d_muhat:\n"
                s += io.data_line([d_xhat, d_muhat], fstr="%18.10E")

            if self.verbosity > 1:
                s += "\n| GP model hyperparameters (lengthscales variance):\n"
                s += io.data_line(model_params[1:], [model_params[0]],
                                    fstr="%18.10E")
        if self.verbosity > 1:
            s += "| Next sampling location x_next:\n"
            s += io.data_line(xnext.flatten(), fstr="%18.10E")
        s += "\nIteration time [s]: %8.3f"%(timer.getLapTime())
        s +=   "        Total time [s]: %8.3f"%(timer.getTotalTime())
        io.append_write(self.outfile, s + '\n')


    def section_header(self, text):
        """
        Writes a section header to main output file.
        """
        s = "--------------------------------------------------------" \
            + "------------------------\n"
        s += "{:^80s}\n".format(text)
        s += "---------------------------------------------------------" \
            + "-----------------------\n"
        io.append_write(self.outfile, s)

    def mep_start(self, mep):
        """
        Writes MEP options and local minima
        """
        s = ''
        s += '|| MEP options\n'
        s += "precision %8d    maxE      %8.3E\n"\
                               %(mep.precision, mep.maxE)
        s += "rrtsteps  %8d    nebsteps   %8d\n"\
                               %(mep.rrtsteps, mep.nebsteps)
        s += '\n'
        s += 'Energy threshold starting at %8.3E, stepsize %8.3E.\n'\
                               %(mep.e_start, mep.stepsize)
        s += '\n'

        s += '|| Minima\n'
        s += '(pt index, coordinates)\n'
        for i in range(mep.min_points.shape[0]):
            s += str(i)
            for j in range(mep.min_points.shape[1]):
                s += ' ' + str(mep.min_points[i, j])
            s += '\n'
        s += '\n'
        io.append_write(self.outfile, s)

    def mep_result(self, mep):
        """
        Writes the results of MEP
        """
        s = '\n'
        s += '|| MEP results\n'
        s += '(pt index, pt index, highest energy on the minimum energy path)\n'
        l = mep.min_points.shape[0]
        e = np.zeros((l,l))
        for path in mep.fullpaths: e[path.mi, path.mj] = path.maxe

        for i in range(l):
            for j in range(l):
                if i < j:
                    s += '%d %d %8.3E\n' % (i, j, e[i,j])
                    
        s += '\n'

        io.append_write(self.outfile, s)


