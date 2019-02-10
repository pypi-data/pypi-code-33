import abc
from pydnameth.config.experiment.types import Method
from pydnameth.config.experiment.types import get_metrics_keys
import statsmodels.api as sm
import numpy as np
from sklearn.cluster import DBSCAN
from pydnameth.routines.clock.types import ClockExogType, Clock
from pydnameth.routines.clock.linreg.processing import build_clock_linreg
import plotly.graph_objs as go
import colorlover as cl
from shapely import geometry
from scipy.stats import norm
from pydnameth.routines.common import is_float


class RunStrategy(metaclass=abc.ABCMeta):

    def __init__(self, get_strategy):
        self.get_strategy = get_strategy

    @abc.abstractmethod
    def single(self, item, config, configs_child):
        pass

    @abc.abstractmethod
    def iterate(self, config, configs_child):
        pass

    @abc.abstractmethod
    def run(self, config, configs_child):
        pass


class TableRunStrategy(RunStrategy):

    def single(self, item, config, configs_child):

        if config.experiment.method == Method.linreg:

            target = self.get_strategy.get_target(config)
            x = sm.add_constant(target)
            y = self.get_strategy.get_single_base(config, [item])[0]

            results = sm.OLS(y, x).fit()

            config.metrics['item'].append(item)
            aux = self.get_strategy.get_aux(config, item)
            config.metrics['aux'].append(aux)
            config.metrics['R2'].append(results.rsquared)
            config.metrics['intercept'].append(results.params[0])
            config.metrics['slope'].append(results.params[1])
            config.metrics['intercept_std'].append(results.bse[0])
            config.metrics['slope_std'].append(results.bse[1])
            config.metrics['intercept_p_value'].append(results.pvalues[0])
            config.metrics['slope_p_value'].append(results.pvalues[1])

        elif config.experiment.method == Method.variance_linreg:

            target = self.get_strategy.get_target(config)
            x = sm.add_constant(target)
            y = self.get_strategy.get_single_base(config, [item])[0]

            results = sm.OLS(y, x).fit()

            config.metrics['item'].append(item)
            aux = self.get_strategy.get_aux(config, item)
            config.metrics['aux'].append(aux)
            config.metrics['R2'].append(results.rsquared)
            config.metrics['intercept'].append(results.params[0])
            config.metrics['slope'].append(results.params[1])
            config.metrics['intercept_std'].append(results.bse[0])
            config.metrics['slope_std'].append(results.bse[1])
            config.metrics['intercept_p_value'].append(results.pvalues[0])
            config.metrics['slope_p_value'].append(results.pvalues[1])

            diffs = []
            for p_id in range(0, len(target)):
                curr_x = target[p_id]
                curr_y = y[p_id]
                pred_y = results.params[1] * curr_x + results.params[0]
                diffs.append(abs(pred_y - curr_y))

            results_var = sm.OLS(diffs, x).fit()

            config.metrics['R2_var'].append(results_var.rsquared)
            config.metrics['intercept_var'].append(results_var.params[0])
            config.metrics['slope_var'].append(results_var.params[1])
            config.metrics['intercept_std_var'].append(results_var.bse[0])
            config.metrics['slope_std_var'].append(results_var.bse[1])
            config.metrics['intercept_p_value_var'].append(results_var.pvalues[0])
            config.metrics['slope_p_value_var'].append(results_var.pvalues[1])

        elif config.experiment.method == Method.cluster:

            x = self.get_strategy.get_target(config, True)
            y = self.get_strategy.get_single_base(config, [item])[0]

            X = np.array([x, y]).T
            db = DBSCAN(eps=config.experiment.params['eps'],
                        min_samples=config.experiment.params['min_samples']).fit(X)
            core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
            core_samples_mask[db.core_sample_indices_] = True
            labels = db.labels_
            number_of_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            number_of_noise_points = list(labels).count(-1)

            config.metrics['item'].append(item)
            config.metrics['aux'].append(self.get_strategy.get_aux(config, item))
            config.metrics['number_of_clusters'].append(number_of_clusters)
            config.metrics['number_of_noise_points'].append(number_of_noise_points)

        elif config.experiment.method == Method.polygon:

            polygons_region = []
            polygons_slope = []
            max_abs_slope = 0.0

            for config_child in configs_child:

                target = self.get_strategy.get_target(config_child)
                item_id = config_child.advanced_dict[item]

                metrics_keys = get_metrics_keys(config.experiment)

                for key in config_child.advanced_data:
                    if key not in metrics_keys:
                        key_primary = key + '_' + str(config_child.attributes.observables)
                        advanced_data = config_child.advanced_data[key][item_id]
                        config.metrics[key_primary].append(advanced_data)

                points_region = []
                points_slope = []

                if config_child.experiment.method == Method.linreg:

                    intercept = config_child.advanced_data['intercept'][item_id]
                    slope = config_child.advanced_data['slope'][item_id]
                    intercept_std = config_child.advanced_data['intercept_std'][item_id]
                    slope_std = config_child.advanced_data['slope_std'][item_id]

                    x_min = np.min(target)
                    x_max = np.max(target)
                    y_min = slope * x_min + intercept
                    y_max = slope * x_max + intercept
                    slope_tmp = slope + 3.0 * slope_std
                    y_tmp = slope_tmp * x_max + intercept
                    y_diff = 3.0 * np.abs(intercept_std) + np.abs(y_tmp - y_max)
                    y_min_up = y_min + y_diff
                    y_min_down = y_min - y_diff
                    y_max_up = y_max + y_diff
                    y_max_down = y_max - y_diff

                    points_region = [
                        geometry.Point(x_min, y_min_down),
                        geometry.Point(x_max, y_max_down),
                        geometry.Point(x_max, y_max_up),
                        geometry.Point(x_min, y_min_up),
                    ]

                    points_slope = [
                        geometry.Point(slope - 3.0 * slope_std, 0.0),
                        geometry.Point(slope + 3.0 * slope_std, 0.0),
                        geometry.Point(slope + 3.0 * slope_std, 1.0),
                        geometry.Point(slope - 3.0 * slope_std, 1.0),
                    ]

                    max_abs_slope = max(max_abs_slope, abs(slope))

                elif config_child.experiment.method == Method.linreg.variance_linreg:

                    intercept = config_child.advanced_data['intercept'][item_id]
                    slope = config_child.advanced_data['slope'][item_id]
                    slope_std = config_child.advanced_data['slope_std'][item_id]
                    intercept_var = config_child.advanced_data['intercept_var'][item_id]
                    slope_var = config_child.advanced_data['slope_var'][item_id]

                    x_min = np.min(target)
                    x_max = np.max(target)
                    y_min = slope * x_min + intercept
                    y_max = slope * x_max + intercept
                    y_min_var = slope_var * x_min + intercept_var
                    if y_min_var < 0:
                        y_min_var = -y_min_var
                    y_max_var = slope_var * x_max + intercept_var
                    if y_max_var < 0:
                        y_max_var = -y_max_var

                    points_region = [
                        geometry.Point(x_min, y_min - y_min_var),
                        geometry.Point(x_max, y_max - y_max_var),
                        geometry.Point(x_max, y_max + y_max_var),
                        geometry.Point(x_min, y_min + y_min_var),
                    ]

                    points_slope = [
                        geometry.Point(slope - 3.0 * slope_std, 0.0),
                        geometry.Point(slope + 3.0 * slope_std, 0.0),
                        geometry.Point(slope + 3.0 * slope_std, 1.0),
                        geometry.Point(slope - 3.0 * slope_std, 1.0),
                    ]

                    max_abs_slope = max(max_abs_slope, abs(slope))

                polygon = geometry.Polygon([[point.x, point.y]
                                            for point in points_region])
                polygons_region.append(polygon)

                polygon = geometry.Polygon([[point.x, point.y]
                                            for point in points_slope])
                polygons_slope.append(polygon)

            intersection = polygons_region[0]
            union = polygons_region[0]
            for polygon in polygons_region[1::]:
                intersection = intersection.intersection(polygon)
                union = union.union(polygon)
            area_intersection_rel = intersection.area / union.area

            intersection = polygons_slope[0]
            union = polygons_slope[0]
            for polygon in polygons_slope[1::]:
                intersection = intersection.intersection(polygon)
                union = union.union(polygon)
            slope_intersection_rel = intersection.area / union.area

            config.metrics['item'].append(item)
            aux = self.get_strategy.get_aux(config, item)
            config.metrics['aux'].append(aux)
            config.metrics['area_intersection_rel'].append(area_intersection_rel)
            config.metrics['slope_intersection_rel'].append(slope_intersection_rel)
            config.metrics['max_abs_slope'].append(max_abs_slope)
            
        elif config.experiment.method == Method.z_test_linreg:
            
            slopes = []
            slopes_std = []
            num_subs = []

            for config_child in configs_child:

                item_id = config_child.advanced_dict[item]
                metrics_keys = get_metrics_keys(config.experiment)

                for key in config_child.advanced_data:
                    if key not in metrics_keys:
                        key_child = key + '_' + str(config_child.attributes.observables)
                        advanced_data = config_child.advanced_data[key][item_id]
                        config.metrics[key_child].append(advanced_data)

                slopes.append(config_child.advanced_data['slope'][item_id])
                slopes_std.append(config_child.advanced_data['slope_std'][item_id])
                num_subs.append(len(config_child.attributes_dict['age']))

            std_errors = [slopes_std[i] / np.sqrt(num_subs[i]) for i in range (0, len(slopes_std))]
            z_value = (slopes[0] - slopes[1]) / np.sqrt(sum([std_error * std_error for std_error in std_errors]))
            p_value = norm.sf(abs(z_value)) * 2.0

            config.metrics['item'].append(item)
            aux = self.get_strategy.get_aux(config, item)
            config.metrics['aux'].append(aux)
            config.metrics['z_value'].append(z_value)
            config.metrics['p_value'].append(p_value)
            config.metrics['z_value_abs'].append(np.absolute(z_value))


    def iterate(self, config, configs_child):
        for item in config.base_list:
            if item in config.base_dict:
                self.single(item, config, configs_child)

    def run(self, config, configs_child):
        self.iterate(config, configs_child)


class ClockRunStrategy(RunStrategy):

    def single(self, item, config, configs_child):
        pass

    def iterate(self, config, configs_child):
        pass

    def run(self, config, configs_child):

        if config.experiment.method == Method.linreg:

            items = config.experiment_data['items']
            values = config.experiment_data['values']
            test_size = config.experiment_data['test_size']
            train_size = config.experiment_data['train_size']

            target = self.get_strategy.get_target(config)

            type = config.experiment.params['type']
            runs = config.experiment.params['runs']
            size = min(config.experiment.params['size'], train_size, len(items))
            config.experiment.params['size'] = size

            if type == ClockExogType.all.value:

                for exog_id in range(0, size):
                    config.metrics['item'].append(items[exog_id])
                    aux = self.get_strategy.get_aux(config, items[exog_id])
                    config.metrics['aux'].append(aux)

                    clock = Clock(
                        endog_data=target,
                        endog_names=config.attributes.target,
                        exog_data=values[0:exog_id + 1],
                        exog_names=items[0:exog_id + 1],
                        metrics_dict=config.metrics,
                        train_size=train_size,
                        test_size=test_size,
                        exog_num=exog_id + 1,
                        exog_num_comb=exog_id + 1,
                        num_bootstrap_runs=runs
                    )

                    build_clock_linreg(clock)

            elif type == ClockExogType.deep.value:

                for exog_id in range(0, size):
                    config.metrics['item'].append(exog_id + 1)
                    config.metrics['aux'].append(exog_id + 1)

                    clock = Clock(
                        endog_data=target,
                        endog_names=config.attributes.target,
                        exog_data=values[0:size + 1],
                        exog_names=items[0:size + 1],
                        metrics_dict=config.metrics,
                        train_size=train_size,
                        test_size=test_size,
                        exog_num=size,
                        exog_num_comb=exog_id + 1,
                        num_bootstrap_runs=runs
                    )

                    build_clock_linreg(clock)

            elif type == ClockExogType.single.value:

                config.metrics['item'].append(size)
                config.metrics['aux'].append(size)

                clock = Clock(
                    endog_data=target,
                    endog_names=config.attributes.target,
                    exog_data=values[0:size],
                    exog_names=items[0:size],
                    metrics_dict=config.metrics,
                    train_size=train_size,
                    test_size=test_size,
                    exog_num=size,
                    exog_num_comb=size,
                    num_bootstrap_runs=runs
                )

                build_clock_linreg(clock)


class MethylationRunStrategy(RunStrategy):

    def single(self, item, config_child, configs_child):
        pass

    def iterate(self, config, configs_child):
        pass

    def run(self, config, configs_child):

        if config.experiment.method == Method.scatter:

            item = config.experiment.params['item']

            plot_data = []

            for config_child in configs_child:

                curr_plot_data = []

                target = self.get_strategy.get_target(config_child)
                methylation = self.get_strategy.get_single_base(config_child, [item])[0]
                color = cl.scales['8']['qual']['Set1'][configs_child.index(config_child)]

                scatter = go.Scatter(
                    x=target,
                    y=methylation,
                    name=str(config_child.attributes.observables),
                    mode='markers',
                    marker=dict(
                        opacity=0.75,
                        size=15,
                        color=color,
                        line=dict(width=2)
                    ),
                )
                curr_plot_data.append(scatter)

                if config_child.experiment.method == Method.linreg:

                    target = self.get_strategy.get_target(config_child)
                    x = sm.add_constant(target)
                    y = self.get_strategy.get_single_base(config_child, [item])[0]

                    results = sm.OLS(y, x).fit()

                    intercept = results.params[0]
                    slope = results.params[1]
                    intercept_std = results.bse[0]
                    slope_std = results.bse[1]

                    x_min = np.min(target)
                    x_max = np.max(target)
                    y_min = slope * x_min + intercept
                    y_max = slope * x_max + intercept
                    slope_tmp = slope + 3.0 * slope_std
                    y_tmp = slope_tmp * x_max + intercept
                    y_diff = 3.0 * np.abs(intercept_std) + np.abs(y_tmp - y_max)
                    y_min_up = y_min + y_diff
                    y_min_down = y_min - y_diff
                    y_max_up = y_max + y_diff
                    y_max_down = y_max - y_diff

                    scatter = go.Scatter(
                        x=[x_min, x_max],
                        y=[y_min, y_max],
                        mode='lines',
                        marker=dict(
                            color=color,
                            line=dict(width=8)
                        ),
                        showlegend=False
                    )
                    curr_plot_data.append(scatter)

                    scatter = go.Scatter(
                        x=[x_min, x_max, x_max, x_min, x_min],
                        y=[y_min_down, y_max_down, y_max_up, y_min_up, y_min_down],
                        fill='tozerox',
                        mode='lines',
                        marker=dict(
                            opacity=0.75,
                            color=color,
                            line=dict(width=8)
                        ),
                        showlegend=False
                    )
                    curr_plot_data.append(scatter)

                elif config_child.experiment.method == Method.variance_linreg:

                    target = self.get_strategy.get_target(config_child)
                    x = sm.add_constant(target)
                    y = self.get_strategy.get_single_base(config_child, [item])[0]

                    results = sm.OLS(y, x).fit()

                    intercept = results.params[0]
                    slope = results.params[1]

                    diffs = []
                    for p_id in range(0, len(target)):
                        curr_x = target[p_id]
                        curr_y = y[p_id]
                        pred_y = slope * curr_x + intercept
                        diffs.append(abs(pred_y - curr_y))

                    results_var = sm.OLS(diffs, x).fit()

                    intercept_var = results_var.params[0]
                    slope_var = results_var.params[1]

                    x_min = np.min(target)
                    x_max = np.max(target)
                    y_min = slope * x_min + intercept
                    y_max = slope * x_max + intercept
                    y_min_var = slope_var * x_min + intercept_var
                    if y_min_var < 0:
                        y_min_var = -y_min_var
                    y_max_var = slope_var * x_max + intercept_var
                    if y_max_var < 0:
                        y_max_var = -y_max_var

                    scatter = go.Scatter(
                        x=[x_min, x_max],
                        y=[y_min, y_max],
                        mode='lines',
                        marker=dict(
                            color=color,
                            line=dict(width=8)
                        ),
                        showlegend=False
                    )
                    curr_plot_data.append(scatter)

                    scatter = go.Scatter(
                        x=[x_min, x_max, x_max, x_min, x_min],
                        y=[y_min - y_min_var,
                           y_max - y_max_var,
                           y_max + y_max_var,
                           y_min + y_min_var,
                           y_min - y_min_var],
                        fill='tozerox',
                        mode='lines',
                        marker=dict(
                            opacity=0.75,
                            color=color,
                            line=dict(width=4)
                        ),
                        showlegend=False
                    )
                    curr_plot_data.append(scatter)

                elif config_child.experiment.method == Method.cluster:
                    pass

                plot_data += curr_plot_data

            config.experiment_data['data'] = plot_data


class ObservablesRunStrategy(RunStrategy):

    def single(self, item, config, configs_child):
        pass

    def iterate(self, config, configs_primary):
        pass

    def run(self, config, configs_child):

        if config.experiment.method == Method.histogram:

            plot_data = []
            for config_child in configs_child:

                curr_plot_data = []

                target = self.get_strategy.get_target(config_child)
                is_number_list = [is_float(t) for t in target]
                if False in is_number_list:
                    xbins = {}
                else:
                    bin_size = config.experiment.params['bin_size']
                    xbins = dict(
                        start=min(target) - 0.5 * bin_size,
                        end=max(target) + 0.5 * bin_size,
                        size=bin_size
                    )

                color = cl.scales['8']['qual']['Set1'][configs_child.index(config_child)]

                if config_child.experiment.method == Method.histogram:

                    histogram = go.Histogram(
                        x=target,
                        name=str(config_child.attributes.observables),
                        xbins=xbins,
                        marker=dict(
                            opacity=config.experiment.params['opacity'],
                            color=color
                        )
                    )

                    curr_plot_data.append(histogram)

                plot_data += curr_plot_data

            config.experiment_data['data'] = plot_data
