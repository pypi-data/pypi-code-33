# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class CustomStylesheet(Component):
    """A CustomStylesheet component.
CustomStylesheet

Accepts arbitrary CSS rules and renders them.

Keyword arguments:
- id (string; optional): The ID for the component
- css (string; optional): The CSS composing the stylesheet"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, css=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'css']
        self._type = 'CustomStylesheet'
        self._namespace = 'galileo_scope_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'css']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(CustomStylesheet, self).__init__(**args)

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
            return ('CustomStylesheet(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'CustomStylesheet(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
