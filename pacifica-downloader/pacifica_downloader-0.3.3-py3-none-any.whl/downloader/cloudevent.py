#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Cloud Event Parser."""


# pylint: disable=too-few-public-methods
class CloudEvent(object):
    """Cloud Event Parser."""

    @staticmethod
    def yield_files(cloudevent):
        """
        Returned a method for yield files.

        The cloud event passed contains a 'data' key that is a flat
        list of metadata objects. Some of those objects are destined
        for the 'Files' table.
        """
        def ce_yield_files():
            """yield files from a cloudevent object."""
            for obj in cloudevent.get('data', []):
                if obj.get('destinationTable', False) == 'Files':
                    yield {
                        'id': obj.get('_id', False),
                        'path': '{}/{}'.format(obj.get('subdir', ''), obj.get('name', False)),
                        'hashsum': obj.get('hashsum', False),
                        'hashtype': obj.get('hashtype', False)
                    }
        return ce_yield_files
# pylint: enable=too-few-public-methods
