# coding: utf-8
##########################################################################
# NSAp - Copyright (C) CEA, 2019
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module contains the BIDS parser definition.
"""

# System import
import os
import pickle
import datetime

# Third party import
import pandas as pd
from grabbit import Layout

# Package import
from .parser_base import ParserBase


class BIDSParser(ParserBase):
    """ Object to retrieve data from a BIDS directory.
    """
    BASE_ENTITIES = ["subject", "session", "task", "run", "suffix"]
    EXT = ".pkl"

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
        return list([elem.replace("{0}.".format(name), "")
                     for elem in layout.entities.keys()])

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
        _key = "{0}.{1}".format(name, key)
        if _key not in layout.entities:
            raise ValueError("Unrecognize layout key '{0}'.".format(key))
        return list(layout.unique(_key))

    def filter_layout(self, name, extension=None, **kwargs):
        """ Filter the layout by using a combination of key-values rules.

        Parameters
        ----------
        name: str
            the name of the layout.
        extension: str or list of str
            a filtering rule on the file extension.
        kwargs: dict
            the filtering options.

        Returns
        -------
        df: pandas DataFrame
            the filtered layout.
        """
        layout = self._load_layout(name)
        if extension is not None:
            kwargs["extensions"] = extension
        header = None
        files = layout.get(**kwargs)
        if len(files) == 0:
            df = pd.DataFrame()
        else:
            file_obj = files[0]
            header = ["filename"]
            for key in self.list_keys(name):
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
        layout = Layout([(layout_root, self.conf[name])])
        self.layouts[name] = layout
        now = datetime.datetime.now()
        timestamp = "{0}-{1}-{2}".format(now.year, now.month, now.day)
        outfile = os.path.join(
            outdir, "{0}_{1}_{2}.pkl".format(self.project, name, timestamp))
        with open(outfile, "wb") as open_file:
            pickle.dump(layout, open_file, -1)
        return outfile
