from enum import Enum
from pydnameth.setup.advanced.clock.clock import ClockExogType


class Experiment(Enum):
    base = 'base'
    advanced = 'advanced'
    plot = 'plot'

    def __str__(self):
        return str(self.value)


class Task(Enum):
    table = 'table'
    clock = 'clock'
    observables = 'observables'
    methylation = 'methylation'

    def __str__(self):
        return str(self.value)


class Method(Enum):
    linreg = 'linreg'
    variance_linreg = 'variance_linreg'
    cluster = 'cluster'
    histogram = 'histogram'
    scatter = 'scatter'
    polygon = 'polygon'

    def __str__(self):
        return str(self.value)


def get_metrics_keys(setup):
    metrics = []

    if setup.task is Task.table:

        if setup.method is Method.linreg:
            metrics = [
                'item',
                'aux',
                'R2',
                'intercept',
                'slope',
                'intercept_std',
                'slope_std',
                'intercept_p_value',
                'slope_p_value'
            ]
        elif setup.method is Method.variance_linreg:
            metrics = [
                'item',
                'aux',
                'R2',
                'intercept',
                'slope',
                'intercept_std',
                'slope_std',
                'intercept_p_value',
                'slope_p_value',
                'R2_var',
                'intercept_var',
                'slope_var',
                'intercept_std_var',
                'slope_std_var',
                'intercept_p_value_var',
                'slope_p_value_var'
            ]
        elif setup.method is Method.cluster:
            metrics = [
                'item',
                'aux',
                'number_of_clusters',
                'number_of_noise_points',
            ]
        elif setup.method is Method.polygon:
            metrics = [
                'item',
                'aux',
                'area_intersection_rel',
                'slope_intersection_rel',
                'max_abs_slope'
            ]

    elif setup.task is Task.clock:

        if setup.method is Method.linreg:
            metrics = [
                'item',
                'aux',
                'count',
                'R2',
                'r',
                'evs',
                'mae',
                'summary'
            ]

    return metrics


def get_main_metric(setup):
    metric = ()

    if setup.task is Task.table:

        if setup.method is Method.linreg:
            metric = ('R2', 'descending')
        elif setup.method is Method.variance_linreg:
            metric = ('R2_var', 'descending')
        elif setup.method is Method.cluster:
            metric = ('number_of_clusters', 'descending')
        elif setup.method is Method.polygon:
            metric = ('area_intersection_rel', 'ascending')

    return metric


def get_default_params(setup):
    params = {}

    if setup.task is Task.table:

        if setup.method is Method.cluster:
            params = {
                'eps': 0.2,
                'min_samples': 5
            }
        elif setup.method is Method.polygon:
            params = {
                'method_primary': Method.linreg,
            }

    elif setup.task is Task.clock:

        if setup.method is Method.linreg:
            params = {
                'type': ClockExogType.all.value,
                'part': 0.25,
                'exogs': 100,
                'combs': 100,
                'runs': 100,
            }

    elif setup.task is Task.observables:

        if setup.method is Method.scatter:
            params = {
                'item': 'cg01620164',
            }

    return params


__all__ = ['Experiment', 'Task', 'Method']
