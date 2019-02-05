import yaml, sys
from qualifyr.utility import get_logger

logger = get_logger(__file__)
def check_conditions(conditions):
    for file_type in conditions:
        for metric in conditions[file_type]:
            if 'failure' not in conditions[file_type][metric] and 'warning' not in conditions[file_type][metric]:
                logger.error('ERROR in conditions yml file')
                logger.error('Every metric in the conditions file must have a warning or failure condition')
                sys.exit(1)



def import_yaml_file(filepath):
    with open(filepath) as yml_file:
        conditions = yaml.load(yml_file.read())
    check_conditions(conditions)
    return conditions