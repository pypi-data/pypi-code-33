# coding: utf-8
##########################################################################
# NSAp - Copyright (C) CEA, 2019
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module contains the generic parser definition.
"""

# System import
import os
import json
import glob
import pickle
import datetime

# Third party import
import pandas as pd

# Package import
from caravel.io import load
  

class ParserBase(object):
    """ Object to retrieve data from a BIDS directory or a CubicWeb instance.
    """
    AVAILABLE_LAYOUTS = ("sourcedata", "derivatives", "phenotype")

    def __init__(self, project, layoutdir):
        """ Initialize the Caravel class.

        Parameters
        ----------
        project: str
            the name of the project you are working on.
        layoutdir: str
            the location of the pre-generated parsing representations. If None
            switch to managers mode.
        """
        self.project = project
        self.layouts = {}
        _conf = ParserBase._get_conf()
        if project not in _conf:
            raise ValueError(
                "Unkown configuration for project '{0}'. Available projects "
                "are: {1}.".format(project, _conf.keys()))
        self.conf = _conf[project]
        if layoutdir is not None:
            _repr = self._get_repr(layoutdir)
            if project not in _repr:
                raise ValueError(
                    "Unkown representation for project '{0}'. Available "
                    "projects are: {1}.".format(project, _repr.keys()))
            self.representation = _repr[project]
        else:
            self.representation = {"manager": [{"path": "to_be_created.pkl"}]}
        self.connection = None

    def can_load(self):
        """ A method checking the dataset type.

        Returns
        -------
        out: bool
            True if the dataset can be loaded, False otherwise.
        """
        checks = [elem[-1]["path"] for elem in self.representation.values()]
        if len(checks) == 0:
            return False
        return all([elem.endswith(self.EXT) for elem in checks])
        
    def _check_layout(self, name):
        """ Check if the layout name is supported.
        """
        if name not in self.AVAILABLE_LAYOUTS:
            raise ValueError(
                "Layout '{0}' is not yet supported. Available layouts are: "
                "{1}.".format(name, AVAILABLE_LAYOUTS))

    @classmethod
    def _get_conf(cls):
        """ List all the configurations available and sort them by project.
        """
        confdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), os.pardir, "conf")
        conf = {}
        for path in glob.glob(os.path.join(confdir, "*.conf")):
            basename = os.path.basename(path).replace(".conf", "")
            project, name = basename.split("_")
            if project not in conf:
                conf[project] = {}
            conf[project][name] = path
        return conf

    def _get_repr(self, layoutdir):
        """ List all the layout representation available and sort them by
        dates.
        """
        representations = {}
        layout_files = glob.glob(os.path.join(layoutdir, "*.pkl"))
        layout_files += glob.glob(os.path.join(layoutdir, "*.cw"))
        for path in layout_files:
            basename = os.path.basename(path).replace(".pkl", "")
            basename = basename.replace(".cw", "")
            project, name, timestamp = basename.split("_")
            if project not in representations:
                representations[project] = {}
            representations[project].setdefault(name, []).append(
                {"date": timestamp, "path": path})
        for project, project_data in representations.items():
            for name, name_data in project_data.items():
                name_data.sort(key=lambda x: datetime.datetime.strptime(
                    x["date"], "%Y-%m-%d"))
        return representations        

    def _check_conf(self, name):
        """ Check if configuration is declared for the layout.
        """
        if name not in self.conf:
            raise ValueError(
                "No configuration available for layout '{0}'. Please contact "
                "the module developpers to add the support for your project.")

    def _load_layout(self, name):
        """ Load a layout from its pre-generated representation.
        """
        if name not in self.layouts:
            if name not in self.representation:
                raise ValueError(
                    "A pre-generated '{0}' layout for your project '{1}' is "
                    "expected in user mode. Please contact the developpers "
                    "of the module.".format(name, self.project))
            path = self.representation[name][-1]["path"]
            with open(path, "rb") as open_file:
                self.layouts[name] = pickle.load(open_file)
        return self.layouts[name]

    def _load_conf(self, name):
        """ Load the configuration associated to a layout.
        """
        if not isinstance(self.conf[name], dict):
            print(self.conf[name])
            with open(self.conf[name], "rt") as open_file:
                self.conf[name] = json.load(open_file)

    def export_layout(self, name):
        """ Export a layout as a pandas DataFrame.

        Parameters
        ----------
        name: str
            the name of the layout.

        Returns
        -------
        df: pandas DataFrame
            the converted layout.
        """
        raise NotImplementedError("This function has to be defined in child "
                                  "child class.")

    def list_keys(self, name):
        """ List all the filtering keys available in the layout.

        Parameters
        ----------
        name: str
            the name of the layout.

        Returns
        -------
        keys: list
            the layout keys.
        """
        raise NotImplementedError("This function has to be defined in child "
                                  "child class.")

    def list_values(self, name, key):
        """ List all the filtering key values available in the layout.

        Parameters
        ----------
        name: str
            the name of the layout.
        key: str
            the name of key in the layout.

        Returns
        -------
        values: list
            the key assocaited values in the layout.
        """
        raise NotImplementedError("This function has to be defined in child "
                                  "child class.")

    def filter_layout(self, name, extensions=None, **kwargs):
        """ Filter the layout by using a combination of key-values rules.

        Parameters
        ----------
        name: str
            the name of the layout.
        extensions: str or list of str
            a filtering rule on the file extension.
        kwargs: dict
            the filtering options.

        Returns
        -------
        df: pandas DataFrame
            the filtered layout.
        """
        raise NotImplementedError("This function has to be defined in child "
                                  "child class.")         

    def load_data(self, name, df, replace=None):
        """ Load the data contained in the filename column of a pandas
        DataFrame.

        Note:
        Only a couple of file extensions are supported. If no loader has been
        found None is returned.

        Parameters
        ----------
        name: str
            the name of the layout.
        df: pandas DataFrame
            a table with one 'filename' column.
        replace: 2-uplet, default None
            in the case of a CubicWeb resource, the data are downloaded in a
            custom folder. Use this parameter to replace the server location
            by your own location.

        Returns
        -------
        data: dict
            a dictionaray containing the loaded data.
        """
        if "filename" not in df:
            raise ValueError("One 'filename' column expected in your table.")
        data = {}
        for index, path in enumerate(df["filename"]):
            if isinstance(path, dict):
                _data = pd.DataFrame.from_records([path])
                path = ["{0}-{1}".format(key, val)
                        for key, val in zip(df.columns, df.values[index])
                        if key != "filename"]
                path = "_".join(path)
            else:
                if replace is not None:
                    path = path.replace(replace[0], replace[1])
                try:
                    _data = load(path)
                except:
                    _data = None
                if isinstance(_data, pd.DataFrame):
                    layout = self._load_layout(name)
                    file_obj = layout.files[path]
                    for ent_name, ent_val in file_obj.entities.items():
                        if ent_name in self.BASE_ENTITIES:
                            _data[ent_name] = ent_val
                    _data["dtype"] = name
                    if "participant_id" in _data:
                        _data["participant_id"] = _data[
                            "participant_id"].str.replace("sub-", "")
            data[path] = _data
        return data
