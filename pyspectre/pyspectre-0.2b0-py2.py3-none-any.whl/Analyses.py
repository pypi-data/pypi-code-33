import os
import numpy as np
import shutil

analyses = ['tran', 'envlp']


def copydc2tran(pyspectre_obj):
    shutil.copyfile(
        os.path.join(pyspectre_obj.working_path, pyspectre_obj.analysis.dcfile),
        os.path.join(pyspectre_obj.working_path, pyspectre_obj.analysis.tranfile))


class Analysis:
    dcfile = 'dcsoln.ic'
    tranfile = 'transoln.icfc'

    def init(self, ):
        raise NotImplementedError

    def reset(self, pyspectre_obj):
        raise NotImplementedError

    def step(self, pyspectre_obj, start, stop):
        raise NotImplementedError

    def interpret_data(self, pyspectre_obj, signal_name):
        raise NotImplementedError


class Tran(Analysis):

    def init(self, pyspectre_obj):
        pyspectre_obj.setparams(pyspectre_obj.analysis_name, {
            "skipdc": "no",
            "readic": 'nil',
            "writefinal": 'nil',
            "write": self.dcfile,
        })
        pyspectre_obj.interface.runanalysis('dc')

    def reset(self, pyspectre_obj, sampleinterval=None):
        copydc2tran()
        pyspectre_obj.setparams( pyspectre_obj.analysis_name,{
            "skipdc": "yes",
            "readic": self.tranfile,
            "write": 'nil',
            "compression": "all",
        })
        if sampleinterval is not None:
            pyspectre_obj.interface.setparametervalue(pyspectre_obj.analysis_name, "strobeperiod", sampleinterval)

    def step(self, pyspectre_obj, start, stop, block=True):
        pyspectre_obj.setparams( pyspectre_obj.analysis_name,{
            "start": start,
            "stop": stop,
            "writefinal": self.tranfile,
            "readic": self.tranfile,
        })
        pyspectre_obj.interface.runanalysis(pyspectre_obj.analysis_name, block=block)

    def interpret_data(self, pyspectre_obj, signal_name):
        raise NotImplementedError
        filename = os.path.join(self.resultsdir, self.spicefilepath.split('/')[-1].split('.')[0] + '.raw')
        blocks = dr.nutmeg_blocks(filename)
        if self.analysis_name not in blocks:
            raise RuntimeError('couldn\'t find \'tran\' block.')
        dr.read(filename, block=blocks.index(self.analysis_name))
        t = np.array(dr.get("time"))
        availdata = dr.names()

        if signames is not None:
            if type(signames) is str:
                signames = [signames]
            # for name in signames:
            #     if name not in availdata:
            #         raise IOError('can\'t find \"{}\" in datafile \"{}\"'.format(name, filename))
        else:
            availdata.remove('time')
            signames = sorted(availdata)

        for name in signames:
            try:
                x.append(dr.get(name))
            except Exception:
                raise IndexError('no signal found with name {}'.format(name))

        x = np.stack(x, 1)


class Envlp(Analysis):

    def __init__(self):
        self.basetime = None

    def init(self, pyspectre_obj, stepsize, block=True):
        fundamental_period = pyspectre_obj.interface.getparametervalue(pyspectre_obj.analysis_name, 'fund')
        pyspectre_obj.setparams( pyspectre_obj.analysis_name, {
            "start": -stepsize,
            "stop": 0.0,
            "skipdc": "no",
            "readic": 'nil',
            "write": self.dcfile,
            "writefinal": self.tranfile,
            # "savetime": "[0.0]",       ## not implemented
            # "savefile": 'savefile.ic',  ## not implemented
        })
        pyspectre_obj.interface.runanalysis(pyspectre_obj.analysis_name, block=block)
        return self.dcfile

    def reset(self, pyspectre_obj, sampleinterval=None, block=True):
        self.basetime = 0.0
        pyspectre_obj.copydc2tran()
        pyspectre_obj.setparams(
            pyspectre_obj.analysis_name,
            {
                "skipdc": "yes",
                "readic": self.tranfile,
                #"readns": self.tranfile,  # filename to read nodeset for dc solution
                "writefinal": self.tranfile,
                "write": 'nil',
                'ic': 'node',  # dc, node, dev, all
                #'start': -circuit_obj.simtimestep,
                #'stop':circuit_obj.simtimestep,
                #'useprevic': 'ns',                                          ## not implemented
                # "savetime": '[{:e}]'.format(stop),                      ## not implemented
                # "savefile": 'savefile.fd',                                ## not implemented
                # "restart": "no",  # if yes, will recalculate time-0 conditions; if no, will reuse last time-0 condition
            },
            block=block)
        if sampleinterval:
            pyspectre_obj.setparams(
                pyspectre_obj.analysis_name,
                {"strobeperiod": sampleinterval},
                block=block
            )

    def step(self, pyspectre_obj, stepsize, resolution=None, block=True):
        pyspectre_obj.setparams( pyspectre_obj.analysis_name,{
            "skipdc": "yes",   # yes, no
            "readic": self.tranfile,    # filename to read initial state
            #"readns" : self.tranfile,   # filename to read nodeset for dc solution
            "writefinal": self.tranfile,    # filename to save final state
            "write": 'nil',     #  file to save initial state
            'ic': 'node', # dc, node, dev, all
            "start": 0.0,
            "stop": stepsize,
            # 'useprevic': 'ns',                                          ## not implemented
            # "savetime": '[{:e}]'.format(stop),                      ## not implemented
            # "savefile": 'savefile.fd',                                ## not implemented
            "strobeperiod": resolution,
            # "restart": "no",  # if yes, will recalculate time-0 conditions; if no, will reuse last time-0 condition
        })
        pyspectre_obj.runanalysis(block=block)
        self.basetime += stepsize

    def interpret_data(self, simulation_obj, signal_names):
        #wave = pyspectre_obj.readdata(signames=signal_name)

        resultsdir = os.path.join(simulation_obj.resultsdir, 'psf')
        files = list(filter(None, [item if item.endswith('fd.envlp') else None for item in os.listdir(resultsdir)]))
        nharms = len(files) - 1

        t = []
        v = []

        for harmno in range(nharms):
            filename = os.path.join(simulation_obj.analysis_name
                                        + '.'
                                        + str(harmno)
                                        + '.fd.'
                                        + simulation_obj.analysis_type
                                    )
            tt, tv = simulation_obj._read_file(filename, signal_names)
            t.append(tt)
            if np.any(np.iscomplex(tv)):
                v.append(np.vstack([np.real(tv).astype(np.float32),np.imag(tv).astype(np.float32)]))
            else:
                v.append(np.real(tv).astype(np.float32))

        if all([np.all(t[0] == item) for item in t]):
            t = t[0]

        return np.vstack(t)+self.basetime, np.vstack(v)
