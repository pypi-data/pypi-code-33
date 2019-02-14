#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-12-28
# Last Modified: 2018-12-29
# Vanderbilt University
from __future__ import (absolute_import, division, print_function)
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon, 2018"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  'DownloadManager',
                    'CatlUtils',
                    'SDSSConformity',
                    'SDSSCatlAnalysis',
                    'SDSSMLAnalysis']
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
from cosmo_utils.utils import work_paths      as cwpaths
from cosmo_utils.utils import web_utils       as cweb

# Main package
from sdss_catl_utils.mocks_manager import catl_utils
from sdss_catl_utils.mocks_manager import mocks_defaults as md
from sdss_catl_utils.models.catl_models_template import CatlClassTemplate

## -- Functions and classes -- ##

## Main class to download all of the catalogues
class DownloadManager(CatlClassTemplate):
    """
    Class used to scrape the web for galaxy and group galaxy
    catalogue data and cache the downloaded catalogues.

    For list of available pre-processed galaxy- and group-galaxy
    catalogues provided by ``sdss_catl_utils``, see

    """
    def __init__(self, **kwargs):
        """
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

        catl_type : {'mr', 'mstar'}, `str`, optional
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
            If True, it chooses to analyze the ``perfect`` version of
            the synthetic galaxy/group galaxy catalogues. Otherwise,
            it downloads the catalogues with group-finding errors
            included. This variable is set to ``False`` by default.

        environ_name : `str`
            Name of the environment variable to assign to ``outdir``.
            This variable is set to the default ``environ_name`` from
            `~sdss_catl_utils.mocks_manager.mocks_default`

        Examples
        ----------

        >>> from sdss_catl_utils.models.catl_models import DownloadManager
        """
        # Super class from template
        super(DownloadManager, self).__init__(**kwargs)

    # Writes the location of catalogues as environment variable
    def _environ_variable_write(self, outdir):
        """
        Writes the location of catalogues as environment variable

        Parameters
        ------------
        outdir : `str`
            Path to the output directory, to which catalogues can be saved
            and stored.
        """
        # Bashrc and bash_profile location
        bashrc_path = os.path.expanduser('~/.bashrc')
        bash_profile_path = os.path.expanduser('~/.bash_profile')
        # Checking if files exist
        if os.path.exists(bashrc_path):
            conf_file = bashrc_path
        elif os.path.exists(bash_profile):
            conf_file = bash_profile
        else:
            conf_file = bashrc_file
            open(conf_file, 'a').close()
            print('`bashrc` file created: `{0}`'.format(bashrc_path))
            cfutils.File_Exists(conf_file)
        ##
        ## Checking that ``outdir`` exists
        assert(os.path.exists(outdir))
        # Appending to ``conf_file`` file if necessary
        if not os.environ.get(self.environ_name):
            with open(conf_file, 'a') as outfile:
                # String for exporting environment variable
                export_str = 'export {0}={1}'.format(   self.environ_name,
                                                        outdir)
                # Appending to file
                outfile.write('\n\n')
                outfile.write('## Output directory for SDSS Catalogues\n')
                outfile.write(export_str)
                outfile.write('\n\n')
                # Printing out message
                msg = '>> The system variable `{0}` has been '
                msg += 'added to your `{1}` file!'
                msg = msg.format(self.environ_name, conf_file)
                print(msg)

    # Checks file and folder structures
    def directory_tree_check(self, loc='./'):
        """
        Checks the file structure of the current directory, and determines
        if it is a ``git`` repository or not. If not, it will save the
        catalogues to a location in the user's home directory, under
        ``~/user/.sdss_catls``. It also adds the location of the
        output directory as an environment variable.

        Parameters
        ------------
        loc : `str`
            Path to the directory being analyzed for possible git
            initialization directory. This variable is set to ``./``
            by default.

        Returns
        ------------
        outdir : `str`
            Path to the output directory, to which catalogues can be saved
            and stored.
        """
        # Defining output directory
        try:
            # Environment variable
            catl_maindir = os.environ[self.environ_name]
            # Output directory - Check if directory exists
            outdir = os.path.join(  catl_maindir,
                                    'data',
                                    'external',
                                    'SDSS/')
            cfutils.Path_Folder(outdir)
            assert(os.path.exists(outdir))
        except KeyError:
            # Git Repository
            try:
                base_dir = cwpaths.git_root_dir(loc)
                outdir   = os.path.join(base_dir, 'data', 'external', 'SDSS/')
                mod_dir  = cwpaths.git_root_dir(path=os.path.realpath(__file__))
                # Creating directory if necessary
                if not (os.path.realpath(mod_dir) != os.path.realpath(base_dir)):
                    # Creating new directory
                    cfutils.Path_Folder(outdir)
                    assert(os.path.exists(outdir))
                else:
                    msg = '>> Current directory ({0}) is not supported! '
                    msg += 'You must move directories!'
                    msg = msg.format(outdir)
            except:
                # Home directory location
                base_dir = os.path.join(os.path.expanduser('~'),
                                        '.sdss_catls')
                # Output directory
                outdir   = os.path.join(base_dir,
                                        'data',
                                        'external',
                                        'SDSS/')
                # Creating directory
                cfutils.Path_Folder(outdir)
                assert(os.path.exists(outdir))
            ##
            ## Adding directory as environment variable
            self._environ_variable_write(outdir)

        return outdir

    # Output directory for local copies of catalogues
    def local_outdir_path(self, loc='./', catl_type='memb', catl_kind='data',
        check_exist=False, create_dir=False, perf_opt=False):
        """
        Output directory for ``local`` copies of the catalogues.

        Parameters
        ------------
        loc : `str`
            Path to the directory being analyzed for possible git
            initialization directory.

        catl_type : {'gal', 'memb', 'group'}, `str`
            Option for which kind of catalogue is being analyzed. This
            variable is set to ``memb`` by default.

            Options:
                - ``'gal'`` : Galaxy catalogue
                - ``'memb'`` : Group Member galaxy catalogue
                - ``'group'`` : Group galaxy catalogue

        catl_kind : {``data``, ``mocks``} `str`
            Kind of catalogues to download. This variable is set to
            ``mocks`` by default.

            Options:
                - ``data``: Downloads the SDSS DR7 real catalogues.
                - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

        check_exist : `bool`, optional
            If `True`, it checks for whether or not the file exists.
            This variable is set to `False` by default.

        create_dir : `bool`, optional
            If `True`, it creates the directory if it does not exist.
            This variable is set to `False` by default.

        perf_opt : `bool`, optional
            If True, it chooses to analyze the ``perfect`` version of
            the synthetic galaxy/group galaxy catalogues. Otherwise,
            it downloads the catalogues with group-finding errors
            included. This variable is set to ``False`` by default.

        Returns
        ----------
        outdir_local : `str`
            Path to the local output directory, based on the type of
            catalogues and input parameters.
        """
        ## Checking input parameters
        # `loc` - Type
        if not (isinstance(loc, str)):
            msg = '`loc` ({0}) is not a valid input type!'
            msg = msg.format(loc)
            raise TypeError(loc)
        # `catl_type` - Value
        catl_type_arr = ['gal', 'memb', 'group']
        if not (catl_type in catl_type_arr):
            msg = '>>> `catl_type` ({0}) is not a valid input!'
            msg = msg.format(catl_type)
            raise ValueError(msg)
        # `catl_type` - Type
        if not (isinstance(catl_type, str)):
            msg = '>>> `catl_type` ({0}) is not a valid type!'
            msg = msg.format(type(catl_type))
            raise TypeError(msg)
        # ``catl_kind`` - Input Value
        catl_kind_arr = ['data', 'mocks']
        if not (catl_kind in catl_kind):
            msg = '>>> `catl_kind` ({0}) is not a valid input!'
            msg = msg.format(catl_kind)
            raise ValueError(msg)
        # ``catl_kind`` - Type
        if not (isinstance(catl_kind, str)):
            msg = '>>> `catl_kind` ({0}) is not a valid type!'
            msg = msg.format(type(catl_kind))
            raise TypeError(msg)
        # `perf_opt` - Type
        if not (isinstance(perf_opt, bool)):
            msg = '`perf_opt` ({0}) is not a valid type!'
            msg = msg.format(type(perf_opt))
            raise TypeError(msg)
        # `check_exist` - Type
        if not (isinstance(check_exist, bool)):
            msg = '`check_exist` ({0}) is not a valid input type!'
            msg = msg.format(type(check_exist))
            raise TypeError(msg)
        # `create_dir` - Type
        if not (isinstance(create_dir, bool)):
            msg = '`create_dir` ({0}) is not a valid input type!'
            msg = msg.format(type(create_dir))
            raise TypeError(msg)
        ##
        ## Local base path
        local_base   = self.directory_tree_check(loc=loc)
        ## Local Output directory
        local_outdir = os.path.join(local_base,
                                    self._catl_prefix(
                                        catl_kind=catl_kind,
                                        catl_type=catl_type,
                                        perf_opt=perf_opt))
        # Creating directory
        if create_dir:
            cfutils.Path_Folder(catl_output_dir)
        # Check for its existence
        if check_exist:
            if not (os.path.exists(catl_output_dir)):
                msg = '`catl_output_dir` ({0}) was not found!'.format(
                    catl_output_dir)
                raise FileNotFoundError(msg)

        return local_outdir

    # Prefix of the catalogues being downloaded
    def _catl_prefix(self, catl_type='memb', catl_kind='mocks',
        perf_opt=False):
        r"""
        Prefix of the paths based on the type of catalogues and input
        parameters chosen.

        Parameters
        ------------
        catl_type : {'gal', 'memb', 'group'}, `str`
            Option for which kind of catalogue is being analyzed. This
            variable is set to ``memb`` by default.

            Options:
                - ``'gal'`` : Galaxy catalogue
                - ``'memb'`` : Group Member galaxy catalogue
                - ``'group'`` : Group galaxy catalogue

        catl_kind : {``data``, ``mocks``} `str`
            Kind of catalogues to download. This variable is set to
            ``mocks`` by default.

            Options:
                - ``data``: Downloads the SDSS DR7 real catalogues.
                - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

        perf_opt : `bool`, optional
            If `True`, it chooses to analyze the ``perfect`` version of
            the synthetic galaxy/group galaxy catalogues. Otherwise,
            it downloads the catalogues with group-finding errors
            included. This variable is set to ``False`` by default.

        Returns
        ----------
        catl_prefix : `str`
            Prefix of the paths based on the type of catalogues and
            input parameters.
        """
        ## Checking input parameters
        # `catl_type` - Type and Value
        catl_utils.check_input_params(catl_type, 'catl_type', check_type='type')
        catl_utils.check_input_params(catl_type, 'catl_type', check_type='vals')
        # `catl_kind` - Type and Value
        catl_utils.check_input_params(catl_kind, 'catl_kind', check_type='type')
        catl_utils.check_input_params(catl_kind, 'catl_kind', check_type='vals')
        # `perf_opt`  - Type
        catl_utils.check_input_params(perf_opt, 'perf_opt', check_type='type')
        ##
        ## Catalogue prefix
        catl_prefix = catl_utils.catl_prefix_main(  catl_type=catl_type,
                                                    catl_kind=catl_kind,
                                                    hod_n=self.hod_n,
                                                    halotype=self.halotype,
                                                    clf_method=self.clf_method,
                                                    clf_seed=self.clf_seed,
                                                    dv=self.dv,
                                                    sigma_clf_c=self.sigma_clf_c,
                                                    sample=self.sample,
                                                    type_am=self.type_am,
                                                    perf_opt=perf_opt)

        return catl_prefix

    # Checks that the combination of parameters is valid
    def catl_web_params_check(self, catl_kind='mocks', catl_type='memb',
        ext='hdf5', return_files_url=False, perf_opt=False):
        """
        Checks that the combination of parameters is valid and that there
        are catalogues available to download.

        Parameters
        ------------
        catl_kind : {``data``, ``mocks``} `str`
            Kind of catalogues to download. This variable is set to
            ``mocks`` by default.

            Options:
                - ``data``: Downloads the SDSS DR7 real catalogues.
                - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

        catl_type : {'gal', 'memb', 'group'}, `str`
            Option for which kind of catalogue is being analyzed. This
            variable is set to ``memb`` by default.

            Options:
                - ``'gal'`` : Galaxy catalogue
                - ``'memb'`` : Group Member galaxy catalogue
                - ``'group'`` : Group galaxy catalogue

        ext : {'hdf5'} `str`
            File extension used for the catalogues. This variable is set
            to ``hdf5`` by default.

        return_files_url : `bool`, optional
            If True, it returns an array of files from the desired combination
            of parameters, and with a file extension ``ext``. This variable
            is set to ``False`` by default.

        perf_opt : `bool`, optional
            If True, it chooses to analyze the ``perfect`` version of
            the synthetic galaxy/group galaxy catalogues. Otherwise,
            it downloads the catalogues with group-finding errors
            included. This variable is set to ``False`` by default.

        Returns
        ------------
        catl_url : `str`
            URL of the files being downloaded.

        catl_files_url : `numpy.ndarray`, optional
        """
        ## Checking input parameters
        # `catl_type` - Input variable
        catl_type_arr = ['gal', 'memb', 'group']
        if not (catl_type in catl_type_arr):
            msg = '>>> `catl_type` ({0}) is not a valid input!'
            msg = msg.format(catl_type)
            raise ValueError(msg)
        # `catl_type` - Type
        if not (isinstance(catl_type, str)):
            msg = '>>> `catl_type` ({0}) is not a valid type!'
            msg = msg.format(type(catl_type))
            raise TypeError(msg)
        # ``catl_kind`` - Input Value
        catl_kind_arr = ['data', 'mocks']
        if not (catl_kind in catl_kind):
            msg = '>>> `catl_kind` ({0}) is not a valid input!'
            msg = msg.format(catl_kind)
            raise ValueError(msg)
        # ``catl_kind`` - Type
        if not (isinstance(catl_kind, str)):
            msg = '>>> `catl_kind` ({0}) is not a valid type!'
            msg = msg.format(type(catl_kind))
            raise TypeError(msg)
        # `ext` - Value
        ext_arr = ['hdf5']
        if not (ext in ext_arr):
            msg = '`ext` ({0}) is not a valid input parameter!'
            msg = msg.format(ext)
            raise ValueError(msg)
        # ``return_files_url``
        if not (isinstance(return_files_url, bool)):
            msg = '>>> `return_files_url` ({0}) is not a valid input type!'
            msg = msg.format(type(return_files_url))
            raise TypeError(msg)
        # `perf_opt` - Type
        if not (isinstance(perf_opt, bool)):
            msg = '`perf_opt` ({0}) is not a valid type!'
            msg = msg.format(type(perf_opt))
            raise TypeError(msg)
        ## Parsing URL
        catl_url = os.path.join(    md.sdss_catl_url,
                                    self._catl_prefix(
                                        catl_kind=catl_kind,
                                        catl_type=catl_type,
                                        perf_opt=perf_opt))
        ## Check that URL exists
        cweb.url_checker(catl_url)
        # Returning files
        if not return_files_url:
            return catl_url
        else:
            # Checking that there are files available
            catl_files_url = cweb.url_file_list(catl_url, ext)
            # Returning elements
            return catl_url, catl_files_url

    # Downloads the catalogues to the corresponding Output directory
    def catl_download(self, outdir='./', download_type='all', ext='hdf5',
        print_outdir=False):
        """
        Downloads the corresponding catalogues to the designated folder.

        Parameters
        ------------
        outdir : `str`, optional
            Output directory, to which catalogues will be saved. This
            variable is set to the default location of
            `~directory_tree_check`. This variable is set to ``./``
            by default.

        download_type : {``all``, ``data``, ``mocks``} `str`, optional
            Type of catalogues to download. This variable is set to ``all``
            by default.

            Options:
                - ``'data'``: Downloads the SDSS `data` catalogues.
                - ``'mocks'``: Downloads the SDSS synthetic catalogues.
                - ``'all'``: Downloads both ``data`` and ``mocks`` catalogues.

        ext : {'hdf5'} `str`
            File extension used for the catalogues. This variable is set
            to ``hdf5`` by default.

        print_outdir : `bool`, optional
            If `True`, it prints out the path to the output directories
            of the catalogues.
        
        Examples
        ----------

        >>> # To download the synthetic catalogues
        >>> from sdss_catl_utils.models.catl_models import DownloadManager
        >>>
        >>> # Downloading catalogues
        >>> A = DownloadManager()
        >>> A.catl_download(outdir='./', download_type='all') # doctest: +SKIP
        >>>
        """
        file_msg = cfutils.Program_Msg(__file__)
        ## Checking input parameters
        # `download_type` - Value
        download_type_arr = ['all', 'data', 'mocks']
        if not (download_type in download_type_arr):
            msg = '`download_type` ({0}) is not a valid input parameter!'
            msg = msg.format(download_type)
            raise ValueError(msg)
        # `download_type` - Type
        if not (isinstance(download_type, str)):
            msg = '`download_type` ({0}) is not a valid input type!'
            msg = msg.format(type(download_type))
            raise TypeError(msg)
        # `outdir` - Type
        if not (isinstance(outdir, str)):
            msg = '`outdir` ({0}) is not a valid input type!'
            msg = msg.format(type(outdir))
            raise TypeError(msg)
        # `ext` - Type
        if not (isinstance(ext, str)):
            msg = '`ext` ({0}) is not a valid input type!'
            msg = msg.format(type(ext))
            raise TypeError(msg)
        # `ext` - Value
        ext_arr = ['hdf5']
        if not (ext in ext_arr):
            msg = '`ext` ({0}) is not a valid input parameter!'
            msg = msg.format(ext)
            raise ValueError(msg)
        ##
        ## Downloading catalogues
        # `download_type` Array
        if (download_type == 'mocks'):
            download_arr = ['mocks']
        elif (download_type == 'data'):
            download_arr = ['data']
        elif (download_type == 'all'):
            download_arr = ['data', 'mocks']
        # `catl_type` array
        catl_type_arr = ['memb', 'group']
        # Looping over different options
        for download_opt_ii in download_arr:
            for catl_type_ii in catl_type_arr:
                # Local Path
                local_ii = self.local_outdir_path(  loc=outdir,
                                                    catl_type=catl_type_ii,
                                                    catl_kind=download_opt_ii)
                # Web URL
                url_ii   = self.catl_web_params_check(
                                                    catl_kind=download_opt_ii,
                                                    catl_type=catl_type_ii,
                                                    ext=ext,
                                                    return_files_url=False)
                ##
                ## Downloading catalogues to corresponding catalogues
                cweb.url_files_download(url_ii,
                                        ext,
                                        local_ii,
                                        create_dir=True,
                                        check_exist=True,
                                        remove_files=self.remove_files)
                # Printing out the output directory
                if print_outdir:
                    msg = '{0} Reading ``{1}`` and saving it to ``{2}``'
                    msg = msg.format(file_msg, url_ii, local_ii)
                    print(msg)
                ##
                ## Perfect option
                if (self.perf_opt) and (download_opt_ii == 'mocks'):
                # Local Path
                    local_ii_perf = self.local_outdir_path(
                                                    loc=outdir,
                                                    catl_type=catl_type_ii,
                                                    catl_kind=download_opt_ii,
                                                    perf_opt=self.perf_opt)
                    # Web URL
                    url_ii_perf   = self.catl_web_params_check(
                                                    catl_kind=download_opt_ii,
                                                    catl_type=catl_type_ii,
                                                    ext=ext,
                                                    return_files_url=False,
                                                    perf_opt=self.perf_opt)
                    ##
                    ## Downloading catalogues to corresponding catalogues
                    cweb.url_files_download(url_ii_perf,
                                            ext,
                                            local_ii_perf,
                                            create_dir=True,
                                            check_exist=True,
                                            remove_files=self.remove_files)
                    # Printing out the output directory
                    if print_outdir:
                        msg = '{0} Reading ``{1}`` and saving it to ``{2}``'
                        msg = msg.format(file_msg, url_ii_perf, local_ii_perf)
                        print(msg)

## Main Class to handle catalogues
class CatlUtils(CatlClassTemplate):
    """
    Class used to handle the galaxy/group galaxy/group catalogues, *after*
    the catalogues have been downloaded. This class has functions to read,
    modify, and analyze the galaxy/group catalogues.

    For a list of available pre-processed galaxy- and group-galaxy
    catalogues provided by ``sdss_catl_utils``, see ...
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

        Examples
        ----------

        >>> from sdss_catl_utils.models.catl_models import CatlUtils

        If one wants to initialize an ``catalogue`` object with the default
        input parameters, one could write:

        >>> catl_obj = CatlUtils() # Initialzing catalogue object

        However, if one wants to have a `modified` version of ``catl_obj``,
        one can pass a dictionary with the proper set of input parameters:

        >>> params_d = {'catl_kind': 'mocks', 'clf_method': 3, 'clf_seed': 123}
        >>> catl_obj = CatlUtils(**params_d)

        This will create an `catalogue object` that corresponds to ``mocks``
        catalogues with ``clf_method = 3`` and ``clf_seed = 123``.
        
        Notes
        ---------

        There are many combinations of parameters that could be performed.
        `However, note that not all variations exist and would not be
        available for download/analysis`!
        """
        # Super class from template
        super(CatlUtils, self).__init__(**kwargs)

    # Main directory path - Path to which all catalogues are saved
    def main_dir(self):
        """
        Path to the main directory, in which all catalogues are stored.
        This directory depends on your installation of `SDSS_Catl_Utils`
        and on your current working space.

        Returns
        ---------
        main_dirpath : `str`
            Path to the main directory, in which all catalogues are stored.
            It uses the environment variable ``environ_name`` from
            the class.

        Examples
        ----------
        The main directory of the catalogues can be easily accessed after
        having created an object for the combination of input parameters
        for the catalogues.
        
        >>> from sdss_catl_utils.models.catl_models import CatlUtils
        >>> catl_params_dict = {'catl_kind': 'mocks', 'clf_seed': 3} # Catalogue parameters
        >>> catl_obj = CatlUtils(**catl_params_dict) # Initialing object

        One can access the directory, under which the galaxy-
        and group-catalogues are saved, by typing:

        >>> catl_obj.main_dir() # doctest: +SKIP

        This will return the path of the directory.

        """
        if os.environ.get(self.environ_name):
            main_dirpath = os.path.join(os.environ[self.environ_name],
                                        'data',
                                        'external',
                                        'SDSS/')
            # Checking directory exists
            if not os.path.exists(main_dirpath):
                msg = '`main_dirpath` ({0}) does not exist!'.format(
                    main_dirpath)
                raise ValueError(msg)
        else:
            msg = '`environ_name` ({0}) is not a system variable! '
            msg += 'Please download the catalogues and add the path '
            msg += 'to the catalogues as `{0}` environment variable!'
            msg = msg.format(self.environ_name)
            raise ValueError(msg)

        return main_dirpath

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

    # Location prefix
    def _catl_prefix(self, catl_type='memb', catl_kind='mocks',
        perf_opt=False):
        r"""
        Prefix of the paths based on the type of catalogues and input
        parameters chosen.

        Parameters
        ------------
        catl_type : {'gal', 'memb', 'group'}, `str`
            Option for which kind of catalogue is being analyzed. This
            variable is set to ``memb`` by default.

            Options:
                - ``'gal'`` : Galaxy catalogue
                - ``'memb'`` : Group Member galaxy catalogue
                - ``'group'`` : Group galaxy catalogue

        catl_kind : {``data``, ``mocks``} `str`
            Kind of catalogues to download. This variable is set to
            ``mocks`` by default.

            Options:
                - ``data``: Downloads the SDSS DR7 real catalogues.
                - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

        perf_opt : `bool`, optional
            If `True`, it chooses to analyze the ``perfect`` version of
            the synthetic galaxy/group galaxy catalogues. Otherwise,
            it downloads the catalogues with group-finding errors
            included. This variable is set to ``False`` by default.

        Returns
        ----------
        catl_prefix : `str`
            Prefix of the paths based on the type of catalogues and
            input parameters.
        """
        ## Checking input parameters
        # `catl_type` - Type and Value
        catl_utils.check_input_params(catl_type, 'catl_type', check_type='type')
        catl_utils.check_input_params(catl_type, 'catl_type', check_type='vals')
        # `catl_kind` - Type and Value
        catl_utils.check_input_params(catl_kind, 'catl_kind', check_type='type')
        catl_utils.check_input_params(catl_kind, 'catl_kind', check_type='vals')
        # `perf_opt`  - Type
        catl_utils.check_input_params(perf_opt, 'perf_opt', check_type='type')
        ##
        ## Catalogue prefix
        catl_prefix = catl_utils.catl_prefix_main(  catl_type=catl_type,
                                                    catl_kind=catl_kind,
                                                    perf_opt=perf_opt,
                                                    hod_n=self.hod_n,
                                                    halotype=self.halotype,
                                                    clf_method=self.clf_method,
                                                    clf_seed=self.clf_seed,
                                                    dv=self.dv,
                                                    sigma_clf_c=self.sigma_clf_c,
                                                    sample=self.sample,
                                                    type_am=self.type_am)

        return catl_prefix

    # Location of galaxy/group catalogues with specified parameters
    def catls_dir(self, catl_type='memb', catl_kind='mocks',
        print_filedir=False):
        r"""
        Location of the group and group galaxy catalogues with the specified
        parameters.

        Parameters
        ------------
        catl_type : {'gal', 'memb', 'group'}, `str`
            Option for which kind of catalogue is being analyzed. This
            variable is set to ``memb`` by default.

            Options:
                - ``'gal'`` : Galaxy catalogue
                - ``'memb'`` : Group Member galaxy catalogue
                - ``'group'`` : Group galaxy catalogue

        catl_kind : {``data``, ``mocks``} `str`
            Kind of catalogues to download. This variable is set to
            ``mocks`` by default.

            Options:
                - ``data``: Downloads the SDSS DR7 real catalogues.
                - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

        print_filedir : `bool`, optional
            If `True`, the path of the catalogue directory is printed
            onto the screen. This variable is set to ``False`` by default.

        Returns
        ---------
        catls_dirpath : `str`
            Path to the location of the group and galaxy catalogues with
            the specified parameters.

        Notes
        ---------
        This method can be used to access the different `kinds` of
        catalogues, i.e. galaxy-, member-, and group-catalogues for different
        combinations of input parameters.

        Examples
        ----------
        `catls_dir` can be used to explore the directories that host different
        `kinds` of catalogues, i.e. galaxy-, member-, and group-catalogues
        for various combinations of input parameters.

        For example, if one wants to read the ``member`` galaxy catalogue,
        i.e. a catalogue with both `galaxy` and `group` information, for
        ``mocks`` catalogues, one could easily write:

        >>> memb_dir = catls_dir(catl_type='memb', catl_kind='mocks') # doctest: +SKIP

        This will return the path to the `member` galaxy catalogues directory
        with the synthetic catalogues in it. This method only returns
        the path of the directory, and not the path to the actual
        files in the directory. To accomplish this, one would need to use
        the function `catl_arr_extract`.
        """
        ## Checking input parameters
        # `catl_type` - Value
        catl_type_arr = ['gal', 'memb', 'group']
        if not (catl_type in catl_type_arr):
            msg = '>>> `catl_type` ({0}) is not a valid input!'
            msg = msg.format(catl_type)
            raise ValueError(msg)
        # `catl_type` - Type
        if not (isinstance(catl_type, str)):
            msg = '>>> `catl_type` ({0}) is not a valid type!'
            msg = msg.format(type(catl_type))
            raise TypeError(msg)
        # ``catl_kind`` - Input Value
        catl_kind_arr = ['data', 'mocks']
        if not (catl_kind in catl_kind):
            msg = '>>> `catl_kind` ({0}) is not a valid input!'
            msg = msg.format(catl_kind)
            raise ValueError(msg)
        # ``catl_kind`` - Type
        if not (isinstance(catl_kind, str)):
            msg = '>>> `catl_kind` ({0}) is not a valid type!'
            msg = msg.format(type(catl_kind))
            raise TypeError(msg)
        # `print_filedir` - Type
        if not (isinstance(print_filedir, bool)):
            msg = '`print_filedir` ({0}) is not a valid type!'
            msg = msg.format(type(print_filedir))
            raise TypeError(msg)
        ##
        ## Reading in environment variable
        if os.environ.get(self.environ_name):
            base_dir = self.main_dir()
            assert(os.path.exists(base_dir))
            # Parsing path to catalogues
            catls_dirpath = os.path.join(   base_dir,
                                            self._catl_prefix(
                                                catl_type=catl_type,
                                                catl_kind=catl_kind,
                                                perf_opt=self.perf_opt))
            # Check directory exists
            if not (os.path.exists(catls_dirpath)):
                msg = '>> `catls_dirpath` ({0}) does not exist!'
                msg = msg.format(catls_dirpath)
                raise ValueError(msg)

        else:
            msg = '`environ_name` ({0}) is not a system variable! '
            msg += 'Please download the catalogues and add the path '
            msg += 'to the catalogues as `{0}` environment variable!'
            msg = msg.format(self.environ_name)
            raise ValueError(msg)

        if print_filedir:
            print(catls_dirpath)

        return catls_dirpath

    # Extract the list of catalogues
    def catl_arr_extract(self, catl_type='memb', catl_kind='mocks',
        ext='hdf5', print_filedir=False, return_len=False):
        r"""
        Extracts the list of galaxy/group catalogues.

        Parameters
        --------------
        catl_type : {``gal``, ``memb``, ``group``}, `str`
            Option for which kind of catalogue is being analyzed. This
            variable is set to ``memb`` by default.

            Options:
                - ``'gal'`` : Galaxy catalogue
                - ``'memb'`` : Group Member galaxy catalogue
                - ``'group'`` : Group galaxy catalogue

        catl_kind : {``data``, ``mocks``} `str`
            Kind of catalogues to download. This variable is set to
            ``mocks`` by default.

            Options:
                - ``data``: Downloads the SDSS DR7 real catalogues.
                - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

        ext : {'hdf5'} `str`
            File extension used for the catalogues. This variable is set
            to ``hdf5`` by default.

        print_filedir : `bool`, optional
            If `True`, the path of the catalogue directory is printed
            onto the screen. This variable is set to ``False`` by default.


        Returns
        ---------
        catls_arr : `numpy.ndarray`, shape (N,)
            Array of the paths of the galaxy/group catalogues with specified
            parameters. The shape of the variable is (`N`,), where `N`,
            is the number of catalogues in the directory.

        Examples
        -----------
        This function is able to return the path to individual kinds of
        galaxy and group catalogues that meet some criteria based on the
        different combinations of input parameters.

        For example, if one wants to get the paths to the ``mocks`` ``member``
        galaxy catalogues with a ``halotype = 'fof'`` prescription, and
        following a ``clf_method = 2`` methodology, one could retrieve them
        by:
        
        >>> params_dict = {'catl_kind': 'mocks', 'halotype': 'fof', 'clf_method': 2}
        >>> catl_obj = CatlUtils(**params_dict) # doctest: +SKIP
        >>> catl_paths = catl_arr_extract(catl_type='memb', catl_kind='mocks', halotype='fof') # doctest: +SKIP

        This will return the paths to the `member` galaxy catalogues that
        meet those prescribed parameters.

        Notes
        ---------
        If no files are present or exist in the given directory, it will
        return an ``empty`` array of files.
        """
        ## Checking input parameters
        # `catl_type` - Value
        catl_type_arr = ['gal', 'memb', 'group']
        if not (catl_type in catl_type_arr):
            msg = '>>> `catl_type` ({0}) is not a valid input!'
            msg = msg.format(catl_type)
            raise ValueError(msg)
        # `catl_type` - Type
        if not (isinstance(catl_type, str)):
            msg = '>>> `catl_type` ({0}) is not a valid type!'
            msg = msg.format(type(catl_type))
            raise TypeError(msg)
        # ``catl_kind`` - Input Value
        catl_kind_arr = ['data', 'mocks']
        if not (catl_kind in catl_kind):
            msg = '>>> `catl_kind` ({0}) is not a valid input!'
            msg = msg.format(catl_kind)
            raise ValueError(msg)
        # ``catl_kind`` - Type
        if not (isinstance(catl_kind, str)):
            msg = '>>> `catl_kind` ({0}) is not a valid type!'
            msg = msg.format(type(catl_kind))
            raise TypeError(msg)
        # `ext` - Value
        ext_arr = ['hdf5']
        if not (ext in ext_arr):
            msg = '`ext` ({0}) is not a valid input parameter!'
            msg = msg.format(ext)
            raise ValueError(msg)
        # `print_filedir` - Type
        if not (isinstance(print_filedir, bool)):
            msg = '`print_filedir` ({0}) is not a valid type!'
            msg = msg.format(type(print_filedir))
            raise TypeError(msg)
        # `return_len` - Type
        if not (isinstance(return_len, bool)):
            msg = '`return_len` ({0}) is not a valid type!'
            msg = msg.format(type(return_len))
            raise TypeError(msg)
        ##
        ## Path to catalogues
        catl_dirpath = self.catls_dir(  catl_type=catl_type,
                                        catl_kind=catl_kind,
                                        print_filedir=print_filedir)
        # List of files
        catl_arr = cfutils.Index(catl_dirpath, '.' + ext)
        # Returning number of files if necessary
        if return_len:
            return catl_arr, len(catl_arr)
        else:
            return catl_arr

    # Merges the `member` and `group` catalogues into a single DataFrame
    def catl_merge(self, catl_idx=0, return_memb_group=False,
        print_filedir=False):
        """
        Merges the `member` and `group` catalogues for a given set of
        input parameters, and returns a `modified` version of the galaxy
        group catalogues with added info about the galaxy groups.

        Parameters
        ------------
        catl_idx : `int`, optional
            Index of the catalogue to match. The index must be smaller
            than the number of files returned by function `~catl_arr_extract`
            for the given combination of parameters. This variable
            is set to ``0`` by default.

        return_memb_group : `bool`, optional
            If `True`, the function returns the `member` and `group`
            catalogues along with the `merged` catalogue. This variable is
            set to `False` by default.

        print_filedir : `bool`, optional
            If `True`, the output directory is printed onto the screen.
            This variable is set to `False` by default.

        Returns
        ------------
        merged_pd : `pandas.DataFrame`
            Combined DataFrame containing both ``galaxy`` and ``group``
            information for the given combination of parameters and the
            ``catl_idx``-th catalogue(s).

        memb_pd : `pandas.DataFrame`
            Member galaxy catalogue of the ``catl_idx``-th catalogue.
            This catalogue contains the information about the ``member``
            galaxies. This object is only returned if
            ``return_memb_group == True``, 

        group_pd : `pandas.DataFrame`
            Group galaxy catalogue of the ``catl_idx``-th catalogue.
            This catalogue contains the information about the ``galaxy groups``
            This object is only returned if ``return_memb_group == True``, 

        Raises
        ------------
        SDSSCatlUtils_Error : Exception from `~sdss_catl_utils.SDSSCatlUtils_Error`
            Program exception if input parameters are `not` accepted.

        Examples
        -----------
        This function will merge the ``member`` and ``group`` catalogues into
        a single `pandas.DataFrame` object, and it can be used to merge
        two existing catalogues. For example, to merge the `member` and
        `group` catalogues using the *default* parameters, one can easily
        write:
        
        >>> merged_pd = catl_merge() # doctest: +SKIP

        The resulting object will consist of a merge between the member and
        group catalogues, with the columns pertaining to **group** properties
        having a ``GG_`` attached to their names.

        However, if one wants to merge two **mock** catalogues with
        a ``clf_method = 2`` and ``halotype = 'fof'`` prescription, one could
        easily write this:

        >>> params_dict = {'catl_kind': 'mocks', 'halotype': 'fof', 'clf_method': 2}
        >>> catl_obj = CatlUtils(**params_dict) # doctest: +SKIP
        >>> merged_pd = catl_obj.catl_merge() # doctest: +SKIP

        Additionally, one could recover the ``member`` and ``group``
        catalogues as well:

        >>> merged_pd, memb_pd, group_pd = catl_obj.catl_merge(return_memb_group=True) # doctest: +SKIP

        For more information and examples, please refer to
        :ref:`quickstart_getting_started`.
        """
        file_msg = cfutils.Program_Msg(__file__)
        ## Checking input parameters
        # `catl_idx` - Type
        catl_idx_arr = (float, int, np.int64, np.int32, np.float32, np.float64)
        if not (isinstance(catl_idx, int)):
            msg = '{0} `catl_idx` ({1}) is not a valid input type!'
            msg = msg.format(file_msg, type(catl_idx))
            raise TypeError(msg)
        else:
            catl_idx = int(catl_idx)
        # `catl_idx` - Value
        idx_range = [0, 100]
        if not ((catl_idx >= idx_range[0]) and (catl_idx < idx_range[1])):
            msg = '{0} `catl_idx` ({1}) is not within the acceptable range! '
            msg = 'Range: `{2}`'
            msg = msg.format(file_msg, catl_idx, idx_range)
            raise ValueError(msg)
        # `return_memb_group` - Type
        if not (isinstance(return_memb_group, bool)):
            msg = '{0} `return_memb_group` ({1}) is not a valid input type!'
            msg = msg.format(file_msg, type(return_memb_group))
            raise TypeError(msg)
        # `print_filedir` - Type
        if not (isinstance(print_filedir, bool)):
            msg = '{0} `print_filedir` ({1}) is not a valid input type!'
            msg = msg.format(file_msg, type(print_filedir))
            raise TypeError(msg)
        ##
        ## Extracting catalogues given input parameters
        (   memb_arr,
            memb_len) = self.catl_arr_extract(  catl_type='memb',
                                                catl_kind=self.catl_kind,
                                                return_len=True,
                                                print_filedir=print_filedir)
        #
        # Checking if `catl_idx` is less than `memb_len`
        if (catl_idx > (memb_len - 1)):
            msg = '{0} `catl_idx` ({1}) is OUT of range ({2})!'
            msg = msg.format(file_msg, catl_idx, memb_len)
            raise ValueError(msg)
        #
        # Extracting group galaxy catalogue
        memb_path = memb_arr[catl_idx]
        # ith galaxy group catalogue
        group_path_base = self.catls_dir(   catl_type='group',
                                            catl_kind=self.catl_kind,
                                            print_filedir=print_filedir)
        # Modifying path to group catalogue
        if (self.catl_kind == 'mocks'):
            group_path = os.path.join(  group_path_base,
                            os.path.basename(memb_path).replace(
                                'memb','group'))
        elif (self.catl_kind == 'data'):
            group_path = os.path.join(  group_path_base,
                            os.path.basename(memb_path).replace(
                                'Gals', 'Group'))
        # Checking if files exist
        cfutils.File_Exists(group_path)
        # Reading in member and group galaxy catalogues into DataFrames
        memb_pd  = cfreaders.read_hdf5_file_to_pandas_DF(memb_path)
        group_pd = cfreaders.read_hdf5_file_to_pandas_DF(group_path)
        # Column keys for catalogues
        (   gm_key,
            id_key,
            galtype_key) = catl_utils.catl_keys(self.catl_kind,
                                                perf_opt=self.perf_opt,
                                                return_type='list')
        # Matching keys from the group catalogue
        memb_id_unq  = np.unique(memb_pd[id_key].values)
        group_id_unq = np.unique(group_pd[id_key].values)
        if np.array_equal(memb_id_unq, group_id_unq):
            # Group column names
            group_cols = np.sort(group_pd.columns.values)
            # Sorting `memb_pd` by `id_key`
            # Member galaxy catalogue
            memb_pd.sort_values(by=id_key, inplace=True)
            memb_pd.reset_index(drop=True, inplace=True)
            # Group galaxy catalogue
            group_pd.sort_values(by=id_key, inplace=True)
            group_pd.reset_index(drop=True, inplace=True)
            # Renaming columns
            g_cols_dict = {ii: 'GG_' + ii for ii in group_cols}
            group_pd.rename(columns=g_cols_dict, inplace=True)
            group_pd.rename(columns={'GG_' + id_key: id_key}, inplace=True)
            # Merging the 2 DataFrames
            merged_pd = pd.merge(   left=memb_pd,
                                    right=group_pd,
                                    how='left',
                                    left_on=id_key,
                                    right_on=id_key)
        else:
            msg  = '{0} Lengths of the 2 DataFrames (`memb_pd`, `group_pd`) '
            msg += 'do not match! `memb_pd`: {1}, `group_pd`: {2}!'
            msg  = msg.format(file_msg, len(memb_id_unq), len(group_id_unq))
            raise SDSSCatlUtils_Error(msg)
        #
        # Returning DataFrames if necessary
        if return_memb_group:
            return_obj = (merged_pd, memb_pd, group_pd)
        else:
            return_obj = merged_pd

        return return_obj

## SDSS Conformity Analysis - Calderon et al. (2018)
class SDSSConformity(CatlUtils, DownloadManager):
    """
    Class used to handle the galaxy/group catalogues for the
    ``Calderon et al. (2018)`` analysis. This class has functions to read,
    modify, and analyze the galaxy/group catalogues for this analysis.

    The scripts and the rest of the codes for ``SDSS Conformity`` analysis
    can be found `here <https://github.com/vcalderon2009/SDSS_Conformity_Analysis>`_

    For a list of available pre-processed galaxy- and group-galaxy
    catalogues provided by ``sdss_catl_utils``, see ...
    """
    def __init__(self):
        """
        Examples
        ----------
        This class serves as the gateway for downloading and handling the
        catalogues used in the `Calderon et al. (2018) <href="https://arxiv.org/abs/1712.02797">`_
        analysis.

        One can easily *initialize* `SDSSConformity`:

        >>> from sdss_catl_utils.models.catl_models import SDSSConformity
        >>> catl_obj = SDSSConformity()

        One can also get the parameters used in the Conformity analysis:

        >>> catl_obj.param_dict # doctest: +SKIP

        The catalogues used for the analysis can be easily downloaded via the
        `~sdss_catl_utils.models.catl_models.DownloadManager.catl_download`
        method. If one wants to download the ``data`` catalogues, i.e.
        both ``memb`` and ``group`` catalogues, one can do it by:

        >>> catl_obj.catl_download(download_type='data') # doctest: +SKIP

        And if one wants to print out the paths of the URLs and output
        directories, one can do that by setting ``print_outdir = True``:

        >>> catl_obj.catl_download(download_type='data', print_outdir = True) # doctest: +SKIP

        Additionally, one could also `extract` the paths to the catalogues.
        For example, to recover the path to the ``data`` ``group`` catalogue,
        you could do that by:

        >>> catl_obj.catl_arr_extract(catl_kind='data', catl_type='group') # doctest: +SKIP

        This would return an array with the path(s) of the catalogues in question.
        """
        # Initializing dictionary
        self.init_params = self._initialize_params_dict()
        # Initializing classes
        CatlUtils.__init__(self, **self.init_params)
        DownloadManager.__init__(self, **self.init_params)
        # Metadata about the analysis
        self.publications  = ['arXiv:1712.02797', 'https://doi.org/10.1093/mnras/sty2000']
        self.github_url    = ['https://github.com/vcalderon2009/SDSS_Conformity_Analysis']
        self.analysis_docs = ['https://galactic-conformity-in-sdss-dr7.readthedocs.io']
    
    # Dictionary of input parameters
    def _initialize_params_dict(self):
        r"""
        Set the initial values of ``self.param_dict`` according to
        the SDSS Conformity analysis values.

        Returns
        ---------
        param_dict : `dict`
            Dictionary with the initial values of ``self.param_dict``
            for the ``SDSS Conformity (2018)`` analysis.
        """
        param_dict = {}
        param_dict['clf_method' ] = 1
        param_dict['clf_seed'   ] = 1235
        param_dict['halotype'   ] = 'fof'
        param_dict['hod_n'      ] = 0
        param_dict['perf_opt'   ] = False
        param_dict['sample'     ] = '19'
        param_dict['dv'         ] = 1.0
        param_dict['type_am'    ] = 'mr'
        param_dict['sigma_clf_c'] = 0.1417

        return param_dict

## Probing the stellar content of Galaxy Groups - Calderon et al. (2019)
class SDSSCatlAnalysis(CatlUtils, DownloadManager):
    """
    Class used to handle the galaxy/group catalogues for the
    ``Calderon et al. (2019)`` analysis. This class has functions to read,
    modify, and analyze the galaxy/group catalogues for this analysis.

    The scripts and the rest of the codes for ``SDSS Conformity`` analysis
    can be found `here <https://github.com/vcalderon2009/SDSS_Conformity_Analysis>`_

    For a list of available pre-processed galaxy- and group-galaxy
    catalogues provided by ``sdss_catl_utils``, see ...
    """
    def __init__(self):
        """
        Examples
        ----------
        This class serves as the gateway for downloading and handling the
        catalogues used in the `Calderon et al. (2018) <href="https://arxiv.org/abs/1712.02797">`_
        analysis.

        One can easily *initialize* `SDSSCatlAnalysis`:

        >>> from sdss_catl_utils.models.catl_models import SDSSCatlAnalysis
        >>> catl_obj = SDSSCatlAnalysis()

        One can also get the parameters used in the Conformity analysis:

        >>> catl_obj.param_dict # doctest: +SKIP

        The catalogues used for the analysis can be easily downloaded via the
        `~sdss_catl_utils.models.catl_models.DownloadManager.catl_download`
        method. If one wants to download the ``data`` catalogues, i.e.
        both ``memb`` and ``group`` catalogues, one can do it by:

        >>> catl_obj.catl_download(download_type='data') # doctest: +SKIP

        And if one wants to print out the paths of the URLs and output
        directories, one can do that by setting ``print_outdir = True``:

        >>> catl_obj.catl_download(download_type='data', print_outdir = True) # doctest: +SKIP

        Additionally, one could also `extract` the paths to the catalogues.
        For example, to recover the path to the ``data`` ``group`` catalogue,
        you could do that by:

        >>> catl_obj.catl_arr_extract(catl_kind='data', catl_type='group') # doctest: +SKIP

        This would return an array with the path(s) of the catalogues in question.
        """
        # Initializing dictionary
        self.init_params = self._initialize_params_dict()
        # Initializing classes
        CatlUtils.__init__(self, **self.init_params)
        DownloadManager.__init__(self, **self.init_params)
        # Metadata about the analysis
        # self.publications  = ['arXiv:1712.02797', 'https://doi.org/10.1093/mnras/sty2000']
        self.github_url    = ['https://github.com/vcalderon2009/SDSS_Catl_Analysis']
        # self.analysis_docs = ['https://galactic-conformity-in-sdss-dr7.readthedocs.io']
    
    # Dictionary of input parameters
    def _initialize_params_dict(self):
        r"""
        Set the initial values of ``self.param_dict`` according to
        the SDSS Conformity analysis values.

        Returns
        ---------
        param_dict : `dict`
            Dictionary with the initial values of ``self.param_dict``
            for the ``SDSS Conformity (2018)`` analysis.
        """
        param_dict = {}
        param_dict['clf_method' ] = 1
        param_dict['clf_seed'   ] = 1235
        param_dict['halotype'   ] = 'fof'
        param_dict['hod_n'      ] = 0
        param_dict['perf_opt'   ] = False
        param_dict['sample'     ] = '19'
        param_dict['dv'         ] = 1.0
        param_dict['type_am'    ] = 'mr'
        param_dict['sigma_clf_c'] = 0.1417

        return param_dict

## Prediction of group masses via ML - Calderon et al (2019)
class SDSSMLAnalysis(CatlUtils, DownloadManager):
    """
    Class used to handle the galaxy/group catalogues for the
    ``Calderon et al. (2019)`` analysis. This class has functions to read,
    modify, and analyze the galaxy/group catalogues for this analysis.

    The scripts and the rest of the codes for ``SDSS Conformity`` analysis
    can be found `here <https://github.com/vcalderon2009/SDSS_Conformity_Analysis>`_

    For a list of available pre-processed galaxy- and group-galaxy
    catalogues provided by ``sdss_catl_utils``, see ...
    """
    def __init__(self):
        """
        Examples
        ----------
        This class serves as the gateway for downloading and handling the
        catalogues used in the `Calderon et al. (2019) <https://arxiv.org/abs/1902.02680">`_
        analysis.

        One can easily *initialize* `SDSSMLAnalysis`:

        >>> from sdss_catl_utils.models.catl_models import SDSSMLAnalysis
        >>> catl_obj = SDSSMLAnalysis()

        One can also get the parameters used in the Conformity analysis:

        >>> catl_obj.param_dict # doctest: +SKIP

        The catalogues used for the analysis can be easily downloaded via the
        `~sdss_catl_utils.models.catl_models.DownloadManager.catl_download`
        method. If one wants to download the ``data`` catalogues, i.e.
        both ``memb`` and ``group`` catalogues, one can do it by:

        >>> catl_obj.catl_download(download_type='data') # doctest: +SKIP

        And if one wants to print out the paths of the URLs and output
        directories, one can do that by setting ``print_outdir = True``:

        >>> catl_obj.catl_download(download_type='data', print_outdir = True) # doctest: +SKIP

        Additionally, one could also `extract` the paths to the catalogues.
        For example, to recover the path to the ``data`` ``group`` catalogue,
        you could do that by:

        >>> catl_obj.catl_arr_extract(catl_kind='data', catl_type='group') # doctest: +SKIP

        This would return an array with the path(s) of the catalogues in question.
        """
        # Initializing dictionary
        self.init_params = self._initialize_params_dict()
        # Initializing classes
        CatlUtils.__init__(self, **self.init_params)
        DownloadManager.__init__(self, **self.init_params)
        # Metadata about the analysis
        self.publications  = ['arXiv:1902.02680']#, 'https://doi.org/10.1093/mnras/sty2000']
        self.github_url    = ['https://github.com/vcalderon2009/SDSS_Groups_ML']
        # self.analysis_docs = ['https://galactic-conformity-in-sdss-dr7.readthedocs.io']
    
    # Dictionary of input parameters
    def _initialize_params_dict(self):
        r"""
        Set the initial values of ``self.param_dict`` according to
        the SDSS Conformity analysis values.

        Returns
        ---------
        param_dict : `dict`
            Dictionary with the initial values of ``self.param_dict``
            for the ``SDSS Conformity (2019)`` analysis.
        """
        param_dict = {}
        param_dict['clf_method' ] = 1
        param_dict['clf_seed'   ] = 1235
        param_dict['halotype'   ] = 'so'
        param_dict['hod_n'      ] = 0
        param_dict['perf_opt'   ] = False
        param_dict['sample'     ] = '19'
        param_dict['dv'         ] = 1.0
        param_dict['type_am'    ] = 'mr'
        param_dict['sigma_clf_c'] = 0.1417

        return param_dict
