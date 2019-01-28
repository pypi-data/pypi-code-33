# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs"""

from datetime import datetime
import json
import numpy as np
import pytz
import time
from automl.client.core.common import constants, logging_utilities
from automl.client.core.common.metrics import minimize_or_maximize
from automl.client.core.common.console_interface import ConsoleInterface


class RemoteConsoleInterface(ConsoleInterface):
    """
    Class responsible for printing iteration information to console for a remote run
    """

    def __init__(self, logger, file_logger=None):
        """
        RemoteConsoleInterface constructor
        :param logger: Console logger for printing this info
        :param file_logger: Optional file logger for more detailed logs
        """
        self._console_logger = logger
        self.logger = file_logger
        self.metric_map = {}
        self.run_map = {}
        self.properties_map = {}
        self.best_metric = None
        super().__init__("score", self._console_logger)

    def print(self, parent_run, primary_metric):
        """
        Print all history for a given parent run
        :param parent_run: AutoMLRun to print status for
        :param primary_metric: Metric being optimized for this run
        :return:
        """
        try:
            self.print_descriptions()
            self.print_columns()
        except Exception as e:
            logging_utilities._log_traceback(e, self.logger)
            raise
        print_loop = True
        best_metric = None
        while print_loop:
            status = parent_run.get_tags().get('_aml_system_automl_status', None)
            if status is None:
                status = parent_run.get_status()
            if status in ('Completed', 'Failed', 'Canceled'):
                print_loop = False
            children = sorted(list(parent_run.get_children(_rehydrate_runs=False)), key=lambda run: run._run_number)
            if children is None:
                continue

            for run in children:
                run_id = run.id
                status = run.get_status()
                if ((run_id not in self.run_map) and
                        (status in ('Completed', 'Failed'))):
                    metrics = run.get_metrics()
                    properties = run.get_properties()
                    self.metric_map[run_id] = metrics
                    self.run_map[run_id] = run
                    self.properties_map[run_id] = properties
                    if 'iteration' in properties:
                        current_iter = properties['iteration']
                    else:
                        current_iter = run_id.split('_')[-1]

                    print_line = ""
                    if 'run_preprocessor' in properties:
                        print_line += properties['run_preprocessor']
                    if 'run_algorithm' in properties:
                        print_line += " " + properties['run_algorithm']

                    created_time = run._run_dto['created_utc']
                    if isinstance(created_time, str):
                        created_time = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                    start_iter_time = created_time.replace(tzinfo=pytz.UTC)
                    end_iter_time = datetime.strptime(run.get_details()['endTimeUtc'],
                                                      '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
                    iter_duration = str(end_iter_time - start_iter_time).split(".")[0]

                    objective = minimize_or_maximize(metric=primary_metric)
                    if primary_metric in metrics:
                        score = metrics[primary_metric]
                    else:
                        score = constants.Defaults.DEFAULT_PIPELINE_SCORE

                    if best_metric is None or best_metric == 'nan' or np.isnan(best_metric):
                        best_metric = score
                    elif objective == constants.OptimizerObjectives.MINIMIZE:
                        if score < best_metric:
                            best_metric = score
                    elif objective == constants.OptimizerObjectives.MAXIMIZE:
                        if score > best_metric:
                            best_metric = score
                    else:
                        best_metric = 'Unknown'

                    self.print_start(current_iter)
                    self.print_pipeline(print_line)
                    self.print_end(iter_duration, score, best_metric)

                    errors = properties.get('friendly_errors')
                    if errors is not None:
                        error_dict = json.loads(errors)
                        for error in error_dict:
                            self.print_error(error_dict[error])
            time.sleep(3)

    @staticmethod
    def _show_output(current_run, logger, file_logger, primary_metric):
        try:
            remote_printer = RemoteConsoleInterface(
                logger, file_logger)
            remote_printer.print(current_run, primary_metric)
        except KeyboardInterrupt:
            logger.write("Received interrupt. Returning now.")
