'''
File containing function to find where each of the detector's parameters are 
used and return two dicts: one of utility functions and one of noise models,
each containing lists of the parameters used by each file. The dictionary of
noise models should take into account the parameters used by the utility 
functions that it makes use of.

This function must be called from *outside* the 'noise' or 'utils' folder so 
that it can tell how to treat the paths, as utilities may be used within noise
models.

MAGIC
@author: Isobel
'''
import magic
import os
from subprocess import check_output
from inspect import getsourcefile, getfile

# path: path under which to recursively search for uses
# parameters: dictionary of parameters to search for
def findParameterUses(parameters):
    path = os.path.dirname(magic.__file__)
    files = _overrideCheckOutput("grep -rlF ' ' " + path)
    # We now have a list of paths to possibly useful files.
    # Now check whether they're in a folder, or have a name, that indicates
    # that they're useful.
    try:
       noise_paths = [f for f in files if 'noise/' in f]
       utils_paths = [f for f in files if 'utils/' in f]
    except:
       noise_paths = [];
       utils_paths = [];

    # We need to account for the fact that detectors may overwrite existing noise
    # classes with their own noise with the same name.
    # Check whether noise comes from magic/ifo/noise, and if not, flag this
    # element in the dictionary as being new.

    noise_map = {
        p.split('noise/')[-1].split('/')[-1].replace('.py', ''): p
        for p in noise_paths
        if 'ifo/noise' in p
    }
    new_noise_map = {
        '--new ' + p.split('noise/')[-1].split('/')[-1].replace('.py', ''): p
        for p in noise_paths
        if 'ifo/noise' not in p
    }
    noise_map.update(new_noise_map)
    noise_parameters = {k: [] for k in noise_map.keys()}

    # We need to account for the fact that detectors may overwrite existing
    # utility functions with their own utility function with the same name.
    # Check whether utility comes from magic/ifo/utils, and if not, flag
    # this element in the dictionary as being new.

    utils_map = {
        p.split('utils/')[-1].split('/')[-1].replace('.py', ''): p
        for p in utils_paths
        if 'ifo/utils' in p
    }
    new_utils_map = {
        '--new ' + p.split('utils/')[-1].split('/')[-1].replace('.py', ''): p
        for p in utils_paths
        if 'ifo/utils' not in p
    }
    utils_map.update(new_utils_map)
    utils_parameters = {k: [] for k in utils_map.keys()}

    # Check for instances of parameter usage in files
    for key in parameters.keys():
        _updateUsage(key, path, utils_parameters, utils_map)
        _updateUsage(key, path, noise_parameters, noise_map)

    # Now need to check where utility functions are used to return correct lists
    for u in utils_parameters.keys():
        _updateUsage(u, path, utils_parameters, utils_map, True,
                     utils_parameters)
        _updateUsage(u, path, noise_parameters, noise_map, True,
                     utils_parameters)

    return noise_parameters, noise_map, utils_parameters, utils_map


# Search one class or function for parameters and return the parameters that it uses
def searchForParameters(obj, parameters):
    try:
        path = getsourcefile(obj)
    except:
        path = getfile(obj.__class__)

    file = open(path).read()
    used_params = [p for p in parameters.keys() if "[\'" + p + "\']" in file]
    return used_params


# Check where a parameter or function is used and update a dictionary of usage
# based on this, cross-referenced against a map of the path to all files.
# If the key corresponds to the name of a utility function (check_util=True)
# then the dictionary is updated with the parameters in that utility file.
def _updateUsage(key,
                 path,
                 dictionary,
                 key_map,
                 check_util=False,
                 util_dict={}):

    new = False
    if '--new ' in key:
        key = key.replace('--new ', '')
        new = True

    try:
        if check_util:
            grep_for_string = key
        else:
            grep_for_string = "\"[\'" + key + "\']\""
        places = _overrideCheckOutput(
            "grep -rlF " + grep_for_string + " " + path)
        places = [p for p in places if p in key_map.values()]
    except:
        places = []

    keys = [k for k in key_map.keys() if key_map[k] in places]

    if new:
        key = '--new ' + key

    if check_util:
        for k in keys:
            dictionary[k] += util_dict[key]
    else:
        for k in keys:
            dictionary[k].append(key)


# Exception handler
def _overrideCheckOutput(command):
    try:
        files = str(check_output(command, shell=True)).split(r'\n')
        # Remove pycaches
        files = [f for f in files if '__pycache__' not in f]
        # Remove compiled files
        files = [f for f in files if 'cpython-35.pyc' not in f]

        # Append full file paths from list
        precede = ''
        for i, f in enumerate(files):

            # Get rid of b
            if 'b\'./' in f:
                f = f.replace('b\'', '')
            # Add file paths together
            if ' :' in f:
                precede = f.replace(':', '/')
            else:
                files[i] = precede + f

        # Make sure the file ends in .py
        files = [f for f in files if '.py' in f]

        return files

    except Exception:
        return None

