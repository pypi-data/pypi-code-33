import re

"""
This module encapsulates information about an image's resolution.
"""


class ImageResolution:
    """
    This class encapsulates information about an image's resolution.

    :member xres:  X resolution in pixels.  Integer value.
    :member yres:  Y resolution in pixels.  Integer value.
    """

    def __init__(self, xres, yres):
        """
         Constructor.

         Initializes this ImageResolution object.

         :param xres:
         :param yres:
         """

        if xres < 0 or yres < 0:
            raise ValueError('xres and/or yres cannot be negative!')
        self.xres = xres
        self.yres = yres

    @staticmethod
    def parse_image_resolution_string(image_resolution_string):
        """
         Given an image_resolution string, parse the xres and yres parts, and return them.

         :param image_resolution_string:  The image resolution in the format XRESxYRES,
                                          where XRES and YRES are positive integers.
         :returns xres, yres:  The xres and yres.  Both are integer values.
         """

        pattern = re.compile('[0-9]+')
        tokens = pattern.findall(image_resolution_string)

        if len(tokens) == 2:
            xres = int(tokens[0])
            yres = int(tokens[1])

            return xres, yres
        else:
            raise ValueError('invalid image_resolution_string format!  Expected <num>x<num>')

    def equals(self, other):
        """
         Equality operator.
         :param other:  Another ImageResolution object to compare against.  ImageResolution value.
         :return:  True if the ImageResolution objects are equal, false otherwise.  Boolean value.
         """

        return self.xres == other.xres and self.yres == other.yres

    def to_string(self):
        """
         Serialize this ImageResolution object to a string suitable for output to screen or file.
         :return: A string representing this ImageResolution object's contents.  String value.
         """

        return str(self.xres) + 'x' + str(self.yres)
