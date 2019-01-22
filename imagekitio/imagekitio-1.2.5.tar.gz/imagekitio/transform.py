''' This module generate, reorder and return traformation string '''

PARAMS = {
    "height": "h",
    "width": "w",
    "quality": "q",
    "crop": "c",
    "crop_mode": "cm",
    "focus": "fo",
    "format": "f",
    "rounded_corner": "r",
    "border": "b",
    "rotation": "rt",
    "blur": "bl",
    "named": "n",
    "overlay_image": "oi",
    "overlay_x": "ox",
    "overlay_y": "oy",
    "overlay_focus": "ofo",
    "background": "bg",
    "progressive": "pr",
    "color_profile": "cp",
    "metadata": "md"
}

INT_LIST = ["h", "w", "q", "r", "rt", "bl", "ox", "oy"]


class Transform(object):
    ''' Transform class '''
    def __init__(self, raw):
        self.options = raw
        self.parsed = self.valid_transforms()

    def valid_transforms(self):
        ''' validating and creating transformations '''
        _tparsed = []

        for data in self.options:
            _option = data
            _parsed = []
            for param, option in _option.items():
                # for key, value in PARAMS.items():
                #    if param in key:
                if param in PARAMS:
                    code = PARAMS[param]
                    if code in INT_LIST:
                        _parsed.append(code+"-"+str(int(option)))
                    else:
                        _parsed.append(code+"-"+str(option))

            transformation = ",".join(sorted(_parsed))
            _tparsed.append(transformation)

        return ':'.join(_tparsed)
