"""
A collection of image transforms.
"""

from manhattan.assets.transforms.base import BaseTransform

__all__ = [
    'Crop',
    'Face',
    'Fit',
    'Output',
    'Rotate',
    'SmartCrop'
    ]


class Crop(BaseTransform):
    """
    Apply a crop to an image.

    Each value (top, left, bottom, right) should be between 0.0 and 1.0
    representing a normalized value for the given dimension.
    """

    _id = 'image.crop'

    def __init__(self, top, left, bottom, right):
        super().__init__({
            'top': top,
            'left': left,
            'bottom': bottom,
            'right': right
            })


class Face(BaseTransform):
    """
    Detect and crop a face from within the image.
    """

    _id = 'image.face'

    def __init__(self, bias=None, padding=0, min_padding=0):
        super().__init__({
            'bias': bias,
            'padding': padding,
            'min_padding': min_padding
            })


class Fit(BaseTransform):
    """
    Resize an image to fit within a set of dimensions. The width and height
    should be specified in pixels.
    """

    _id = 'image.fit'

    def __init__(self, width, height=None):
        super().__init__({'width': width, 'height': height or width})


class Output(BaseTransform):
    """
    Set the output format of an image. The list of support formats will vary
    depending on service, however as a minimum the following formats should be
    supported by all services:

    - jpg (supports quality)
    - gif
    - png
    - webp (supports quality)
    """

    _id = 'image.output'

    def __init__(self, format, quality=None):
        settings = {'format': format}
        if quality is not None:
            settings['quality'] = quality

        super().__init__(settings)


class Rotate(BaseTransform):
    """
    Rotate an image by 90, 180 or 270 degrees.
    """

    _id = 'image.rotate'

    def __init__(self, angle):
        super().__init__({'angle': angle})


class SmartCrop(BaseTransform):
    """
    Cropping a region of the image matching the given aspect ratio (w / h)
    centered around a detected area of interest (based on the detection of a
    face or feature).
    """

    _id = 'image.smart_crop'

    def __init__(self, aspect_ratio):
        super().__init__({'aspect_ratio': aspect_ratio})