import numpy as np
import pandas as pd
from numpy.testing import assert_array_equal

from cognite_ml.transformations.cluster_span import ClusterSpanFinder

inp = pd.DataFrame({'num': [.1, .2, .3, 10, 9, 3, 3.5, 4, 4.5, .15],
                    'cluster': [1, 1, 1, 3, 3, 2, 2, 2, 2, 1]})

class TestClassClusterFilter:
    def test_find(self):
        expected = np.array([3, 3, 3, 2, 2, 4, 4, 4, 4, 1])
        csf = ClusterSpanFinder()
        assert_array_equal(csf.fit_transform(inp.cluster), expected)
