"""A lazy developer hasn't written a proper module docstring."""

from nose.plugins.base import Plugin
import logging
import os
import zipfile

logger = logging.getLogger("rhinoplasty.archives")


class CompressedTestLoaderPlugin(Plugin):
    """Nose plugin that loads tests from a compressed file
    (such as a zipfile).
    """
    
    # Standard Plugin attributes
    name = "load-zipfile"
    
    # Use default implementation of options() and configure to enable this plugin
    
    def help(self):
        return "Load tests from a zipfile or other compressed file."
    
    # Implementing IPluginInterface
    # -----------------------------
    def loadTestsFromFile(self, filename):
        #TODO Need to treat the entire zipfile namespace like a normal directory, and do all the hackery ourselves. ugh!
        return [False]
    
    def wantFile(self, filename):
        assert False, "This method doesnt seem to get called" #FIXME
        
        # Does the filename look like an archive?
        base, extension = os.path.splitext(filename)
        if not self._is_valid_extension(extension):
            return None
        
        # Is the file actually an archive
        if zipfile.is_zipfile(filename):
            return True
        
        # This is not an archive
        return None
    
    
    # Class Methods
    # -------------
    def _is_valid_extension(self, ext):
        """Is this filename extension a possible candidate for a compressed
        file supported by this plugin.
        """
        return ext in [
            #TODO make a class constant
            #TODO explain what each of these extensions are for (especially .bin)
            "bin",
            "zip",
        ]
    
