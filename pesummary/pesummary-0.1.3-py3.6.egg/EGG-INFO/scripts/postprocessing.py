#!/home/c1737564/virtualenvs/test/bin/python

# Copyright (C) 2018  Charlie Hoy <charlie.hoy@ligo.org>
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import logging
import warnings
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

import argparse
import subprocess
import socket
import os
import shutil
from glob import glob

import numpy as np
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pesummary
from pesummary.utils import run_checks
from pesummary.utils.utils import guess_url
from pesummary.utils.utils import combine_hdf_files
from pesummary.utils.utils import rename_group_or_dataset_in_hf5_file
from pesummary.webpage import webpage
from pesummary.utils import utils
from pesummary.plot import plot
from pesummary.one_format.data_format import one_format

import h5py

import copy

import lal
import lalsimulation as lalsim

__doc__ == "Parameters to run post_processing.py from the command line"


class PostProcessing():

    def __init__(self, inputs, colors="default"):
        self.inputs = inputs
        self.webdir = inputs.webdir
        self.baseurl = inputs.baseurl
        self.result_files = inputs.result_files
        self.approximant = inputs.approximant
        self.detectors = inputs.detectors
        self.dump = inputs.dump
        self.email = inputs.email
        self.user = inputs.user
        self.host = inputs.host
        self.config = inputs.config
        self.colors = colors

        self.parameters = []
        self.injection_data = []
        self.samples = []
        self.maxL_samples = []

    @property
    def colors(self):
        return self._colors

    @colors.setter
    def colors(self, colors):
        if colors == "default":
            self._colors = ["#a6b3d0", "#baa997", "#FF6347", "#FFA500",
                            "#003366"]
        else:
            if not len(self.result_files) <= colors:
                raise Exception("Please give the same number of colors as "
                                "results files")
            self._colors = colors

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        parameter_list = []
        for num, results_files in enumerate(self.result_files):
            f = h5py.File(results_files, "r")
            p = [i for i in f["%s/parameter_names" %(self.approximant[num])]]
            parameter_list.append([i.decode("utf-8") for i in p])
            f.close()
        self._parameters = parameter_list

    @property
    def injection_data(self):
        return self._injection_data

    @injection_data.setter
    def injection_data(self, injection_data):
        injection_list = []
        for num, results_files in enumerate(self.result_files):
            f = h5py.File(results_files, "r")
            inj_p = [i for i in f["%s/injection_parameters" %(self.approximant[num])]]
            inj_p = [i.decode("utf-8") for i in inj_p]
            inj_data = [i for i in f["%s/injection_data" %(self.approximant[num])]]
            injection_list.append({i:j for i,j in zip(inj_p, inj_data)})
        self._injection_data = injection_list

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, samples):
        sample_list = []
        for num, results_files in enumerate(self.result_files):
            f = h5py.File(results_files, "r")
            s = [i for i in f["%s/samples" %(self.approximant[num])]]
            sample_list.append(s)
        self._samples = sample_list

    @property
    def maxL_samples(self):
        return self._maxL_samples

    @maxL_samples.setter
    def maxL_samples(self, maxL_samples):
        key_data = self._key_data()
        maxL_list = []
        for num, i in enumerate(self.parameters):
            dictionary = {j: key_data[num][j]["maxL"] for j in i}
            dictionary["approximant"] = self.approximant[num]
            maxL_list.append(dictionary)
        self._maxL_samples = maxL_list
            
    def _key_data(self):
        key_data_list = []
        for num, i in enumerate(self.samples):
            data = {}
            likelihood_ind = self.parameters[num].index("log_likelihood")
            logL = [j[likelihood_ind] for j in i]
            for ind, j in enumerate(self.parameters[num]):
                index = self.parameters[num].index("%s" %(j))
                subset = [k[index] for k in i]
                data[j] = {"mean": np.mean(subset),
                           "median": np.median(subset),
                           "maxL": subset[logL.index(np.max(logL))],
                           "std": np.std(subset)}
            key_data_list.append(data)
        return key_data_list

