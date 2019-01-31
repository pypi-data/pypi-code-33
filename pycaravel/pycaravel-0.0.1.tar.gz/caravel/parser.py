# coding: utf-8
##########################################################################
# NSAp - Copyright (C) CEA, 2019
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
import glob
import pickle
import datetime

# Third party import
import pandas as pd
from grabbit import Layout

# Package import
from .io import load

# Define global parameters
BASE_ENTITIES = ["subject", "session", "task", "run", "suffix"]


class Caravel(object):
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
        _conf = self._get_conf()
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
            self.representation = {}

    def _check_layout(self, name):
        """ Check if the layout name is supported.
        """
        if name not in self.AVAILABLE_LAYOUTS:
            raise ValueError(
                "Layout '{0}' is not yet supported. Available layouts are: "
                "{1}.".format(name, AVAILABLE_LAYOUTS))

    def _get_layout(self, name, layoutdir=None):
        """ Get a layout: chack if already loaded or try to load it from
        the latest representation. If not found,raise an error.
        """
        layout = self.layouts.get(name, None)
        if layout is None:
            if layoutdir is None:
                raise ValueError(
                    "Impossible to load layout '{0}', please specify a layout "
                    "directory.".format(name))

    def _get_conf(self):
        """ List all the configurations available and sort them by project.
        """
        confdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "conf")
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
        for path in glob.glob(os.path.join(layoutdir, "*.pkl")):
            basename = os.path.basename(path).replace(".pkl", "")
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
        """ Load a loayout from its pre-generated represnetation.
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
        layout = self._load_layout(name)
        return layout.as_data_frame()

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
        layout = self._load_layout(name)
        return list(layout.entities.keys())

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
        layout = self._load_layout(name)
        if key not in layout.entities:
            raise ValueError("Unrecognize layout key '{0}'.".format(key))
        return list(layout.unique(key))

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
        layout = self._load_layout(name)
        if extensions is not None:
            kwargs["extensions"] = extensions
        header = None
        files = layout.get(**kwargs)
        if len(files) == 0:
            df = pd.DataFrame()
        else:
            file_obj = files[0]
            header = ["filename"]
            for key in layout.entities:
                if hasattr(file_obj, key):
                    header.append(key)
            data = []
            for file_obj in files:
                row = []
                for key in header:
                    row.append(getattr(file_obj, key))
                data.append(row)
            df = pd.DataFrame(data, columns=header)
        return df           

    def load_data(self, name, df):
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

        Returns
        -------
        data: dict
            a dictionaray containing the loaded data.
        """
        if "filename" not in df:
            raise ValueError("One 'filename' column expected in your table.")
        layout = self._load_layout(name)
        data = {}
        for path in df["filename"]:
            try:
                _data = load(path)
            except:
                _data = None
            if isinstance(_data, pd.DataFrame):
                file_obj = layout.files[path]
                for ent_name, ent_val in file_obj.entities.items():
                    if ent_name in BASE_ENTITIES:
                        _data[ent_name] = ent_val
                _data["dtype"] = name
                if "participant_id" in _data:
                    _data["participant_id"] = _data["participant_id"].str.replace(
                        "sub-", "")
            data[path] = _data
        return data

    def pickling_layout(self, bids_root, name, outdir):
        """ Load the requested BIDS layout and save it as a pickle.

        Parameters
        ----------
        bids_root: str
            path to the BIDS folder.
        name: str
            the name of subfolder to be parsed (the layout name).
        outdir: str
            the folder where the pickle will be generated.

        Returns
        -------
        outfile: str
            the generated layout representation location.
        """
        self._check_layout(name)
        self._check_conf(name)
        layout_root = os.path.join(bids_root, name)
        if not os.path.isdir(layout_root):
            raise ValueError("'{0}' is not a valid directory.")
        layout = Layout(layout_root, self.conf[name])
        self.layouts[name] = layout
        now = datetime.datetime.now()
        timestamp = "{0}-{1}-{2}".format(now.year, now.month, now.day)
        outfile = os.path.join(
            outdir, "{0}_{1}_{2}.pkl".format(self.project, name, timestamp))
        with open(outfile, "wb") as open_file:
            pickle.dump(layout, open_file, -1)
        return outfile

