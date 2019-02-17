import os
from .file_utils import FileUtils
from .image_resolution import ImageResolution

"""
This module encapsulates specific details about an image.
"""


class ImageDetails:
    """
    This class encapsulates specific details about an image.

    :member file_name:  The file_name part of the file_path.
    :member new_file_name:  The final file_name.
    :member old_file_name:  The original, unmodified file_name.
    :member output_dir:  Which directory to write output to.
    :member image_format:  The file format that PIL detected.
    :member mode:  The image mode PIL detected.
    """
    def __init__(self, image, file_path, output_dir):
        """
         Constructor.

         Initialize this ImageDetails instance.

         :param image:  An PIL Image object.
         :param file_path:  The full file path to the image file.
         :param output_dir:  Which directory we should write output to.
         """
        self.file_name = FileUtils.get_file_name(file_path)
        self.new_file_name = FileUtils.get_file_name(file_path)
        self.old_file_path = FileUtils.get_file_dir(file_path)
        self.output_dir = output_dir
        self.image_format = image.format
        self.image_resolution = ImageResolution(image.size[0], image.size[1])
        self.mode = image.mode

    def get_full_old_path(self):
        """
         Returns the full file path of the original unmodified file.

         :returns:  The full file path of the original unmodified file.  String value.
         """
        return os.path.join(self.old_file_path, self.file_name)

    def get_full_new_path(self):
        """
         Returns the full file path of the original unmodified file.

         :returns:  The full file path of the original unmodified file.  String value.
         """
        return os.path.join(self.output_dir, self.new_file_name)

    def to_string(self):
        """
         Serialize this object into a string appropriate for output to screen or file.
         :return:  Object's contents converted to string fromat.  String value.
         """
        return '    file_name: ' + self.file_name + '\n'\
               + '    new_file_name: ' + self.new_file_name + '\n'\
               + '    old_file_path: ' + self.get_full_old_path() + '\n'\
               + '    new_file_path: ' + self.get_full_new_path() + '\n'\
               + '    format: ' + self.image_format + '\n'\
               + '    size: ' + self.image_resolution.to_string() + '\n'\
               + '    mode: ' + self.mode + '\n'
