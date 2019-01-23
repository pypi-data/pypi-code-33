import matplotlib.pyplot as plt


def _get_labels(l, hours, items):
    """
    Formats the labels, undocumented on purpose, not relevant.
    """
    total_sum = sum(l)

    it = 0
    temp_list = []
    for p in l:
        pct = (p / total_sum) * 100
        temp_list.append(f'{items[it]} - {hours[it]} ({round(pct, 2)}%)')
        it += 1
    return temp_list


class PieChart:
    """
    Matplotlib pie chart that comes with the library for the people that just want a quick
    insight of their data.

    Parameters
    ----------

    _dict : :class:`dict`
        The dictionary containing all the data that will be showed in the piechart.
    num : :class:`int`
        Number of max elements that will be shown in the chart
    dates : :class:`datetime.date`
        The dates if the data comes from a slice. Just for tagging purposes.

    Note
    ----
    You are suppose to access this by :meth:`.pie_chart`
    """
    def __init__(self, _dict, num: int, dates=None):
        self.dict = _dict
        self.fig = None

        items = list(self.dict.keys())
        data = list(map(lambda x: x / 3600, self.dict.values()))

        item1 = items[:num]
        data1 = data[:num]

        hours = list(map(lambda x: f'{round(x, 2)}h', data1))
        labels = _get_labels(data1, hours, item1)
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(aspect='equal'))
        wedges, texts = ax.pie(data1)

        ax.legend(wedges, labels,
                  title=f"|{dates[0].date} | {dates[1].date}|",
                  loc=2,
                  bbox_to_anchor=(1, 0)
                  )

    def show(self) -> None:
        """
        Shows the figure. :class:`matplotlib.pyplot.show`
        """
        self.fig = plt.gcf()
        plt.show()

    def save(self, fp: str) -> None:
        """
        Saves the figure in the given path. :class:`matplotlib.pyplot.save(fp)`

        :param fp:
            :class:`str`
        """
        fig = self.fig if self.fig else plt.gcf()
        fig.savefig(fp, bbox_inches='tight', format='png', dpi=100)

    def __repr__(self):
        return f"class <'{self.__class__.__name__}{self.dict}'>"
