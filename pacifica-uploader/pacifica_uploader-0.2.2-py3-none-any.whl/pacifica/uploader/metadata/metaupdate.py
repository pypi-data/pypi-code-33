#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Module used to update MetaData objects.

This module exports classes and methods for
constructing and executing the strategy for modifying the values, including the
parents and children, of instances of the `pacifica.uploader.metadata.MetaData` class.
"""
from __future__ import absolute_import
from .metadata import MetaData
from .policyquery import PolicyQuery


class MetaUpdate(MetaData):
    """
    Class to update the MetaData object.

    This class is a sub-class of the ``pacifica.uploader.metadata.MetaData``
    class that is specialized to issue and handle
    queries to `Pacifica Policy <https://github.com/pacifica/pacifica-policy>`_
    servers.
    """

    def __init__(self, user, *args, **kwargs):
        """Pull the user from the arguments so we can use that for policy queries."""
        self._auth = kwargs.pop('auth', {})
        super(MetaUpdate, self).__init__(*args, **kwargs)
        self._user = user

    def get_auth(self):
        """Return the auth object to be used by other instances."""
        return self._auth

    def query_results(self, meta_id):
        """
        Build a PolicyQuery out of the meta_id.

        This method creates a ``pacifica.uploader.metadata.PolicyQuery`` object
        that queries the policy server and returns the results.
        """
        where_clause = {}
        for column, dep_meta_id in self[meta_id].queryDependency.items():
            where_clause[column] = self[dep_meta_id].value
        pq_obj = PolicyQuery(
            user=self._user,
            columns=self[meta_id].queryFields,
            from_table=self[meta_id].sourceTable,
            where=where_clause,
            auth=self._auth
        )
        return pq_obj.get_results()

    def dependent_meta_id(self, meta_id):
        """Get the dependent meta ID."""
        meta = self[meta_id]
        ret = []
        for dep_meta_id in meta.queryDependency.values():
            if meta_id != dep_meta_id:
                ret.append(dep_meta_id)
        return ret

    def update_parents(self, meta_id):
        """Update the parents of the meta_id."""
        for dep_meta_id in self.dependent_meta_id(meta_id):
            self.update_parents(dep_meta_id)

        meta = self[meta_id]._replace(
            query_results=self.query_results(meta_id))
        self[meta_id] = meta

        if meta.query_results and not meta.value:
            meta = meta._replace(value=meta.query_results[0][meta.valueField])
            self[meta_id] = meta

    def directory_prefix(self):
        """Return the directory prefix of the MetaObjs which have directoryOrder."""
        dir_md_objs = []
        for md_obj in self:
            if md_obj.directoryOrder is not None:
                dir_md_objs.append(md_obj)
        dirs = []
        for md_obj in sorted(dir_md_objs, key=lambda x: x.directoryOrder):
            format_hash = md_obj.query_results[0]
            dirs.append(md_obj.displayFormat.format(**format_hash))
        return '/'.join(dirs)
