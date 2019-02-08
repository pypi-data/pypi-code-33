#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-12-28
# Last Modified: 2018-12-28
# Vanderbilt University
from __future__ import (absolute_import, division, print_function)
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon, 2018"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  'CatlClassTemplate']
"""
Compilation of different models corresponding to the set of catalogues used
in various of the Calderon et al. (2018, 2019) papers and analyses.
"""

## Importing modules and packages
import os
import six
import numpy as np
import pandas as pd
from   abc import ABCMeta

# Cosmo-Utils
from cosmo_utils.utils import file_utils      as cfutils
from cosmo_utils.utils import file_readers    as cfreaders

# Main package
from sdss_catl_utils.mocks_manager import catl_utils
from sdss_catl_utils.mocks_manager import mocks_defaults as md
from sdss_catl_utils.mocks_manager.catl_utils import check_input_params


## -- Functions and classes -- ##

## Class Template
@six.add_metaclass(ABCMeta)
class CatlClassTemplate(object):
    r"""
    Abstract base class of any of models for the various analyses.
    The functionality of this class is mostly trivial.
    The sole purpose of the base class is to standardize the
    attributes and methods required of any of the analyses of each
    of the different papers.
    """
    def __init__(self, **kwargs):
        r"""
        Parameters
        ------------
        catl_kind : {``data``, ``mocks``} `str`
            Kind of catalogues to download. This variable is set to
            ``mocks`` by default.

            Options:
                - ``data``: Downloads the SDSS DR7 real catalogues.
                - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

        hod_n : `int`, optional
            Number of the HOD model to use. This value is set to `0` by
            default.

        halotype : {'so', 'fof'}, `str`, optional
            Type of dark matter definition to use. This value is set to
            ``so`` by default.

            Options:
                - ``so``: Spherical Overdensity halo definition.
                - ``fof``: Friends-of-Friends halo definition.

        clf_method : {1, 2, 3}, `int`, optional
            Method for assigning galaxy properties to mock galaxies.
            This variable dictates how galaxies are assigned
            luminosities or stellar masses based on their galaxy type
            and host halo's mass. This variable is set to ``1`` by
            default.

            Options:
                - ``1``: Independent assignment of (g-r) colour, sersic, and specific star formation rate (`logssfr`)
                - ``2``: (g-r) colour dictates active/passive designation and draws values independently.
                - ``3``: (g-r) colour dictates active/passive designation, and assigns other galaxy properties for that given galaxy.

        clf_seed : `int`, optional
            Value of the random seed used for the conditional luminosity function.
            This variable is set to ``1235`` default.

        dv : `float`, optional
            Value for the ``velocity bias`` parameter. It is the difference
            between the galaxy and matter velocity profiles.

            .. math::
                dv = \\frac{v_{g} - v_{c}}{v_{m} - v_{c}}

            where :math:`v_g` is the galaxy's velocity; :math:`v_m`, the
            matter velocity.

        sigma_clf_c : `float`, optional
            Value of the scatter in log(L) for central galaxies, when being
            assigned during the `conditional luminosity function` (CLF).
            This variable is set to ``0.1417`` by default.

        sample : {'19', '20', '21'}, `str`, optional
            Luminosity of the SDSS volume-limited sample to analyze.
            This variable is set to ``'19'`` by default.

            Options:
                - ``'19'``: :math:`M_r = 19` volume-limited sample
                - ``'20'``: :math:`M_r = 20` volume-limited sample
                - ``'21'``: :math:`M_r = 21` volume-limited sample

        type_am : {'mr', 'mstar'}, `str`, optional
            Type of Abundance matching used in the catalogue. This
            variable is set to ``'mr'`` by default.

            Options:
                - ``'mr'``: Luminosity-based abundance matching used
                - ``'mstar'``: Stellar-mass-based abundance matching used.

        cosmo_choice : { ``'LasDamas'``, ``'Planck'``} `str`, optional
            Choice of cosmology to use. This variable is set to ``LasDamas``
            by default.

            Options:
                - ``LasDamas`` : Uses the cosmological parameters from the 
                    `LasDamas <http://lss.phy.vanderbilt.edu/lasdamas/simulations.html>`_ simulations.
                - ``Planck`` : Uses the Planck 2015 cosmology.

        perf_opt : `bool`, optional
            If `True`, it chooses to analyze the ``perfect`` version of
            the synthetic galaxy/group galaxy catalogues. Otherwise,
            it downloads the catalogues with group-finding errors
            included. This variable is set to ``False`` by default.

        environ_name : `str`
            Name of the environment variable to assign to ``outdir``.
            This variable is set to the default ``environ_name`` from
            `~sdss_catl_utils.mocks_manager.mocks_default`
        """
        # Assigning variables
        self.catl_kind    = kwargs.get('catl_kind', md.catl_kind)
        self.hod_n        = kwargs.get('hod_n', md.hod_n)
        self.halotype     = kwargs.get('halotype', md.halotype)
        self.clf_method   = kwargs.get('clf_method', md.clf_method)
        self.clf_seed     = kwargs.get('clf_seed', md.clf_seed)
        self.dv           = kwargs.get('dv', md.dv)
        self.sigma_clf_c  = kwargs.get('sigma_clf_c', md.sigma_clf_c)
        self.sample       = kwargs.get('sample', md.sample)
        self.type_am      = kwargs.get('type_am', md.type_am)
        self.cosmo_choice = kwargs.get('cosmo_choice', md.cosmo_choice)
        self.perf_opt     = kwargs.get('perf_opt', md.perf_opt)
        self.remove_files = kwargs.get('remove_files', md.remove_files)
        self.environ_name = kwargs.get('environ_name', md.environ_name)
        # Other variables
        self.sample_Mr    = 'Mr{0}'.format(self.sample)
        self.sample_s     = str(self.sample)
        # Checking input parameters
        self._check_input_parameters()
        # Dictionary of input parameters
        self.param_dict = self.get_params_dict()

    # Checking input parameters to make sure they are `expected`
    def _check_input_parameters(self):
        r"""
        Checks whether or not the input parameters are what is expected or not.
        """
        ## Checking for input TYPES
        # `catl_kind`
        check_input_params(self.catl_kind, 'catl_kind', check_type='type')
        check_input_params(self.catl_kind, 'catl_kind', check_type='vals')
        # `hod_n`
        check_input_params(self.hod_n, 'hod_n', check_type='type')
        check_input_params(self.hod_n, 'hod_n', check_type='vals')
        # `halotype`
        check_input_params(self.halotype, 'halotype', check_type='type')
        check_input_params(self.halotype, 'halotype', check_type='vals')
        # `clf_method`
        check_input_params(self.clf_method, 'clf_method', check_type='type')
        check_input_params(self.clf_method, 'clf_method', check_type='vals')
        # `clf_seed`
        check_input_params(self.clf_seed, 'clf_seed', check_type='type')
        # `dv`
        check_input_params(self.dv, 'dv', check_type='type')
        # `sigma_clf_c`
        check_input_params(self.sigma_clf_c, 'sigma_clf_c', check_type='type')
        # `sample`
        check_input_params(self.sample, 'sample', check_type='type')
        check_input_params(self.sample, 'sample', check_type='vals')
        # `type_am`
        check_input_params(self.type_am, 'type_am', check_type='type')
        check_input_params(self.type_am, 'type_am', check_type='vals')
        # `cosmo_choice`
        check_input_params(self.cosmo_choice, 'cosmo_choice', check_type='type')
        check_input_params(self.cosmo_choice, 'cosmo_choice', check_type='vals')
        # `perf_opt`
        check_input_params(self.perf_opt, 'perf_opt', check_type='type')
        # `remove_files`
        check_input_params(self.remove_files, 'remove_files', check_type='type')
        # `environ_name`
        check_input_params(self.environ_name, 'environ_name', check_type='type')

    # Get dictionary of input parameters
    def get_params_dict(self):
        r"""
        Gets the dictionary of input parameters for the given model.

        Returns
        ---------
        param_dict : `dict`
            Dictionary of input parameters for the chosen combination of
            parameters.

        Examples
        ----------
        After having initializing an `CatlUtils` object, one can easily
        recover the set of input parameters used.

        >>> from sdss_catl_utils.models.catl_models import CatlUtils
        >>> catl_params_dict = {'catl_kind': 'mocks', 'clf_seed': 3} # Catalogue parameters
        >>> catl_obj = CatlUtils(**catl_params_dict) # Initialing object

        The dictionary of parameters is saved as ``self.param_dict`` for
        the class object. It can be easily accessed by:

        >>> catl_obj.param_dict # doctest: +SKIP

        Or, it can also be accessed as:

        >>> catl_obj.get_params_dict() # doctest: +SKIP
        
        For example, in order to print out the list of input parameters,
        one can do the following:

        >>> param_dict = catl_obj.param_dict # doctest: +SKIP
        >>> param_dict # doctest: +SKIP
        {'catl_kind': 'mocks',
         'hod_n': 0,
         'halotype': 'fof',
         'clf_method': 1,
         'clf_seed': 3,
         'dv': 1.0,
         'sigma_clf_c': 0.1417,
         'sample': '19',
         'type_am': 'mr',
         'cosmo_choice': 'LasDamas',
         'perf_opt': False,
         'remove_files': False,
         'environ_name': 'sdss_catl_path',
         'sample_Mr': 'Mr19',
         'sample_s': '19'}

        This dictionary can now be used in other parts of one's analysis,
        or as a reference of the parameters used.
        """
        # Initializing dictionary
        param_dict = {}
        # Populating dictionary
        param_dict['catl_kind'   ] = self.catl_kind
        param_dict['hod_n'       ] = self.hod_n
        param_dict['halotype'    ] = self.halotype
        param_dict['clf_method'  ] = self.clf_method
        param_dict['clf_seed'    ] = self.clf_seed
        param_dict['dv'          ] = self.dv
        param_dict['sigma_clf_c' ] = self.sigma_clf_c
        param_dict['sample'      ] = self.sample
        param_dict['type_am'     ] = self.type_am
        param_dict['cosmo_choice'] = self.cosmo_choice
        param_dict['perf_opt'    ] = self.perf_opt
        param_dict['remove_files'] = self.remove_files
        param_dict['environ_name'] = self.environ_name
        param_dict['sample_Mr'   ] = self.sample_Mr
        param_dict['sample_s'    ] = self.sample_s

        return param_dict
