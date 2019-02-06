from netCDF4 import Dataset
import os

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


    return dst
