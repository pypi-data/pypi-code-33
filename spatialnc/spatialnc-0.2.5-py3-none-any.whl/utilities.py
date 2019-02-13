from netCDF4 import Dataset
import os
import numpy as np


def strip_chars(edit_str, bad_chars='[(){}<>,"_]=\nns'):
    """
    Written to strip out unwanted chars from the proj strings received
    back from the URL for the EPSG requests.

    Args:
        edit_str: String containing unwanted chars
        bad_chars: String of chars to be removed

    Returns:
        result: The edit_str without any of the chars in bad_chars
    """

    result = ''.join([s for s in edit_str if s not in bad_chars])
    return result


def copy_nc(infile, outfile, exclude=None):
    """
    Copies a netcdf from one to another exactly.

    Args:
        infile: filename or netCDF4 dataset object you want to copy
        outfile: output filename
        exclude: variables to exclude

    Returns the output netcdf dataset object for modifying
    """

    if type(exclude) != list:
        exclude = [exclude]

    dst = Dataset(outfile, "w")

    # Allow for either object or filename to be passed
    if type(infile) == str:
        src = Dataset(infile)
    else:
        src = infile

    # copy global attributes all at once via dictionary
    dst.setncatts(src.__dict__)

    # copy dimensions
    for name, dimension in src.dimensions.items():
        dst.createDimension(
            name, (len(dimension) if not dimension.isunlimited() else None))

    # copy all file data except for the excluded
    for name, variable in src.variables.items():
        if name not in exclude:
            dst.createVariable(name, variable.datatype, variable.dimensions)

            if name != 'projection':
                dst[name][:] = src[name][:]
                # copy variable attributes all at once via dictionary
            dst[name].setncatts(src[name].__dict__)

            #dst[name].missing_value = "NaN"
    return dst


def mask_nc(unmasked_file, mask_file, output=None, exclude=[]):
    """
    Masks a all the variables in a netcdf exlcuding, time, projection, x, y.
    If output = none it will make the file named after the original filename

    Args:
        unmasked_file: Path to a netcdf dataset to that is to be masked
        mask_file: Path to a netcdf dataset containing a variable named mask
        output: filename to output the data
        exlcude: variables to exclude

    Returns:
        dst: dataset object that the new masked dataset was written
    """

    #Parse the option name
    if output is None:
        # Isolate the name of the input file and use it for netcdf
        out_fname = "masked_" + (os.path.split(unmasked_file)[-1]).split('.')[0] + '.nc'

    else:
        out_fname = output

    unmasked = Dataset(unmasked_file)
    mask_ds = Dataset(mask_file)
    mask = mask_ds.variables['mask'][:]

    mask = mask.astype(float)
    mask[mask == 0] = np.nan
    # Make a copy
    dst = copy_nc(unmasked_file, out_fname)

    for name, variable in unmasked.variables.items():
        dims = variable.dimensions

        if 'x' in dims and 'y' in dims:
            if 'time' in dims:
                # Mask all data in the time series
                for i,t in enumerate(unmasked.variables['time'][:]):
                    dst.variables[name][i,:] = unmasked.variables[name][i,:] * mask
            else:
                dst.variables[name][:] = unmasked.variables[name][:] * mask

    # Close out
    unmasked.close()
    mask_ds.close()

    return dst
