

########################################################################
class Write:
    """"""
    # ----------------------------------------------------------------------

    def __init__(self, buffer, font):
        """Constructor"""

        self.buffer = buffer
        self.font = font

    # ----------------------------------------------------------------------
    def text(self, string, x0=0, y0=0, color=0xffff, bgcolor=0, colors=None):
        """"""

        buffer = self.buffer
        font = self.font

        if colors is None:
            colors = (color, color, bgcolor, bgcolor)

        x = x0
        for c in string:

            if not c in font.keys():
                c = "?"

            row = y0
            _w, * _font = font[c]
            for byte in _font:
                unsalted = byte
                for col in range(x, x + _w):
                    color = colors[unsalted & 0x03]
                    if color is not None:
                        buffer.pixel(col, row, color)
                    unsalted >>= 2
                row += 1
            x += _w
