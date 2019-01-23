#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from .Rect import Rect
from .Console import Console
from .ConsoleGraphics import ConsoleGraphics

# console buffer: cells with color ASCII string, text character and changed-flag; the buffer itself is without offset;

from .ConsoleBuffer import ConsoleBuffer

# console buffer: cells with color ASCII string, text character and changed-flag; the buffer itself has an offset value stored internall;

from .ConsoleBufferWO import ConsoleBufferWO

# simple version of ConsoleBuffer without changed flag

from .CharacterBuffer import CharacterBuffer

# int-based RGB values

from .IntRGB import IntRGB
from .ConsoleBufferRGB import ConsoleBufferRGB


