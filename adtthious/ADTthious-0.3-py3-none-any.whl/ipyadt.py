# encoding utf-8

import ipywidgets as widgets
from . import basictypes

def select_widget(obj, attr):
    val = getattr(obj, attr)
    
    # On récupère le type de l'attribut et pas seulement de la valeur
    try:
        valtype = getattr(type(obj), attr).type
    except AttributeError:
        valtype = type(getattr(obj, attr))

    if valtype is bool:
        widget = widgets.Checkbox(value=val, 
                                  description=attr, 
                                  disabled=False)
    elif valtype is int:
        widget = widgets.IntText(value=val, 
                                 description=attr, 
                                 disabled=False)
        
    elif valtype is float:
        widget = widgets.FloatText(value=val, 
                                   description=attr, 
                                   disabled=False)
    elif valtype is str:
        widget = widgets.Text(value=val, 
                              description=attr, 
                              disabled=False,
                              placeholder='')
    
    elif isinstance(val, basictypes.Enum):
        widget = widgets.Dropdown(value=val.name,
                                  options=list(type(val).__members__.keys()), 
                                  description=attr, 
                                  disabled=False)
    elif isinstance(val, basictypes.date):
        widget = widgets.DatePicker(value=val,
                                    description=attr,
                                    disabled=False)
    elif isinstance(val, basictypes.time):
        widget = widgets.Text(value=val.strftime("%H:%M:%S"), 
                              description=attr, 
                              disabled=False,
                              placeholder='hh:mm:ss')
    elif isinstance(val, basictypes.datetime):
        widget = widgets.HBox((
            widgets.Label(value=attr),
            widgets.DatePicker(value=val),
            widgets.Text(value=val.strftime("%H:%M:%S"), 
                         placeholder='hh:mm:ss')
        ))

    else:
        widget = None

    return widget

def objatt2widget(obj, attr, widget_selector=select_widget):
    def on_value_change(change):
        newval = change['new']
        oldval = getattr(obj, attr)
        print(oldval, newval)
        if isinstance(oldval, basictypes.Enum):
            newval = type(oldval).__members__[newval]
        if oldval != newval:
            if isinstance(oldval, basictypes.datetime) \
            and isinstance(newval, basictypes.date):
                newval = basictypes.datetime(newval.year, newval.month, newval.day)
            setattr(obj, attr, newval)
            
    widget = widget_selector(obj, attr)
    if widget is None:
        widget = widgets.Text(value="Unknown widget for type '%s' for '%s'" % (type(val), val),
                              description=attr, 
                              disabled=True)
    
    widget.observe(on_value_change, names='value')
    return widget


