import os
import platform

# Link to documentation
CMAX_DOCS_URL = "http://web.mit.edu/6.01/www/cmax_docs/cmax_docs.html"


# Icon and image data
LOGO_IMGDATA='''\
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
'''
ICON_IMGDATA='''\
R0lGODlhEAAQAMIHAAAAAAUFBRcXF1UrAO0cJJ+AAP/QsP///yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAcALAAAAAAQABAAAANJeKrQ/mA1QquN0+p2sr4SUEHO0hFNoa6R6awwF8J00aZ13AEsrz6Mx2DgAxgMLcaQ6LMhXUNj05bsMJFTW+jInVaNXKwAEIgkAAA7
'''
WARNING_IMGDATA='''\
R0lGODlhGAAZAKECAAAAAP/JDv///////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAMALAAAAAAYABkAAAJgnI8DkO231psw0rlCkLflzXTIp3GiAmhlKH4ue2VRalLyItzdDeQ07HjNVrbUilRLkEDLZEW1goKCRuiSqKyqrtORVgruGrigsImM+2LRETODHA0z1XLw7I7Pz1D6vqUAADs=
'''

# Color definitions
BLACK = '#000000'
BROWN = '#AB6533'
RED = '#FF0000'
ORANGE = '#FF7F00'
YELLOW = '#FFFF00'
GREEN = '#00FF00'
BLUE = '#0000FF'
VIOLET = '#FF00FF'
GRAY = '#7F7F7F'
WHITE = '#FFFFFF'
BODY = '#CFCFCF'
CYAN = '#00FFFF'

# Font definitions
DEFAULT_FONT = ('Helvetica', 9, 'normal')
BOLD_FONT = ('Helvetica', 9, 'bold')

# Constants for setting cursors
CURSOR_NORMAL = 0
CURSOR_SHIFT = 1
CURSOR_CTRL = 2

# Grid methods, for converting grid locations to pixel ones, etc
GRID_WIDTH = 12


# grid(i,j) returns the pixel coordinates (x,y) of grid location i,j
# 1,1 -> upper left; 63,20 -> lower right; see proto.jpg
def gridx(i): return GRID_WIDTH*(i+2)


def gridy(j): return GRID_WIDTH*(j+3)


def grid(i, j): return gridx(i), gridy(j)


# ijgrid(x,y) returns the grid location (i,j) with pixel coordinates x,y
def igrid(x): return x/GRID_WIDTH-2


def jgrid(y): return y/GRID_WIDTH-3


def ijgrid(x, y): return igrid(x), jgrid(y)


# pin(i,j) returns the pixel coordinates (x,y) of pin i,j
# 1 <= i <= 63; 1 <= j <= 10
def pin(i, j):
    if j > 5: j += 2
    return grid(i, j+4)


def bus(i, j): return grid(i, [0, 1, 2, 19, 20][j])


LABEL_ID = 999


# Get a unique label based on a prefix
def get_label(prefix):
    global LABEL_ID
    LABEL_ID += 1
    return prefix+str(LABEL_ID)[1:]

# Because right click bindings differ on Mac, these constants are for binding in a multi-platform way

if platform.system().lower() == 'darwin':
    _button_id = 2
    # Note that this will only work for click; there is no right-click motion in CMax yet
    RIGHT_CLICK = '<Double-Button-1>'
else:
    _button_id = 3
    RIGHT_CLICK = '<Button-3>'
RIGHT_MOTION = '<B%d-Motion>' % _button_id
RIGHT_RELEASED = '<ButtonRelease-%d>' % _button_id


# updated for Windows compatability
# hartz 17 october 2012
def directoryonly(filename):
    if os.path.isdir(filename):
        return filename
    else:
        return os.path.split(filename)[0]


# updated for Windows compatability
# hartz 17 october 2012
def filenameonly(filename):
    if os.path.isfile(filename):
        return os.path.split(filename)[-1]
    else:
        return ''
