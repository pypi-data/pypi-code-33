# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class InfoBox(Component):
    """A InfoBox component.


Keyword arguments:
- change_value (number; optional)
- main_title (string; required)
- sub_title (string; required)
- value (string; required)
- id (string; optional)
- bottom_title (string; optional)

Available events: """
    @_explicitize_args
    def __init__(self, change_value=Component.UNDEFINED, main_title=Component.REQUIRED, sub_title=Component.REQUIRED, value=Component.REQUIRED, id=Component.UNDEFINED, bottom_title=Component.UNDEFINED, **kwargs):
        self._prop_names = ['change_value', 'bottom_title', 'sub_title', 'value', 'id', 'main_title']
        self._type = 'InfoBox'
        self._namespace = 'dash_custom_components'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['change_value', 'bottom_title', 'sub_title', 'value', 'id', 'main_title']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in [u'main_title', u'sub_title', u'value']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(InfoBox, self).__init__(**args)

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
            return ('InfoBox(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'InfoBox(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
