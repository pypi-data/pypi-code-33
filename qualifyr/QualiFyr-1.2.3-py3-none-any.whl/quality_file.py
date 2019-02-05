import sys
import json
from collections import OrderedDict
from qualifyr.utility import get_logger
from qualifyr.quality_check import QualityCheck

logger = get_logger(__file__)
class QualityFile:
    file_type = None

    def __init__(self, file_path, file_id = None):
        self.file_path = file_path 
        self.metrics = {} # a dict of metrics key is the metric name, value is the metric value
        self.quality_checks = [] # A list of tuples where the first item is the metric name, second is the value, third if the reason for failure, and the last is the failure category (PASS, FAILURE or WARNING)
        self.file_id = file_id # used in cases where there are two files for a pair of fastqs, e.g FASTQC
        
        self.parse()
    
    @property
    def type_and_id(self):
        if self.file_id:
            return '{0} {1}'.format(self.file_type, self.file_id)
        else:
            return self.file_type

    @property
    def failed_checks(self):
        return [ quality_check for quality_check in self.quality_checks if quality_check.result != 'PASS' ]

    def parse(self):
        raise NotImplementedError


    def check(self, conditions): # method to check if the metrics contained in the quality file meet the conditions specified in the yml conditions file
        # Steps as follows
        # check all condition keys exist
        # loop through conditions and apply condition, one of gt,lt,lt_gt,eq,ne
        # return conditions that fail

        # check all condition keys exist - extract conditions for file type
        try:
            conditions_for_file_type = conditions[self.file_type]
        except KeyError as e:
            logger.error("No such quality file type {0} in conditions. The available file types in the supplied condition file are {1}".format(e, ", ".join(conditions.keys())))
            sys.exit(1)

        # loop through conditions and apply condition, one of gt,lt,lt_gt,eq,ne
        for metric_name in conditions_for_file_type:
            self.quality_checks.append(self.check_metric(metric_name, conditions_for_file_type))


    def check_metric(self, metric_name, conditions):
        """
        checks a metric against a condition and returns a tuple with PASS, FAILURE or WARNING and a string with a summary of the check
        Params:
            metric_name (string): name of the metric
            conditions (dict): dict containing checks to be made
        Returns:
            tuple: metric_name, metric_value, reason for warning/failure, check_result of failure
        """
        try:
            metric_value = self.metrics[metric_name]
            return QualityCheck(metric_name, metric_value, conditions)
            
        except KeyError as e:
            logger.error("No such metric {0}. The available metrics are {1}".format(e, ", ".join(self.metrics.keys())))
            sys.exit(1)

    def quality_checks_to_dict(self, only_failed_checks = True):
        quality_checks_dict = { self.type_and_id : OrderedDict() }
        if only_failed_checks:
            included_quality_checks = self.failed_checks
        else:
            included_quality_checks = self.quality_checks

        for quality_check in included_quality_checks:
             quality_checks_dict[self.type_and_id][quality_check.metric_name] = OrderedDict([
                        ('metric_value' , quality_check.metric_value),
                        ('check' , quality_check.check),
                        ('check_result' , quality_check.result)
                    ])
        return quality_checks_dict

    def output_quality_checks_string(self, output_format = 'tsv', only_failed_checks = True):
        if output_format == 'tsv':
            if only_failed_checks:
                included_quality_checks = self.failed_checks
            else:
                included_quality_checks = self.quality_checks

            checks_string = '\n'.join(
                    [ '\t'.join([
                        self.type_and_id,
                        str(quality_check.metric_name),
                        str(quality_check.metric_value),
                        str(quality_check.check),
                        str(quality_check.result)]
                        )
                        for quality_check in included_quality_checks
                    ]
                )
            return checks_string

        elif output_format == 'json':
            return json.dumps(self.quality_checks_to_dict(only_failed_checks), indent = 2 )

    def overall_qc_check_result(self):
        failure_categories = [quality_check.result for quality_check in self.quality_checks]
        if 'FAILURE' in failure_categories:
            return 'FAILURE'
        elif 'WARNING' in failure_categories:
            return 'WARNING'
        else:
            return 'PASS'
    
    @staticmethod
    def check_multiple_files(quality_files, conditions):
        # check multiple quality files
        for quality_file in quality_files:
            quality_file.check(conditions)
        return quality_files
    
    @staticmethod
    def multiple_overall_qc_check_result(quality_files):
        failure_categories = [quality_file.overall_qc_check_result() for quality_file in quality_files]
        if 'FAILURE' in failure_categories:
            return 'FAILURE'
        elif 'WARNING' in failure_categories:
            return 'WARNING'
        else:
            return 'PASS'

    @staticmethod
    def multiple_qc_result_string(sample_name, quality_files, output_format = 'tsv', only_failed_checks = True):
        """
        Function to produce a string of the results from multiple quality check files
        """ 
        if output_format == 'tsv':
            header_string = 'file_type\tmetric_name\tmetric_value\tcheck\tcheck result\n'
            quality_check_strings = [quality_file.output_quality_checks_string(output_format, only_failed_checks) for quality_file in quality_files]
            # remove empty strings
            quality_check_strings = [quality_check_string for quality_check_string in quality_check_strings if quality_check_string != ""]
            body_string = '\n'.join(quality_check_strings)
            return header_string + body_string + '\n'
        elif output_format == 'json':
            checks_dict = {}
            for quality_file in quality_files:
                checks_dict.update(quality_file.quality_checks_to_dict(only_failed_checks))

            output_dict = OrderedDict([
                ('sample_name', sample_name),
                ('result', QualityFile.multiple_overall_qc_check_result(quality_files)),
                ('checks', checks_dict)
            ])
            return json.dumps(output_dict, indent = 2 )


            