# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class NavbarSimple(Component):
    """A NavbarSimple component.


Keyword arguments:
- children (a list of or a singular dash component, string or number; optional): The children of this component
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- style (dict; optional): Defines CSS styles which will override styles previously set.
- className (string; optional): Often used with CSS to style elements with common properties.
- brand (string; optional): Branding text, to go top left of the navbar
- brand_href (string; optional): Link to attach to brand
- brand_style (dict; optional): Style options for Brand
- brand_external_link (boolean; optional): If true, the browser will treat the brand link as external,
forcing a page refresh at the new location. If false,
this just changes the location without triggering a page
refresh. Use this if you are observing dcc.Location, for
instance. Defaults to true for absolute URLs and false
otherwise.
- fluid (boolean; optional): Allow menu items to expand to fill width of page
- light (boolean; optional): Apply light styling to the navbar
- dark (boolean; optional): Apply dark styling to the navbar
- fixed (string; optional): Fix the navbar's position at the top or bottom of the page, options: top, bottom
- sticky (string; optional): Stick the navbar to the top or the bottom of the viewport, options: top, bottom

With `sticky`, the navbar remains in the viewport when you scroll. By
contrast, with `fixed`, the navbar will remain at the top or bottom of
the page.
- color (string; optional): Sets the color of the NavbarSimple. Main options are primary, light and dark, default light.

You can also choose one of the other contextual classes provided by Bootstrap
(secondary, success, warning, danger, info, white) or any valid CSS color of
your choice (e.g. a hex code, a decimal code or a CSS color name)
- expand (boolean | string; optional): Specify screen size at which to expand the menu bar, e.g. sm, md, lg etc."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, brand=Component.UNDEFINED, brand_href=Component.UNDEFINED, brand_style=Component.UNDEFINED, brand_external_link=Component.UNDEFINED, fluid=Component.UNDEFINED, light=Component.UNDEFINED, dark=Component.UNDEFINED, fixed=Component.UNDEFINED, sticky=Component.UNDEFINED, color=Component.UNDEFINED, expand=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'style', 'className', 'brand', 'brand_href', 'brand_style', 'brand_external_link', 'fluid', 'light', 'dark', 'fixed', 'sticky', 'color', 'expand']
        self._type = 'NavbarSimple'
        self._namespace = 'dash_bootstrap_components/_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'style', 'className', 'brand', 'brand_href', 'brand_style', 'brand_external_link', 'fluid', 'light', 'dark', 'fixed', 'sticky', 'color', 'expand']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(NavbarSimple, self).__init__(children=children, **args)

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
            return ('NavbarSimple(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'NavbarSimple(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
