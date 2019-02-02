# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class HydraJobSelectionBox(Component):
    """A HydraJobSelectionBox component.
Component for displaying inputs for a Hydra Base
Job ID and Hydra Feature Job ID. Initial values are
based on URL params. Updates will be propagated through
a redirect. The `search` param is what should be provided
by the <Location /> dash core component.

Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- base (string; optional): The Base Hydra job ID
- feature (string; optional): The Feature Hydra job ID
- singleJob (boolean; optional): Whether only the feature job box will be shown"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, base=Component.UNDEFINED, feature=Component.UNDEFINED, singleJob=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'base', 'feature', 'singleJob']
        self._type = 'HydraJobSelectionBox'
        self._namespace = 'galileo_scope_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'base', 'feature', 'singleJob']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(HydraJobSelectionBox, self).__init__(**args)

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
            return ('HydraJobSelectionBox(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'HydraJobSelectionBox(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
