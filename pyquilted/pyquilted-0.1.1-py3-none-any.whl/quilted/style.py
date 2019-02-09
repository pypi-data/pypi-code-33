class Style:
    def __init__(self, height="9in", width="6in", name_color=None,
                 font_main=None, font_other=None, font_size=None, **kwargs):
        self.page_height = height
        self.page_width = width
        self.name_color = name_color or "#0066cc"
        self.font_main = font_main or "verdana, arial, sans-serif"
        self.font_other = font_other or font_main \
            or "verdana, arial, sans-serif"
        self.font_size = font_size or "10pt"
