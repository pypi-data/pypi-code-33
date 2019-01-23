"""

@author: Johannes Kolberg
"""

import numpy as np
import pandas as pd
from scipy import signal


class TruncatedGaussian:
    """Right-truncated Gaussian signal processing filter to smooth time series values,
    """

    def __init__(self, lookback_window=None, sigma=None, threshold=None):
        """
        :param lookback_window: Number of preceding timestamps to include in the window.
        :param sigma: Standard deviation of the complete Gaussian distribution.
        :param (optional) threshold: Values above are set to 1, those below to 0.
        """
        self.threshold = threshold
        if lookback_window or sigma:
            if lookback_window:
                full_distribution_datapoints = lookback_window * 2 + 1
                sigma = sigma or 0.28 * lookback_window
            else:
                full_n = int((2 / 0.28) * sigma + 1)
                full_distribution_datapoints = full_n if full_n % 2 == 1 else full_n + 1
                lookback_window = int((full_distribution_datapoints - 1) / 2)
            self.kernel = np.array(signal.gaussian(full_distribution_datapoints, sigma))
            self.kernel = self.kernel[0 : lookback_window + 1]
            self.kernel = self.kernel / sum(self.kernel)
        else:
            self.kernel = None

    def fit(self, model_predictions, allowed_flags=0):
        """Fitting kernel to predictions to achieve defined maximum number of flags.
        If the window size or sigma exist, the kernel also does, so it is simply returned.
        Note that this ignores the maximum number of allowed flags.
        If the kernel does not exist, fit it to achieve that condition.

        :param model_predictions: Pandas df where first col predictions, index is timestamps.
        :param allowed_flags: Maximum number of value 1.0 the kernel is allowed to output
        :return: The fitted kernel.
        """

        # Kernel exists if window or sigma was defined, so there's no need to fit
        if self.kernel:
            return self
        # TODO: Raise warning if using default of 0.99
        if not self.threshold:
            self.threshold = 0.99
        # TODO: Set some stopping condition
        lookback = 0
        while True:
            # TODO: Better/more intelligent way of searching for window sizes
            lookback += 10
            if lookback % 50 == 0:
                print("Trying window of {} datapoints".format(lookback))
            kernel = np.array(signal.gaussian(1 + lookback * 2, 0.28 * lookback))
            kernel = kernel[0 : lookback + 1]
            self.kernel = kernel / sum(kernel)
            kernel_flags = self.transform(model_predictions)
            flagged = kernel_flags.iloc[:, 0].sum()
            if flagged <= allowed_flags:
                print("Found window of {} with {} anomalies flagged".format(lookback, flagged))
                break
        return self

    def transform(self, model_predictions):
        """Apply a defined or fitted kernel to a vector of values.

        :param model_predictions: Pandas df where first col predictions, index is timestamps.
        :return: A corresponding Pandas df with the resulting values.
        """
        # Assumes that the input model_predictions has timestamps as index
        kernel_scores = pd.Series(index=model_predictions.index)
        for i in range(len(model_predictions)):
            preds = model_predictions.iloc[:, 0].values[max(0, i + 1 - len(self.kernel)) : i + 1]
            preds = np.pad(preds, (len(self.kernel) - len(preds), 0), "constant")
            score = np.dot(self.kernel, preds)
            kernel_scores.at[model_predictions.index[i]] = score
        # Apply the threshold if it is set, to get binary [0, 1] anomaly flags
        if self.threshold:
            kernel_scores = kernel_scores.apply(lambda y: 1 if y >= self.threshold else 0)
        # Otherwise return the continuous [0, 1] anomaly scores
        return kernel_scores.to_frame(name="kernelScore")
