#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Python code to interface with different aerodynamic executables

Includes adapted code snippets from:
https://github.com/The-Fonz/xfoil-optimization-toolbox
http://eyalarubas.com/python-subproc-nonblock.html
"""


from threading import Thread
from queue import Queue, Empty
from distutils.dir_util import copy_tree

import subprocess as subp
import numpy as np
import tempfile
import os
import re
import shutil


class Executable:
    """
    This base class basically represents an executable child process.
    """

    def __init__(self, executable, cwd=None):
        self.inst = subp.Popen(os.path.join(os.path.dirname(os.path.realpath(__file__)), executable), stdin=subp.PIPE,
                               stdout=subp.PIPE, stderr=subp.PIPE, cwd=cwd)
        self._stdoutnonblock = NonBlockingStreamReader(self.inst.stdout)
        self._stdin = self.inst.stdin
        self._stderr = self.inst.stderr
        self.tempfiles = []
        self.tempdirs = []
        self.config = []

    def cmd(self, cmd, autonewline=True):
        n = '\n' if autonewline else ''
        command = cmd + n
        self.inst.stdin.write(command.encode())

    def readline(self):
        self.inst.stdin.close()
        return self._stdoutnonblock.readline()

    def delete_temp(self):
        if len(self.tempfiles) > 0:
            for tempf in self.tempfiles:
                os.remove(tempf.name)
            self.tempfiles = []
        if len(self.tempdirs) > 0:
            for tempd in self.tempdirs:
                shutil.rmtree(tempd)
            self.tempdirs = []

    def cmdlogcheck(self):
        if not (hasattr(self, 'cmdlog')):
            self.close()
            raise Exception('The executable first needs to be executed!')

    def close(self):
        self.inst.kill()
        self.delete_temp()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def __del__(self):
        self.close()


class NonBlockingStreamReader:
    """
    Reader to communicate properly with the Executable
    """

    def __init__(self, stream):
        self._s = stream
        self._q = Queue()

        def _populate_queue(stream, queue):
            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    return

        self._t = Thread(target=_populate_queue,
                         args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()

    def readline(self, timeout=None):
        try:
            return self._q.get(block=timeout is not None,
                               timeout=timeout).decode()
        except Empty:
            return None


class XFOIL(Executable):
    """
    XFOIL interface with some convenience functions
    """

    def __init__(self):
        Executable.__init__(self, 'xfoil.exe')

    def airfoil(self, x, y, NORM, GDES):
        # Temporary file
        input_airfoil = tempfile.NamedTemporaryFile(delete=False)
        input_airfoil.close()
        self.tempfiles.append(input_airfoil)
        # Sanity check
        if (len(x) > 300) and (not GDES):
            self.close()
            raise ValueError('The number of input coordinates is too high. Keep it below 300 else XFOIL is likely to crash. Alternatively you can also activate GDES.')
        # Data
        data = np.array([x[:-1], y[:-1]])
        data = data.T
        np.savetxt(input_airfoil.name, data, fmt=['%f', '%f'])
        # Config        
        if NORM:
            self.config.append('NORM')
        self.config.append('LOAD {} \n'.format(input_airfoil.name))
        if GDES:
            self.config.append('GDES \n CADD \n\n\n\n\n PANEL')

    def execute(self, alphas):
        # Temporary files        
        self.alphas = alphas
        self.output_airfoil = tempfile.NamedTemporaryFile(delete=False)
        self.output_airfoil.close()
        self.tempfiles.append(self.output_airfoil)
        self.pressure_distributions = []
        for alpha in alphas:
            self.pressure_distributions.append(tempfile.NamedTemporaryFile(delete=False))
            self.pressure_distributions[-1].close()
            self.tempfiles.append(self.pressure_distributions[-1])
            # Config
        self.config.append('OPER \n PACC \n\n\n')
        self.config.append('SAVE {}'.format(self.output_airfoil.name))
        self.config.append('Y')
        self.config.append('OPER')
        for i, alpha in enumerate(alphas):
            self.config.append('ALFA %.4f' % (alpha * 180. / np.pi))
            self.config.append('CPWR %s' % self.pressure_distributions[i].name)
        self.config.append('PLIS')
        # Execute
        for cmd in self.config:
            self.cmd(cmd)
        self.cmd('ENDD')
        self.cmdlog = ['']
        while not re.search('ENDD', self.cmdlog[-1]):
            line = self.readline()
            if line:
                self.cmdlog.append(line)
        return self.cmdlog

    def output_polar(self):
        self.cmdlogcheck()
        lines = self.cmdlog

        def clean_split(s):
            return re.split('\s+', s.replace(os.linesep, ''))[1:]

        for i, line in enumerate(lines):
            if re.match('\s*---', line):
                dividerIndex = i
        data_header = clean_split(lines[dividerIndex - 1])
        info = ''.join(lines[dividerIndex - 4:dividerIndex - 2])
        info = re.sub('[\r\n\s]', '', info)

        def p(s):
            return float(re.search(s, info).group(1))

        infodict = {
            'xtrf_top': p('xtrf=(\d+\.\d+)'),
            'xtrf_bottom': p('\(top\)(\d+\.\d+)\(bottom\)'),
            'Mach': p('Mach=(\d+\.\d+)'),
            'Ncrit': p('Ncrit=(\d+\.\d+)'),
            'Re': p('Re=(\d+\.\d+e\d+)')
        }
        datalines = lines[dividerIndex + 1:-2]
        data_array = np.array(
            [clean_split(dataline) for dataline in datalines], dtype='float')
        return data_array, data_header, infodict

    def output_coordinates(self):
        self.cmdlogcheck()
        coords = np.loadtxt(self.output_airfoil.name, skiprows=1)
        x = coords[:, 0]
        y = coords[:, 1]
        return x, y

    def output_pressures(self):
        self.cmdlogcheck()
        control_x, control_y = self.output_coordinates()
        c_p = np.empty([len(self.alphas), len(control_x)])
        for i, pressure_distribution in enumerate(self.pressure_distributions):
            data = np.loadtxt(pressure_distribution.name, skiprows=1)
            c_p[i] = data[:, 1]
        return c_p


class SU2EDU(Executable):
    """
    SU2EDU interface with some convenience functions
    """

    def __init__(self):
        self.cwd = tempfile.mkdtemp()
        Executable.__init__(self, 'su2edu.exe',cwd=self.cwd)
        copy_tree(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'su2edu'), self.cwd)
        self.tempdirs = [self.cwd]

    def airfoil(self, x, y):
        # Temporary file
        self.input_airfoil = tempfile.NamedTemporaryFile(delete=False, dir=self.cwd)
        self.input_airfoil.close()
        self.tempfiles.append(self.input_airfoil)
        # Data
        data = np.array([x[:-1], y[:-1]])
        data = data.T
        np.savetxt(self.input_airfoil.name, data, fmt=['%f', '%f'])

    def execute(self, Re):
        if Re:
            configname = 'ConfigFile_RANS.cfg'
            initialize = '1'
        else:
            configname = 'ConfigFile_INV.cfg'
            initialize = '0'

        np.savetxt(os.path.join(self.cwd, configname), self.config, delimiter='\n', fmt="%s")
        self.cmd(initialize)
        self.cmd(self.input_airfoil.name)
        self.cmd('0')
        self.cmdlog = ['']
        while not re.search('Exit Success', self.cmdlog[-1]):
            line = self.readline()
            if line:
                self.cmdlog.append(line)
        return self.cmdlog

    def output_surface(self):
        self.cmdlogcheck()
        data_header = np.char.strip(
            np.genfromtxt(os.path.join(self.cwd, 'surface_flow.csv'), dtype='str', max_rows=1, delimiter=',',
                          autostrip=True), '"')
        data_array = np.loadtxt(os.path.join(self.cwd, 'surface_flow.csv'), skiprows=1, delimiter=',')
        return data_array, data_header

    def output_history(self):
        self.cmdlogcheck()
        data_header = np.char.strip(
            np.genfromtxt(os.path.join(self.cwd, 'history.csv'), dtype='str', max_rows=1, delimiter=',',
                          autostrip=True), '"')
        data_array = np.loadtxt(os.path.join(self.cwd, 'history.csv'), skiprows=1, delimiter=',')
        return data_array, data_header
