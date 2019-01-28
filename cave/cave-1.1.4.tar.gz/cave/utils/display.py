def array_to_table(array, style='bokeh', colors=None):
    """ Turns given array into a table. This is an abstract method to easily toggle between bokeh-tables and normal
    HTML-tables.

    Parameters
    ----------
    colors: dict( str : dict( str : str ))
        legal keys are [columns, rows]
        for examples: {'columns' : {'apple': 'green', 'banana' : 'yellow'}, 'rows' : {'cost' : 'blue'}}
    """

    style = style.lower()
    if style == 'bokeh':
        get_bokeh_table
    elif style == 'html':
        get_html_table
    else:
        raise ValueError("%s not supported as an option in cave.utils.display.array_to_table." % style)
