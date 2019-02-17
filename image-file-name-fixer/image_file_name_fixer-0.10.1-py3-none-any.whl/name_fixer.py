import os
import shutil
import re

from PIL import Image
from .image_details import ImageDetails
from .file_utils import FileUtils

"""
This module takes image file names, and modifies them to conform to our image file name
requirements.
"""


# Determine what the output_dir should be for the given file_path.
#
# If the user specifies an output_dir via argument, this is a fixed output_dir.
# If the user does not specify an output_dir argument, the default is to write output to the same directory as the
# input.
def get_output_dir(config, file_path, base):
    if config.get_output_dir() is not None:
        return FileUtils.process_raw_file_path(os.path.join(config.get_output_dir(), base))
    else:
        return FileUtils.get_file_dir(file_path)


def get_image_file_details(config, file_path, base):
    """
    Given a path to an input file, try to construct an ImageDetails object representing the details
    of that input image file.

    If the input file is not recognized by Pillow, do not bother processing this file, return None.

    If the input file is recognized by Pillow, extract details, construct an ImageDetails object.

    :param config:  The application configuration.  AppConfig value.
    :param file_path: The path name of the input file.  String value.
    :param base: The base directory to append to the output string.
    :returns image_details:  Details about the input image file.  Image Details value.
    """

    if os.path.exists(file_path):
        try:
            image = Image.open(file_path)
        except OSError as os_error:
            print('Caught OSError: {0}'.format(os_error))
            return None
        output_dir = get_output_dir(config, file_path, base)
        image_details = ImageDetails(image, file_path, output_dir)
        image.close()
        return image_details
    else:
        print(file_path + ' does not exist!')
        return None


def strip_image_resolution_fields(image_details):
    """
    Given an image_details object, strip out all image_resolution fields from the path, and return the modified
    image_details object.

    Note: Here we do care about the '-' char, we want to get rid of them here.

    :param image_details:  Details about the input image file.  Image Details value.
    :returns image_details:  Modified input_details object.  ImageDetails value.
    """
    pattern = re.compile('[-]?[0-9]+[xX][0-9]+[-]?')
    tokens = pattern.split(image_details.file_name)
    image_details.new_file_name = ''.join(tokens)
    return image_details


def append_image_resolution_field(image_details):
    """
    Given an image_details object add an image_resolution field to the path.
    Return the modified image_details object.

    :param image_details:  Details about the input image file.  Image Details value.
    :returns image_details:  Modified input image_details object.  ImageDetails value.
    """
    tokens = os.path.splitext(image_details.new_file_name)
    image_details.new_file_name = tokens[0] + '-' + image_details.image_resolution.to_string() + tokens[1]
    return image_details


def rename_file(image_details, should_move_file):
    """
    Given an image_details object, copy/move the file to it's new path.

    :param image_details:  Details about the input image file.  ImageDetails value.
    :param should_move_file:  Should we move the file instead of copying it?  Boolean value.
    :returns nothing:
    """
    FileUtils.create_output_dir(image_details.output_dir)
    if should_move_file:
        shutil.move(image_details.get_full_old_path(), image_details.get_full_new_path())
    else:
        if image_details.get_full_old_path() != image_details.get_full_new_path():
            shutil.copy2(image_details.get_full_old_path(), image_details.get_full_new_path())


# Given an image_detail object, give us the new file_path to write the file to.
def fix_file_name(image_details):
    """
    Given an image_detail object, fix the file name such that it conforms to our image file naming
    requirements.

    :param image_details:  Details about the input image file.  Image Details value.
    :returns image_details:  Modified input image_details object.  ImageDetails value.
    """
    image_details = strip_image_resolution_fields(image_details)
    image_details = append_image_resolution_field(image_details)

    return image_details


def process_file(config, file_path, base=''):
    image_details = get_image_file_details(config, file_path, base)
    if image_details is not None:
        final_result = fix_file_name(image_details)
        if not config.dry_run:
            rename_file(image_details, config.should_move_file)
        if config.verbose:
            print('Image details:\n' + final_result.to_string())
        print(image_details.get_full_old_path() + ' -> ' + image_details.get_full_new_path())

    else:
        print(file_path + ': Could not process this file.')


def process_directory(config, path, base=''):
    items = os.listdir(path)
    for item in items:
        file_path = os.path.join(path, item)
        if os.path.isfile(file_path):
            process_file(config, file_path, base)
        elif os.path.isdir(file_path):
            if config.recursive:
                process_directory(config, os.path.join(path, item), os.path.join(base, item))


def run(config):
    """
    Runs the name_fixer module.

    :param config:  Application configuration.  AppConfig value.
    :returns nothing:
    """
    # check config.version first, before doing anything else.
    if config.version:
        print('Version: 0.10.1')
        exit(0)
    # config.path is only required if config.version is not set.
    if config.get_paths() is None:
        raise ValueError('The input path is required!')
    for path in config.get_paths():
        path = FileUtils.process_raw_file_path(path)
        if os.path.exists(path):
            if os.path.isfile(path):
                process_file(config, path)
            elif os.path.isdir(path):
                process_directory(config, path)
            else:
                raise ValueError('Got something other than regular file or directory.  Bailing!')
        else:
            raise ValueError('The input path does not exist')
