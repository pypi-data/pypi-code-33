import abc
import numpy as np
from pydnameth.config.experiment.types import Method
from pydnameth.config.experiment.types import get_main_metric
import plotly.graph_objs as go
from statsmodels.stats.multitest import multipletests


class ReleaseStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def release(self, config, configs_child):
        pass


class TableReleaseStrategy(ReleaseStrategy):

    def release(self, config, configs_child):
        if config.experiment.method == Method.z_test_linreg:
            reject, pvals_corr, alphacSidak, alphacBonf = multipletests(config.metrics['p_value'], 0.05, method='fdr_bh')
            config.metrics['p_value'] = pvals_corr

        (key, direction) = get_main_metric(config.experiment)
        
        order = list(np.argsort(config.metrics[key]))
        if direction == 'descending':
            order.reverse()

        for key, value in config.metrics.items():
            config.metrics[key] = list(np.array(value)[order])

class ClockReleaseStrategy(ReleaseStrategy):

    def release(self, config, configs_child):
        pass


class MethylationReleaseStrategy(ReleaseStrategy):

    def release(self, config, configs_child):

        if config.experiment.method == Method.scatter:

            item = config.experiment.params['item']
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

            if 'x_range' in config.experiment.params:
                if config.experiment.params['x_range'] != 'auto':
                    layout.xaxis.range = config.experiment.params['x_range']

            config.experiment_data['fig'] = go.Figure(data=config.experiment_data['data'], layout=layout)


class ObservablesReleaseStrategy(ReleaseStrategy):


    def release(self, config, configs_child):

        if config.experiment.method == Method.histogram:

            layout = go.Layout(
                autosize=True,
                barmode=config.experiment.params['barmode'],
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

            config.experiment_data['fig'] = go.Figure(data=config.experiment_data['data'], layout=layout)
