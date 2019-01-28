# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import datetime
from dateutil import parser as date_parser
import json
from multiprocessing.dummy import Pool
import operator
import re
import traceback
import urllib
import urllib.request
from urllib.error import HTTPError

from azureml.core.compute.amlcompute import AmlCompute
from azureml.core.run import Run
# noinspection PyProtectedMember
from azureml._restclient.run_client import RunClient
# noinspection PyProtectedMember
from azureml.widgets._telemetry_logger import _TelemetryLogger

from azureml.widgets._constants import WIDGET_REFRESH_SLEEP_TIME, WEB_WORKBENCH_PARENT_RUN_ENDPOINT
from azureml.widgets.run_details import RunDetails, PLATFORM
from azureml.widgets._widget_run_details_base import _WidgetRunDetailsBase
# noinspection PyProtectedMember
from azureml.widgets._transformer import _DataTransformer

_logger = _TelemetryLogger.get_telemetry_logger(__name__)

if PLATFORM == 'JUPYTER':
    # noinspection PyProtectedMember
    from azureml.widgets._userrun._widget import _UserRunWidget
else:
    assert PLATFORM == "DATABRICKS"
    # noinspection PyProtectedMember
    from azureml.widgets._userrun._universal_widget import _UserRunWidget


class _UserRunDetails(_WidgetRunDetailsBase):
    """Generic run details widget."""

    _metrics_cache = {}
    _run_finished_states = ["completed", "failed", "canceled"]
    _str_waiting_log = "Your job is submitted in Azure cloud and we are monitoring to get logs..."
    _str_no_log = "Log is empty or no log files found."

    def __init__(self, run_instance, run_type="experiment", refresh_time=WIDGET_REFRESH_SLEEP_TIME,
                 widget=_UserRunWidget, recursive_children=False, rehydrate_runs=False):
        self.experiment = run_instance.experiment
        self.run_instance = run_instance
        self.run_client = RunClient.create(
            workspace=self.experiment.workspace,
            experiment_name=self.experiment.name,
            run_id=self.run_instance.id,
            user_agent="azureml-sdk-widget-{}".format(run_type))
        self.transformer = self._create_transformer()
        self.child_widget_instance = None
        self._transformed_child_runs_cache = []
        self._run_cache = {}
        self.run_properties = {}
        created_utc = self.run_instance._run_dto['created_utc']
        self.run_init_time = date_parser.parse(created_utc) if not isinstance(created_utc, datetime.datetime) \
            else created_utc
        self.run_type = run_type
        self.recursive_children = recursive_children
        self.rehydrate_runs = rehydrate_runs
        self.selected_process = None
        self.auto_cluster = False
        _logger.info("Creating worker pool")
        self._pool = Pool()
        super().__init__(refresh_time, widget)

    def __del__(self):
        """Destructor for the widget."""
        _logger.info("Closing worker pool")
        self._pool.close()
        if super().__del__:
            super().__del__()

    @staticmethod
    def _sort_distributed_processes(distributed_processes):
        def ord_key_distributed_processes(process):
            # Direct alphanumeric comparison doesn't suffice- otherwise "worker_10" will show up before "worker_2"
            # Tuples compare in columnar order- SortBy(A, B, C) works like .Net's OrderBy(A).ThenBy(B).ThenBy(C)
            # Tupleize by underscores, casting columns to integers where possible to enforce numeric ordering.
            return tuple(int(s) if s.isdigit() else s for s in process.split("_"))
        return sorted(distributed_processes, key=ord_key_distributed_processes)

    def get_widget_data(self, widget_settings=None):
        """
        Retrieve and transform data from run history to be rendered by widget

        :param widget_settings: Settings to be applied to widget. Supported settings are: 'debug' and 'display'
        :type widget_settings: dict
        :return: Dictionary containing data to be rendered by the widget.
        :rtype: dict
        """
        if not self.settings:
            self.settings = widget_settings

        # set azure portal deep link for the run
        self.widget_instance.workbench_uri = self._get_web_workbench_run_detail_url(self.experiment)

        self.widget_instance.run_id = self.run_instance.id
        self.tags = self.run_instance.get_tags()

        run_properties_init = {'run_id': self.run_instance.id,
                               'created_utc': self.run_instance._run_dto['created_utc'],
                               'properties': self.run_instance.get_properties(),
                               'tags': self.tags}

        self.run_properties = {**self.run_properties, **run_properties_init}

        self.widget_instance.run_properties = self.run_properties

        self._pool.apply_async(func=self._get_run_metrics, callback=self._update_metrics)

        run_details = self.run_instance.get_details()

        self.error = run_details.get("error")
        run_config = run_details.get("runDefinition")

        if run_config:
            _aml_compute = run_config.get('AmlCompute') if run_config.get('Target') == 'amlcompute' else None
            self.auto_cluster = _aml_compute and _aml_compute.get('VmSize')
            self.run_properties['script_name'] = run_config.get('Script')
            self.run_properties['arguments'] = " ".join(run_config['Arguments']) \
                if 'Arguments' in run_config and run_config['Arguments'] else None

        self._pool.apply_async(func=self._get_compute_target_status, args=(run_details.get("target"),),
                               callback=self._update_compute_target_status)

        # get parent run properties
        self.run_properties['end_time_utc'] = run_details.get("endTimeUtc")
        self.run_properties['status'] = self.tags.get("_aml_system_automl_status") \
            if self.tags.get("_aml_system_automl_status") else run_details.get("status")
        self.run_properties['log_files'] = run_details.get("logFiles")

        # log file names have process names embedded within the name which we need to extract
        distributed_processes = []
        log_files = run_details.get("logFiles")
        if log_files:
            for file in log_files.keys():
                found_group = re.search(r'log_(.*[0-9]*).txt$', file)
                if found_group is not None:
                    process_name = found_group.group(1)
                    if process_name not in distributed_processes:
                        distributed_processes.append(process_name)

        self.run_properties['distributed_processes'] = \
            _UserRunDetails._sort_distributed_processes(distributed_processes)

        self._add_additional_properties(self.run_properties)

        run_properties_temp = copy.deepcopy(self.run_properties)
        run_properties_temp['SendToClient'] = '1'
        self.widget_instance.run_properties = run_properties_temp
        self.properties = self.run_properties['properties']

        if self.selected_process:
            _run_process = self.selected_process
        else:
            _run_process = self.run_properties['distributed_processes'][0] \
                if self.run_properties['distributed_processes'] else None
        self._get_run_logs_async(log_files,
                                 self.run_properties['status'],
                                 self.error,
                                 _run_process)

        child_runs = self._get_child_runs()

        # Widget renders child runs in two phases. In phase one it retrieves the child runs from backend and
        # renders them with corresponding properties. Then, in second phase, when their metrics are retrieved
        # it renders child runs again, this time it updates each child run with its corresponding best metric value.
        # we keep this cache for two purposes:
        # 1. so that in next refresh iteration we do not lose the metrics and user keeps seeing
        # updated child runs on the client
        # 2. Only query the backend for runs that are not completed
        copy_cache = copy.deepcopy(self._transformed_child_runs_cache)
        for c in child_runs:
            _run = next((x for x in copy_cache if x['run_number'] == c['run_number']), None)
            if not _run:
                # todo: switch to dict
                copy_cache.append(c)
            else:
                ind = copy_cache.index(_run)
                copy_cache[ind] = {**_run, **c}

        self.widget_instance.child_runs = copy_cache
        self._transformed_child_runs_cache = copy_cache

        # get the run with smallest datetime that is already running. We do not need to get the older runs as they
        # are completed and cached
        incomplete_runs = [x for x in self._transformed_child_runs_cache if x['status'].lower() not in
                           _UserRunDetails._run_finished_states]

        if incomplete_runs:
            def parse_created_time(date):
                return date_parser.parse(date) if not isinstance(date, datetime.datetime) else date

            self.run_init_time = min(parse_created_time(run['created_time_dt']) for run in incomplete_runs)

        transformed_children_metrics = {}
        if self._transformed_child_runs_cache:
            run_ids = [x['run_id'] for x in self._transformed_child_runs_cache]

            metrics = {}

            # get list of not cached runs for which we will retrieve metrics
            not_cached_runs = [x for x in self._transformed_child_runs_cache if x['run_id']
                               not in _UserRunDetails._metrics_cache]
            if not_cached_runs:
                metrics = self._get_metrics(not_cached_runs)

                # populate cache with metrics from completed runs
                completed_run_ids = [x['run_id'] for x in self._transformed_child_runs_cache
                                     if x['status'].lower() in _UserRunDetails._run_finished_states]
                metrics_to_be_cached = {k: v for k, v in metrics.items() if k in completed_run_ids}
                _UserRunDetails._metrics_cache = {**_UserRunDetails._metrics_cache, **metrics_to_be_cached}

            cached_run_metrics = {k: v for k, v in _UserRunDetails._metrics_cache.items() if k in run_ids}
            metrics = {**cached_run_metrics, **metrics}

            mapped_metrics = self._get_mapped_metrics(metrics, self._transformed_child_runs_cache)

            transformed_children_metrics = self.transformer.transform_widget_metric_data(mapped_metrics,
                                                                                         self._get_primary_config())
            self.widget_instance.child_runs_metrics = transformed_children_metrics

            updated_runs = self._update_children_with_metrics(self._transformed_child_runs_cache,
                                                              transformed_children_metrics)
            if updated_runs:
                self._transformed_child_runs_cache = sorted(updated_runs, key=operator.itemgetter("run_number"))
                self.widget_instance.child_runs = self._transformed_child_runs_cache

        return {'status': self.run_properties['status'],
                'workbench_run_details_uri': self._get_web_workbench_run_detail_url(self.experiment),
                'run_id': self.run_instance.id,
                'run_properties': self.run_properties,
                'child_runs': self.widget_instance.child_runs,
                'children_metrics': self.widget_instance.child_runs_metrics,
                'run_metrics': self.widget_instance.run_metrics,
                'run_logs': self.widget_instance.run_logs,
                'widget_settings': widget_settings}

    def _add_additional_properties(self, run_properties):
        run_properties['run_duration'] = self.transformer._get_run_duration(run_properties['status'],
                                                                            run_properties['created_utc'],
                                                                            run_properties['end_time_utc'])

    def _get_compute_target_status(self, target_name):
        if not self.auto_cluster:
            ws_targets = []
            try:
                ws_targets = self.experiment.workspace.compute_targets
            except Exception as e:
                if self.isDebug:
                    _logger.warning(e)

            for ct_name in ws_targets:
                ct = ws_targets[ct_name]
                if ct.name == target_name and type(ct) is AmlCompute:
                    ct_dict = {
                        "provisioning_state": ct.provisioning_state,
                        "provisioning_errors": ct.provisioning_errors
                    }
                    status_dict = {}
                    ct_status = ct.get_status()
                    if ct_status:
                        status_dict = {
                            "target_node_count": ct_status.target_node_count,
                            "allocation_state": ct_status.allocation_state,
                            "node_state_counts": ct_status.node_state_counts.serialize(),
                            "scale_settings": ct_status.scale_settings.serialize(),
                            "vm_size": ct_status.vm_size,
                            "current_node_count": ct_status.current_node_count,
                        }
                    return {**ct_dict, **status_dict}
        else:
            # Temporarily read from both tags for backwards compatibility
            _ct_status_str = self.tags.get('_aml_system_ComputeTargetStatus')
            if not _ct_status_str:
                _ct_status_str = self.tags.get('ComputeTargetStatus')
            if _ct_status_str:
                _ct_status = json.loads(_ct_status_str)

                return {
                    "allocation_state": _ct_status.get('AllocationState'),
                    "current_node_count": _ct_status.get('CurrentNodeCount'),
                    "target_node_count": _ct_status.get('TargetNodeCount'),
                    "node_state_counts": {
                        "preparingNodeCount": _ct_status.get('PreparingNodeCount'),
                        "runningNodeCount": _ct_status.get('RunningNodeCount')
                    }
                }

        return {}

    def _update_compute_target_status(self, result):
        self.widget_instance.compute_target_status = result

    def _get_run_logs_async(self, log_files, status, error, process):
        self._pool.apply_async(func=self._get_run_logs, args=(log_files, status, error, process),
                               callback=self._update_logs)

    def _get_run_logs(self, log_files, status, error, process):
        _status = status.lower()
        logs = _UserRunDetails._str_no_log \
            if _status in _UserRunDetails._run_finished_states \
            else _UserRunDetails._str_waiting_log
        _logs = ''

        if log_files:
            _logs = self._get_formatted_logs(log_files, process)

        if error:
            inner_error = error.get('error')
            error_message = inner_error.get('message') if inner_error else ""
            _error = "" if not error_message else "{0}\n".format(error_message)
            _logs = "{0}\nError occurred: {1}".format(_logs, _error)
        elif _status in ['completed', 'canceled']:
            _logs = "{0}\nRun is {1}.".format(_logs, _status)

        if _logs:
            logs = _logs
        return logs

    def _get_formatted_logs(self, log_files, process):
        _process = "_{0}.".format(process) if process else ""
        return "{0}{1}{2}{3}".format(self._get_log('ice_log', log_files),
                                     self._get_log('image_build_log', log_files),
                                     self._get_log('control_log' + _process, log_files),
                                     self._get_log('driver_log' + _process, log_files))

    def _get_log(self, log_type, log_files):
        log_uri = [v for (k, v) in log_files.items() if log_type in k]
        if log_uri:
            url = log_uri[0]
            try:
                response = urllib.request.urlopen(url)
                log_content_bytes = response.read()
                log_content = self._post_process_log(log_content_bytes.decode('utf-8'))
                return "{}\n".format(log_content)
            except HTTPError as e:
                if self.isDebug:
                    self.widget_instance.error = repr(traceback.format_exception(type(e), e, e.__traceback__))
                return ''
        return ''

    def _post_process_log(self, log_content):
        return log_content

    def _update_logs(self, result):
        self.widget_instance.run_logs = result

    def _get_child_runs(self):
        # put a buffer for look-back due to time sync
        buffered_init_time = self.run_init_time - datetime.timedelta(seconds=20)
        child_run_dtos = self.run_client.get_child_runs(
            root_run_id=self.run_instance.id,
            recursive=self.recursive_children,
            _filter_on_server=True,
            created_after=buffered_init_time)

        if self.rehydrate_runs:
            child_runs = list(Run._rehydrate_runs(self.experiment, child_run_dtos))
        else:
            child_runs = list(Run._dto_to_run(self.experiment, child) for child in child_run_dtos)

        for child_run in child_runs:
            self._run_cache[child_run.id] = child_run

        return self.transformer.transform_widget_run_data(child_runs)

    def _get_run_metrics(self):
        run_metrics = self.run_instance.get_metrics(populate=True)
        transformed_run_metrics = []

        for key, value in run_metrics.items():
            metric_data = {
                'name': key,
                'run_id': self.run_instance.id,
                # get_metrics can return array or not based on metrics being series or scalar value
                'categories': list(range(len(value))) if isinstance(value, list) else [0],
                'series': [{'data': value if isinstance(value, list) else [value]}]}
            transformed_run_metrics.append(metric_data)

        model_explanation_metric = self._get_model_explanation_metric()
        if (model_explanation_metric):
            transformed_run_metrics.append(model_explanation_metric)

        return transformed_run_metrics

    def _get_model_explanation_metric(self):
        if self.tags.get('model_explanation') != 'True':
            return None

        try:
            # Take a soft dependency on azureml-explain-model
            from azureml.explain.model._internal import get_model_summary, get_classes
            # Add the model explanation information
            class_labels = get_classes(self.run_instance)
            explanation = get_model_summary(self.run_instance)
            overall_summary = explanation[0]
            overall_imp = explanation[1]
            # Classification Model's explanation includes Per_class information while Regression Model does not
            per_class_summary = explanation[2] if len(
                explanation) > 2 else None
            per_class_imp = explanation[3] if len(
                explanation) > 3 else None

            return {'name': 'model_explanation',
                    'run_id': self.run_instance.id,
                    'categories': [0],
                    'series': [{'data': [{
                        # 'classes': class_labels,
                        # 'global_importance_values': overall_summary,
                        # 'global_importance_names': overall_imp,
                        # 'per_class_values': per_class_summary,
                        # 'per_class_names': per_class_imp}]}]}
                        'class_labels': class_labels,
                        'overall_summary': overall_summary,
                        'overall_imp': overall_imp,
                        'per_class_summary': per_class_summary,
                        'per_class_imp': per_class_imp}]}]}
        except ImportError as import_error:
            _logger.error(import_error.msg)
            return None

    def _update_metrics(self, result):
        self.widget_instance.run_metrics = result

    def _get_metrics(self, child_runs):
        child_run_ids = [run['run_id'] for run in child_runs]
        # noinspection PyProtectedMember
        return self.run_client._get_metrics_by_run_ids(child_run_ids)

    def _get_mapped_metrics(self, metrics, child_runs):
        run_number_mapper = {c['run_id']: c['run_number'] for c in child_runs}
        return {run_number_mapper[k]: v for k, v in metrics.items()}

    def _update_children_with_metrics(self, child_runs, metrics):
        pass

    def _get_web_workbench_run_detail_url(self, experiment):
        """Generate the web workbench job url for the run details.

        :param experiment: The experiment.
        :type experiment: azureml.core.experiment.Experiment
        """
        # TODO: Host to web workbench needs to be retrieved
        return (WEB_WORKBENCH_PARENT_RUN_ENDPOINT).format(
            experiment.workspace.subscription_id,
            experiment.workspace.resource_group,
            experiment.workspace.name,
            experiment.name,
            self.run_instance.id)

    def _get_primary_config(self):
        if self.settings and 'Metric' in self.settings:
            return {
                'name': self.settings['Metric']['name'],
                'goal': self.settings['Metric']['goal'] if 'goal' in self.settings['Metric'] else 'minimize'
            }
        return {}

    def _should_stop_refresh(self, widget_data):
        return \
            widget_data['run_properties']['status'] is not None and \
            widget_data['run_properties']['status'].lower() in _UserRunDetails._run_finished_states

    def _register_events(self):
        self._register_event(self._on_selected_run_id_change, "selected_run_id")
        self._register_event(self._on_run_process_change, "run_process")

    def _on_run_process_change(self, change):
        self.selected_process = change.new
        self._get_run_logs_async(self.widget_instance.run_properties['log_files'],
                                 self.widget_instance.run_properties['status'],
                                 self.error, change.new)

    def _on_selected_run_id_change(self, change):
        # work around about close of popup, selected_run_id is set to empty string right after with it is set
        # with value
        if change.new == '':
            return
        if self.child_widget_instance is not None and change.new != '':
            self.child_widget_instance.close()
        if self.widget_instance.child_runs:
            run_list = [x for x in self.widget_instance.child_runs if x['run_id'] == change.new]
            if len(run_list) > 0:
                run = self._run_cache[change.new]
                selected_run_widget = RunDetails(run)  # type: _WidgetRunDetailsBase
                display_setting = self.settings["childWidgetDisplay"] if "childWidgetDisplay" in self.settings else ""
                selected_run_widget.show(widget_settings={'display': display_setting})
                self.child_widget_instance = selected_run_widget.widget_instance

    def _get_telemetry_values(self, func):
        telemetry_values = super()._get_telemetry_values(func)
        telemetry_values['widgetRunType'] = self.run_type
        return telemetry_values

    # noinspection PyMethodMayBeStatic
    def _create_transformer(self):
        return _DataTransformer()
