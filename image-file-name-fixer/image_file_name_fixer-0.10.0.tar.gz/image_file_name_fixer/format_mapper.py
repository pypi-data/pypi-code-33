

# TODO: We are not using this class.  We might need it for a feature later on.
# The purpose of this class is to take a format string, and map it to a format extension.
# TODO: What other formats should be supported?  XCF?  Photoshop files? etc.
#       For now, we'll just support these four formats, and add on an as-needed basis.
class FormatMapper:
    def __init__(self):
        self.map = dict()

    def setup_map(self):
        self.map['JPEG'] = '.jpg'
        self.map['GIF'] = '.gif'
        self.map['PNG'] = '.png'
        self.map['TIFF'] = '.tif'

    def map_format(self, image_format):
        if image_format in self.map:
            return self.map[image_format]
        else:
            raise ValueError('That format was not recognized')
