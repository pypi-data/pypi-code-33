import abc
import numpy as np
from pydnameth.config.setup.types import Method
from pydnameth.config.setup.types import get_main_metric
import plotly.graph_objs as go


class ReleaseStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def release_base(self, config):
        pass

    @abc.abstractmethod
    def release_advanced(self, config, configs_primary):
        pass

    @abc.abstractmethod
    def release_plot(self, config, configs_primary):
        pass


class TableReleaseStrategy(ReleaseStrategy):

    def release_base(self, config):
        (key, direction) = get_main_metric(config.setup)

        order = list(np.argsort(config.metrics[key]))
        if direction == 'descending':
            order.reverse()

        for key, value in config.metrics.items():
            config.metrics[key] = list(np.array(value)[order])

    def release_advanced(self, config, configs_primary):
        self.release_base(config)

    def release_plot(self, config, configs_primary):
        pass


class ClockReleaseStrategy(ReleaseStrategy):

    def release_base(self, config):
        pass

    def release_advanced(self, config, configs_primary):
        pass

    def release_plot(self, config, configs_primary):
        pass


class MethylationReleaseStrategy(ReleaseStrategy):

    def release_base(self, config):
        pass

    def release_advanced(self, config, configs_primary):
        pass

    def release_plot(self, config, configs_primary):

        if config.setup.method == Method.scatter:

            item = config.setup.params['item']
            aux = config.cpg_gene_dict[item]
            if isinstance(aux, list):
                aux_str = ';'.join(aux)
            else:
                aux_str = str(aux)

            layout = go.Layout(
                title=item + '(' + aux_str + ')',
                autosize=True,
                barmode='overlay',
                legend=dict(
                    font=dict(
                        family='sans-serif',
                        size=16,
                    ),
                    orientation="h",
                    x=0,
                    y=1.15,
                ),
                xaxis=dict(
                    title=config.attributes.target,
                    showgrid=True,
                    showline=True,
                    mirror='ticks',
                    titlefont=dict(
                        family='Arial, sans-serif',
                        size=24,
                        color='black'
                    ),
                    showticklabels=True,
                    tickangle=0,
                    tickfont=dict(
                        family='Old Standard TT, serif',
                        size=20,
                        color='black'
                    ),
                    exponentformat='e',
                    showexponent='all'
                ),
                yaxis=dict(
                    title='$\\beta$',
                    showgrid=True,
                    showline=True,
                    mirror='ticks',
                    titlefont=dict(
                        family='Arial, sans-serif',
                        size=24,
                        color='black'
                    ),
                    showticklabels=True,
                    tickangle=0,
                    tickfont=dict(
                        family='Old Standard TT, serif',
                        size=20,
                        color='black'
                    ),
                    exponentformat='e',
                    showexponent='all'
                ),

            )
            config.plot_data['fig'] = go.Figure(data=config.plot_data['data'], layout=layout)


class ObservablesReleaseStrategy(ReleaseStrategy):

    def release_base(self, config):
        pass

    def release_advanced(self, config, configs_primary):
        pass

    def release_plot(self, config, configs_primary):

        if config.setup.method == Method.histogram:
            layout = go.Layout(
                autosize=True,
                barmode='overlay',
                legend=dict(
                    font=dict(
                        family='sans-serif',
                        size=16,
                    ),
                    orientation="h",
                    x=0,
                    y=1.15,
                ),
                xaxis=dict(
                    title=config.attributes.target,
                    showgrid=True,
                    showline=True,
                    mirror='ticks',
                    titlefont=dict(
                        family='Arial, sans-serif',
                        size=24,
                        color='black'
                    ),
                    showticklabels=True,
                    tickangle=0,
                    tickfont=dict(
                        family='Old Standard TT, serif',
                        size=20,
                        color='black'
                    ),
                    exponentformat='e',
                    showexponent='all'
                ),
                yaxis=dict(
                    title='count',
                    showgrid=True,
                    showline=True,
                    mirror='ticks',
                    titlefont=dict(
                        family='Arial, sans-serif',
                        size=24,
                        color='black'
                    ),
                    showticklabels=True,
                    tickangle=0,
                    tickfont=dict(
                        family='Old Standard TT, serif',
                        size=20,
                        color='black'
                    ),
                    exponentformat='e',
                    showexponent='all'
                ),

            )
            config.plot_data['fig'] = go.Figure(data=config.plot_data['data'], layout=layout)
