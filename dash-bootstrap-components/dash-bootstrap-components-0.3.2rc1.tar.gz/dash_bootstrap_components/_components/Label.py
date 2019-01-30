# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Label(Component):
    """A Label component.


Keyword arguments:
- children (a list of or a singular dash component, string or number; optional): The children of this component
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- style (dict; optional): Defines CSS styles which will override styles previously set.
- className (string; optional): Often used with CSS to style elements with common properties.
- hidden (boolean; optional): Hide label from UI, but allow it to be discovered by screen-readers.
- size (string; optional): Set size of label. Options 'sm', 'md' (default) or 'lg'.
- html_for (string; optional): Set the `for` attribute of the label to bind it to a particular element
- width (optional): Specify width of label for use in grid layouts. Accepts the same values
as the Col component.
- xs (optional): Specify label width on extra small screen
- sm (optional): Specify label width on a small screen
- md (optional): Specify label width on a medium screen
- lg (optional): Specify label width on a large screen
- xl (optional): Specify label width on an extra large screen
- align (a value equal to: 'start', 'center', 'end'; optional): Set vertical alignement of the label, default: `center`
- color (string; optional): Text color, options: primary, secondary, success, warning, danger, info,
muted, light, dark, body, white, black-50, white-50."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, hidden=Component.UNDEFINED, size=Component.UNDEFINED, html_for=Component.UNDEFINED, width=Component.UNDEFINED, xs=Component.UNDEFINED, sm=Component.UNDEFINED, md=Component.UNDEFINED, lg=Component.UNDEFINED, xl=Component.UNDEFINED, align=Component.UNDEFINED, color=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'style', 'className', 'hidden', 'size', 'html_for', 'width', 'xs', 'sm', 'md', 'lg', 'xl', 'align', 'color']
        self._type = 'Label'
        self._namespace = 'dash_bootstrap_components/_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'style', 'className', 'hidden', 'size', 'html_for', 'width', 'xs', 'sm', 'md', 'lg', 'xl', 'align', 'color']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Label, self).__init__(children=children, **args)

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
            return ('Label(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'Label(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
