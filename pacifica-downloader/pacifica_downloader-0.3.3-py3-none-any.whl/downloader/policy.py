#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Policy Parser."""


# pylint: disable=too-few-public-methods
class TransactionInfo(object):
    """Cloud Event Parser."""

    @staticmethod
    def yield_files(transinfo):
        """
        Return a method for yield files.

        The files are part of a 'files' key that contains a
        dictionary that is keyed off the files ID.
        """
        def ce_yield_files():
            """yield files from a cloudevent object."""
            for file_id, file_obj in transinfo.get('files', {}).items():
                yield {
                    'id': file_id,
                    'path': '{}/{}'.format(
                        file_obj.get('subdir', ''),
                        file_obj.get('name', False)
                    ),
                    'hashsum': file_obj.get('hashsum', False),
                    'hashtype': file_obj.get('hashtype', False)
                }
        return ce_yield_files
# pylint: enable=too-few-public-methods
