# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Histogram(Component):
    """A Histogram component.


Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- style (dict; optional): Defines CSS styles which will override styles previously set.
- className (string; optional): Often used with CSS to style elements with common properties.
- height (string | number; optional): The height of the chart.
- width (string | number; optional): The width of the chart.
- options (dict; optional): A dictionary of options for the chart
- data (list | dict; optional): The data for the chart
- diffdata (dict; optional): Some charts support passing `diffdata` for visualising a change over time
- mapsApiKey (string; optional): Google maps api key for use with GeoChart
- spreadSheetUrl (string; optional): URL to google sheet for pulling data
- spreadSheetQueryParameters (dict; optional): Query parameters for external spreadsheet
- formatters (list | dict; optional): Data formatting options.
- legend_toggle (optional): Allow legend to toggle inclusion of data in chart
- selection (dict; optional): Data associated to user selection for use in callbacks
- dataTable (dict; optional): DataTable object, can be combined with selection data for use in callbacks

Available events: """
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, height=Component.UNDEFINED, width=Component.UNDEFINED, options=Component.UNDEFINED, data=Component.UNDEFINED, diffdata=Component.UNDEFINED, mapsApiKey=Component.UNDEFINED, spreadSheetUrl=Component.UNDEFINED, spreadSheetQueryParameters=Component.UNDEFINED, formatters=Component.UNDEFINED, legend_toggle=Component.UNDEFINED, selection=Component.UNDEFINED, dataTable=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'style', 'className', 'height', 'width', 'options', 'data', 'diffdata', 'mapsApiKey', 'spreadSheetUrl', 'spreadSheetQueryParameters', 'formatters', 'legend_toggle', 'selection', 'dataTable']
        self._type = 'Histogram'
        self._namespace = 'dash_google_charts/_components'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['id', 'style', 'className', 'height', 'width', 'options', 'data', 'diffdata', 'mapsApiKey', 'spreadSheetUrl', 'spreadSheetQueryParameters', 'formatters', 'legend_toggle', 'selection', 'dataTable']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Histogram, self).__init__(**args)

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
            return ('Histogram(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'Histogram(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
