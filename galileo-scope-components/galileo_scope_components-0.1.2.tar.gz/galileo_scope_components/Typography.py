# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Typography(Component):
    """A Typography component.
Typography

See http://pages.github.robot.car/cruise/robot-styles for typography properties.

Keyword arguments:
- children (a list of or a singular dash component, string or number; optional): The children nodes for the layout
- color (string; optional): The color for the text
- fontFamily (string; optional): The font-family to use. Preferably a Cruise supported font like `sans` or `mono`.
- fontSize (number; optional): The font-size, based on the theme fontSizes. See http://pages.github.robot.car/cruise/robot-styles
- fontStyle (string; optional): The font-style to use. (eg. italic)
- fontWeight (number; optional): The font-weight of the text
- textAlign (string; optional): The text alignment
- width (number; optional): The width of the element
- m (optional): Margin on top, left, bottom and right
- mt (optional): Margin for the top
- mr (optional): Margin for the right
- mb (optional): Margin for the bottom
- ml (optional): Margin for the left
- mx (optional): Margin for the left and right
- my (optional): Margin for the top and bottom
- p (optional): Padding on top, left, bottom and right
- pt (optional): Padding for the top
- pr (optional): Padding for the right
- pb (optional): Padding for the bottom
- pl (optional): Padding for the left
- px (optional): Padding for the left and right
- py (optional): Padding for the top and bottom"""
    @_explicitize_args
    def __init__(self, children=None, color=Component.UNDEFINED, fontFamily=Component.UNDEFINED, fontSize=Component.UNDEFINED, fontStyle=Component.UNDEFINED, fontWeight=Component.UNDEFINED, textAlign=Component.UNDEFINED, width=Component.UNDEFINED, m=Component.UNDEFINED, mt=Component.UNDEFINED, mr=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mx=Component.UNDEFINED, my=Component.UNDEFINED, p=Component.UNDEFINED, pt=Component.UNDEFINED, pr=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, px=Component.UNDEFINED, py=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'color', 'fontFamily', 'fontSize', 'fontStyle', 'fontWeight', 'textAlign', 'width', 'm', 'mt', 'mr', 'mb', 'ml', 'mx', 'my', 'p', 'pt', 'pr', 'pb', 'pl', 'px', 'py']
        self._type = 'Typography'
        self._namespace = 'galileo_scope_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'color', 'fontFamily', 'fontSize', 'fontStyle', 'fontWeight', 'textAlign', 'width', 'm', 'mt', 'mr', 'mb', 'ml', 'mx', 'my', 'p', 'pt', 'pr', 'pb', 'pl', 'px', 'py']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Typography, self).__init__(children=children, **args)

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('Typography(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'Typography(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
