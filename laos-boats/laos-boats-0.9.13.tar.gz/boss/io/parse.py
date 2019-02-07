import numpy as np

class Parse:
    """
    Functions to parse files produced by a BOSS optimization.
    """

    def min_preds(STS, filepath):
        """
        Extracts xhat, muhat and nuhat from all bo iterations in the output
        file. Returns a numpy array where each element is [npts, xhat, muhat,
        nuhat]. Works on output files with all verbosity levels.
        """
        try:
            data = []
            with open(filepath) as f:
                line = f.readline()
                npts = None
                while len(line) > 0:
                    if line.find("Total ensemble size") != -1:
                        npts = int(line.split()[-1])
                    elif line.find("Global minimum prediction") != -1:
                        line = f.readline()
                        line = line.split()
                        data.append(np.concatenate([[npts], line[:STS.dim+2]]))
                    line = f.readline()
            return np.array(data).astype(float)
        except:
            raise OSError("Error trying to read file '" + filepath + "'")

    def acqs(STS, filepath):
        """
        Extracts data acquisitions from all bo iterations in the output file.
        Returns a numpy array where each element is [npts, x, y].
        Note that there may be several acquisitions on the same iteration -
        especially the initial points at the 0th iteration.
        Works on output files with all verbosity levels.
        """
        try:
            f = open(filepath)
            acq = []
            line = f.readline()
            npts = 0
            while len(line) > 0:
                if line.find("Data point added to dataset") != -1:
                    line = f.readline()
                    while len(line.split()) == STS.dim+1 \
                    and line.find('.') != -1:
                        line = line.split()
                        npts += 1
                        acq.append(np.concatenate([[npts], line[:STS.dim+1]]))
                        line = f.readline()
                else:
                    line = f.readline()
            f.close()
            return np.array(acq).astype(float)
        except:
            raise OSError("Error trying to read file '" + filepath + "'")

    def best_acqs(STS, filepath):
        """
        Extracts xbest and ybest from all bo iterations in the output file.
        Returns a numpy array where each element is [npts, xbest, ybest].
        Works only on output files with verbosity levels of at least 1.
        """
        try:
            data = []
            with open(filepath) as f:
                line = f.readline()
                npts = None
                while len(line) > 0:
                    if line.find("Total ensemble size") != -1:
                        npts = int(line.split()[-1])
                    elif line.find("Best acquisition") != -1:
                        line = f.readline()
                        line = line.split()
                        data.append(np.concatenate([[npts], line[:STS.dim+1]]))
                    line = f.readline()
                return np.array(data).astype(float)
        except:
            raise OSError("Error trying to read file '" + filepath + "'")

    def conv_measures(STS, filepath):
        """
        Extracts dx_hat and dmu_hat from all bo iterations in the output
        file. Returns a numpy array where each element is
        [npts, dxhat, dmuhat].
        Works only on output files with verbosity levels of at least 1.
        """
        try:
            data = []
            with open(filepath) as f:
                line = f.readline()
                npts = None
                while len(line) > 0:
                    if line.find("Total ensemble size") != -1:
                        npts = int(line.split()[-1])
                    elif line.find("Global minimum convergence") != -1:
                        line = f.readline()
                        line = line.split()
                        if 'none' in line:
                            pass
                        else:
                            data.append(np.concatenate([[npts], line]))
                    line = f.readline()
                return np.array(data).astype(float)
        except:
            raise OSError("Error trying to read file '" + filepath + "'")

    def mod_params(STS, filepath):
        """
        Extracts unfixed GP model hyperparameters from all bo iterations in the
        output file. Returns a numpy array where each element is
        [npts, variances, lengthscales].
        Works only on output files with verbosity levels of at least 2.
        """
        try:
            f = open(filepath)
            hpar = []
            line = f.readline()
            npts = None
            while len(line) > 0:
                if line.find("Total ensemble size") != -1:
                    npts = int(line.split()[-1])
                elif line.find("GP model hyperparameters") != -1:
                    line = f.readline()
                    line = line.split()
                    line = list(np.insert(line, 0, line[-1]))
                    del line[-1]
                    hpar.append(np.concatenate([[npts], line]))
                line = f.readline()
            f.close()
            return np.array(hpar).astype(float)
        except:
            raise OSError("Error trying to read file '" + filepath + "'")

    def xnexts(STS, filepath):
        """
        Extracts xnext locations from all bo iterations in the output file.
        Returns a numpy array where each element is [npts, xnext].
        Note that this means that the location 'xnext' is to be evaluated
        in the next iteration 'iter+1'.
        Works only on output files with verbosity levels of at least 2.
        """
        try:
            data = []
            with open(filepath) as f:
                data = []
                line = f.readline()
                npts = None
                while len(line) > 0:
                    if line.find("Total ensemble size") != -1:
                        npts = int(line.split()[-1])
                    elif line.find("Next sampling location") != -1:
                        line = f.readline()
                        line = line.split()
                        data.append(np.concatenate([[npts], line]))
                    line = f.readline()
                return np.array(data).astype(float)
        except:
            raise OSError("Error trying to read file '" + filepath + "'")


    def rst(STS, filepath):
        """
        Extracts all information below the keyword 'RESULTS:' from an rst file.
        """
        try:
            f = open(filepath)
            acqs = []; mod_par = []
            line = f.readline()
            res_begun = False
            npts = 1
            while len(line) > 0:
                if res_begun:
                    line = line.split()
                    acqs.append(np.concatenate([[npts], line[:STS.dim+1]]))
                    if len(line) > STS.dim + 1:
                        mod_par.append(np.concatenate([[npts],
                                                    line[STS.dim+1:]]))
                    npts += 1
                elif line.find("RESULTS:") != -1:
                    res_begun = True
                else:
                    pass
                line = f.readline()
            f.close()
            return np.array(acqs).astype(float), \
                   np.array(mod_par).astype(float)
        except:
            raise OSError("Error trying to read file '" + filepath + "'")

    def minima(filepath):
        """
        Extract local minima
        """
        try:
            f = open(filepath)
            line = f.readline()
            if line[:14] == '# Local minima': ok = True
            else: ok = False
            f.close()
        except:
            raise OSError("Error trying to read file '" + filepath + "'")
 
        if not ok:
            raise Exception("'" + filepath + "' not recognized as " 
                            + "a minima file.")

        try:
            f = open(filepath)
            line = f.readline()
            line = f.readline()
            minima = np.array(line.split())
            line = f.readline()
            while len(line) > 0:
                minima = np.vstack((minima, line.split()))
                line = f.readline()
            f.close()
            return minima.astype(float)
 
        except:
            raise OSError("Error trying to read file '" + filepath + "'")

