from inicheck.checkers import GenericCheck
from .health_check import check_missing_vars, check_missing_file, check_min_file_size
import netCDF4 as nc
import os
import glob
from collections import OrderedDict

class MissingVarCheck(GenericCheck):
    def __init__(self, **kwargs):
        super(MissingVarCheck, self).__init__(**kwargs)

    def cast(self):
        return self.value

    def is_valid(self):
        # path to file with pattern
        pattern = self.config.cfg['output_check']['pattern']
        file = self.config.cfg['output_check']['file']
        vars = self.config.cfg['output_check']['netcdf_vars']
        # find files with missing variables and the missing variables
        self.incomplete = check_missing_vars(pattern, file, vars)

        # if we have errors, construct the message
        if len(self.incomplete) > 0:
            self.message=('Variables missing from netcdfs.\n'
                          '{}\n'.format('\n'.join(['{} --- {}'.format(k,v) for k,v in self.incomplete.items()])))
            return False, self.message
        else:
            return True, self.message


class MissingFileCheck(GenericCheck):
    def __init__(self, **kwargs):
        super(MissingFileCheck, self).__init__(**kwargs)

    def cast(self):
        return self.value

    def is_valid(self):
        # path to file with pattern
        pattern = self.config.cfg['output_check']['pattern']
        file = self.config.cfg['output_check']['file']
        # find files with missing variables and the missing variables
        self.incomplete = check_missing_file(pattern, file)

        if len(self.incomplete) > 0:
            self.message=('Files missing from pattern.\n'
                          '{}\n'.format('\n'.join(['{}'.format(k) for k in self.incomplete])))
            return False, self.message
        else:
            return True, self.message


class MinSizeCheck(GenericCheck):
    def __init__(self, **kwargs):
        super(MinSizeCheck, self).__init__(**kwargs)

    def cast(self):
        return self.value

    def is_valid(self):
        # path to file with pattern
        pattern = self.config.cfg['output_check']['pattern']
        file = self.config.cfg['output_check']['file']
        min_size = self.config.cfg['output_check']['min_size']
        # find files with missing variables and the missing variables
        self.incomplete = check_min_file_size(pattern, file, min_size=min_size)

        if len(self.incomplete) > 0:
            message = 'Files smaller than {} kB.\n'.format(min_size)
            message = message + '{}\n'.format('\n'.join(['{}'.format(k) for k in self.incomplete]))
            self.message = message
            return False, self.message
        else:
            return True, self.message
