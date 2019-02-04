# coding: utf-8
##########################################################################
# NSAp - Copyright (C) CEA, 2019
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module contains the CubicWeb parser definition.
"""

# System import
import os

# Third party import
import numpy as np
import pandas as pd
from cwbrowser import CWInstanceConnection
from cwbrowser.utils import ask_credential

# Package import
from .parser_base import ParserBase


class CWParser(ParserBase):
    """ Object to retrieve data from a CubicWeb instance.
    """
    EXT = ".cw"

    def _get_connection(self, name):
        """ Create a connection object to CubicWeb instance.
        """
        if self.connection is None:
            url = self.conf[name]["url"]
            login, password = ask_credential()
            self.connection = CWInstanceConnection(
                url, login, password, verify=True,
                server_root="/home/{0}".format(login))
        return self.connection

    def _rset_as_data_frame(self, rset, header):
        """ Convert a CubicWeb rset to a pandas DataFrame.
        """
        if len(rset) > 0:
            return pd.DataFrame(data=np.asarray(rset), columns=header)
        else:
            return pd.DataFrame(columns=header)

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
        self._load_conf(name)
        connection = self._get_connection(name)
        selector = "Any X"
        header = ["filename"]
        for _alias, _cw_repr in self.conf[name]["attrs"].items():
            _name, _label = _cw_repr.split("-")
            selector += ", {0}".format(_label)
            header.append(_alias)
        rql = self.conf[name]["rql"].replace("Any X", selector)
        rset = connection.execute(rql)
        return self._rset_as_data_frame(rset, header)

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
        self._load_conf(name)
        return list(self.conf[name]["attrs"].keys())

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
        self._load_conf(name)
        connection = self._get_connection(name)
        if key not in self.conf[name]["attrs"]:
            raise ValueError("Unrecognize layout key '{0}'.".format(key))
        _name, _label = self.conf[name]["attrs"][key].split("-")
        selector = "DISTINCT Any {0}".format(_label)
        rql = self.conf[name]["rql"].replace("Any X", selector)
        rset = connection.execute(rql)
        return [elem[0] for elem in rset]

    def filter_layout(self, name, **kwargs):
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
        self._load_conf(name)
        connection = self._get_connection(name)
        selector = "Any X"
        header = ["filename"]
        rql = self.conf[name]["rql"]
        split_rql = rql.split(", ")
        key_rql = [elem.split(" ", 1)[1] for elem in split_rql]
        rql_suffix = []
        for _alias, _cw_repr in self.conf[name]["attrs"].items():
            _name, _label = _cw_repr.split("-")
            if _alias in kwargs:
                filtered_val = [
                    "'{0}'".format(elem) for elem in kwargs[_alias].split("|")]
                _key = "{0} {1}".format(_name, _label)
                _index = key_rql.index(_key)
                rql = rql.replace(
                    _key,
                    "{0} IN ({2})".format(
                        _name, _label, ",".join(filtered_val)))
                rql_suffix.append(split_rql[_index])
            selector += ", {0}".format(_label)
            header.append(_alias)
        rql = rql.replace("Any X", selector)
        if len(rql_suffix) > 0:
            rql = rql + ", " + ", ".join(rql_suffix)
        rset = connection.execute(rql)
        return self._rset_as_data_frame(rset, header)         
