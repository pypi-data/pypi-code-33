from . import const


class Error(Exception):
    pass


class OUT_OF_OUTPUT_COUNT_BOUNDARY_ERROR(Error):
    def __str__(self):
        return "OUTPUT NUMBER IS MORE THAN " + (const.OUTPUT_COUNT-1).__str__()


class UNKNOWN_LANG_ERROR(Error):
    def __str__(self):
        return "UNKNOWN LANGUAGE"


class CONNECTION_ERROR(Error):
    def __init(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return "CONNECTION ERROR: STATUS CODE " + self.status_code.__str__()


class CANT_FIND_SUCH_EMOTION_ERROR(Error):
    def __str__(self):
        return "CAN'T FIND SUCH EMOTION"
