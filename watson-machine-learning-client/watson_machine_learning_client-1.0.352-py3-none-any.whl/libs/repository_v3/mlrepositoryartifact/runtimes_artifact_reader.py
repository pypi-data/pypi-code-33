################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


import logging

from repository_v3.mlrepository.artifact_reader import ArtifactReader

logger = logging.getLogger('RuntimesArtifactReader')


class RuntimesArtifactReader(ArtifactReader):
    def __init__(self, runtimespec_path):
        self.runtimespec_path = runtimespec_path

    def read(self):
        return self._open_stream()

    # This is a no. op. for RuntimeYmlFileReader as we do not want to delete the
    # archive file.
    def close(self):
        pass

    def _open_stream(self):
        return open(self.runtimespec_path, 'rt')

