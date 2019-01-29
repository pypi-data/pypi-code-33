import plotly
import plotly.io as pio
from pydnameth.infrastucture.path import get_save_path


def save_figure(config, fig, prefix=''):
    if prefix == '':
        fn = get_save_path(config) + '/' + \
             config.setup.get_file_name()
    else:
        fn = get_save_path(config) + '/' + \
             prefix + '_' + config.setup.get_file_name()
    plotly.offline.plot(fig, filename=fn + '.html', auto_open=False)
    pio.write_image(fig, fn + '.png')
    pio.write_image(fig, fn + '.pdf')
