import pytest
from cognite_ml.metrics import RangeBasedPrecisionRecall


class TestClassRangeBasedPrecisionRecall(object):

    def test_empty_input(self):
        anomaly_labels = []
        predicted_labels = []

        pm = RangeBasedPrecisionRecall(
            anomaly_labels=anomaly_labels,
            predicted_labels=predicted_labels,
            alpha=0.5,
            beta=0.5,
            bias_type="front",
            granularity="10m",
        )
        with pytest.raises(ZeroDivisionError):
            pm.get_recall()

