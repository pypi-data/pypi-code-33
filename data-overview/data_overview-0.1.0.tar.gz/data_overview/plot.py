"""该类用于绘制直方图
"""
import base64
import matplotlib.pyplot as plt
try:
    from StringIO import BytesIO
except ImportError:
    from io import BytesIO

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


def _plot_histogram(series, var_type):
    """
    绘制直方图
    :param series: 数据
    :param var_type: 数据类型
    :return:
    """

    bins = 10  # 直方图条形的个数
    figsize = (6, 4)  # 直方图尺寸（宽，高）
    facecolor = '#337ab7'  # 直方图显示的颜色

    if var_type == 'date':
        # TODO: These calls should be merged
        fig = plt.figure(figsize=figsize)
        plot = fig.add_subplot(111)
        plot.set_ylabel('Frequency')
        try:
            plot.hist(series.dropna().values, facecolor=facecolor, bins=bins)
        except TypeError: # matplotlib 1.4 can't plot dates so will show empty plot instead
            pass
    else:
        plot = series.plot(kind='hist', figsize=figsize,
                           facecolor=facecolor,
                           bins=bins)  # TODO when running on server, send this off to a different thread
    return plot


def histogram(series, var_type):
    """
    对series数据绘制直方图
    :param series: 数据
    :param var_type: 该字段的数据类型
    :return: str
    """

    img_data = BytesIO()
    plot = _plot_histogram(series, var_type)
    plot.figure.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1, wspace=0, hspace=0)
    plot.figure.savefig(img_data)
    img_data.seek(0)
    result_string = 'data:image/png;base64,' + quote(base64.b64encode(img_data.getvalue()))
    # TODO Think about writing this to disk instead of caching them in strings
    plt.close(plot.figure)
    return result_string

