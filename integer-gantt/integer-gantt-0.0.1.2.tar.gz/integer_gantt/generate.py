import plotly as py
import plotly.figure_factory as pff
import plotly.io as pio


def gantt(data, x_title='Count', y_title='Task', fname='gantt_chart.png'):
    """Create a gantt chart and save it.

    Arguments:
        data {list of objects} -- The list of objects to place on the gantt chart. in the format [{"Task": "A"},{"Start": 0},{"Finish": 3}]

    Keyword Arguments:
        x_title {str} -- Title of the x_axis (default: {'Count'})
        y_title {str} -- Title of the y_axis (default: {'Task'})
        filename {str} -- Path to output the chart (default: {'gantt_chart'})
    """

    # Create the gantt chart
    fig = pff.create_gantt(data)

    # Add the titles and fix the ticks
    fig['layout']['xaxis'].update({'type': None, 'title': x_title})
    fig['layout']['yaxis'].update({'type': None, 'title': y_title})

    pio.write_image(fig, fname)
