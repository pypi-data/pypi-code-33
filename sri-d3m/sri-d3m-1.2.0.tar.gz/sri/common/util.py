import logging

import pandas
from d3m import container
from d3m.metadata import base as meta_base

from sri.common import constants

# Keep track of loggers so we can change their level globally.
_loggers = {}
_current_log_level = logging.INFO

def computeNodeLabel(nodeID, nodeModifier):
    if (nodeModifier != constants.NODE_MODIFIER_SOURCE and nodeModifier != constants.NODE_MODIFIER_TARGET):
        raise ValueError("Node modifier must be NODE_MODIFIER_SOURCE/NODE_MODIFIER_TARGET, found: %s" % (nodeModifier))

    return (int(nodeID) + 1) * nodeModifier

def write_tsv(path, rows):
    with open(path, 'w') as file:
        # TODO(eriq): Batch
        for row in rows:
            file.write("\t".join(map(str, row)) + "\n")

def get_logger(name):
    if (len(_loggers) == 0):
        logging.basicConfig(
                level = _current_log_level,
                format = '%(asctime)s [%(levelname)s] %(name)s -- %(message)s')

    if (name in _loggers):
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(_current_log_level)

    _loggers[name] = logger
    return logger

def set_logging_level(level = logging.INFO):
    _current_log_level = level
    for name in _loggers:
        _loggers[name].setLevel(level)

# Prepare the frame to be output as predictions by:
#  - Re-ordering by the d3m index order.
#  - Removing extra rows.
#  - Adding missing rows.
#  - Attatching the correct semantic types.
# If |increment_missing| is True, then the missing values will all get different, incremented values
# (which will start at 0 or |missing_value| (if present)).
def prep_predictions(predictions, d3m_indexes, metadata_source = None, missing_value = None, increment_missing = False):
    # First add in the proper ordering of the rows.
    order = [[int(d3m_indexes[i]), i] for i in range(len(d3m_indexes))]
    order_frame = container.DataFrame(order, columns = [constants.D3M_INDEX, 'order'])

    data_columns = list(predictions.columns)
    data_columns.remove(constants.D3M_INDEX)

    predictions[constants.D3M_INDEX] = pandas.to_numeric(predictions[constants.D3M_INDEX], downcast = 'integer')

    # Join in the ordering and use a right join to drop extra rows.
    predictions = predictions.merge(order_frame, on = constants.D3M_INDEX, how = 'right')

    # Replace missing values.
    if (not increment_missing):
        replacements = dict([(col, missing_value) for col in data_columns])
        predictions.fillna(replacements, inplace = True)
    else:
        value = 0
        if (missing_value is not None):
            value = missing_value

        for data_col in data_columns:
            for i in range(len(predictions)):
                if (pandas.np.isnan(predictions[data_col][i])):
                    predictions.loc[i, data_col] = value
                    value += 1

    # Sort
    predictions.sort_values(by = ['order'], inplace = True)

    # Drop extra columns.
    predictions.drop(columns = ['order'], inplace = True)

    # Reorder columns,
    ordered_columns = data_columns.copy()

    if (constants.CONFIDENCE_COLUMN in ordered_columns):
        ordered_columns.remove(constants.CONFIDENCE_COLUMN)
        ordered_columns.append(constants.CONFIDENCE_COLUMN)

    ordered_columns.insert(0, constants.D3M_INDEX)

    predictions = predictions[ordered_columns]

    # Attach semantic types.
    for i in range(len(ordered_columns)):
        column = ordered_columns[i]

        semantic_type = None
        if (i == 0):
            semantic_type = constants.SEMANTIC_TYPE_PK
        elif (column == constants.CONFIDENCE_COLUMN):
            semantic_type = constants.SEMANTIC_TYPE_CONFIDENCE
        else:
            semantic_type = constants.SEMANTIC_TYPE_TARGET

        predictions.metadata = predictions.metadata.add_semantic_type((meta_base.ALL_ELEMENTS, i), semantic_type)

    return predictions
