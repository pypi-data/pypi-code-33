"""

@author: Johannes Kolberg
"""

import pandas as pd


def anomaly_ranges(anomaly_flags, threshold=None):
    """Finds the time ranges with continuous values of 1.0.
    Applies a threshold if specified, e.g. if inputs are continuous.

    :param anomaly_flags: Pandas df where first col predictions, index is timestamps.
    :param (optional) threshold: Values above are set to 1, those below to 0.
    :return: List of tuples with start and end timestamps of anomalous ranges in time.
    """
    if threshold:
        anomaly_flags.iloc[:, 0] = anomaly_flags.iloc[:, 0].apply(lambda y: 1 if y >= threshold else 0)

    anom_groups = anomaly_flags.iloc[:, 0].to_frame(name="anomaly")
    anom_groups["value_grp"] = (anom_groups.anomaly.diff(1) != 0).astype("int").cumsum()
    anom_groups["timestamp"] = anom_groups.index.values

    flag_ranges = pd.DataFrame(
        {
            "Begin": anom_groups.groupby("value_grp").timestamp.first(),
            "End": anom_groups.groupby("value_grp").timestamp.last(),
            "Consecutive": anom_groups.groupby("value_grp").size(),
            "anomaly": anom_groups.groupby("value_grp").anomaly.first(),
        }
    ).reset_index(drop=True)

    anom_ranges = []
    for index, _ in flag_ranges[flag_ranges.anomaly == 1].iterrows():
        anom_ranges.append((flag_ranges.Begin[index], flag_ranges.End[index]))

    return anom_ranges
