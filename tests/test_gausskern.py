import numpy as np
import pytest

import gausskern

class TestGausskern:

    def test_get_neighborhood_diffs(self):
        j = np.array([[11, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.int32)
        l = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.int32)
        print gausskern.get_neighborhood_diffs(j, l, 2, 5)
    #    assert gausskern.get_neighborhood_diffs(j, l, 2, 5)[0,0]==0.0
     #   assert gausskern.get_neighborhood_diffs(j, l, 2, 7)[0, 1] == 1.0

    def test_distance_metric(self):
        k = np.array([[1.0, 1.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
        res = np.array([[1.0,1.0,0.83333333],[0.66666667, 0.5, 0.33333333],[0.16666667, 0.0, 0.0]])

        assert gausskern.distance_metric(k, 2, 8)[0][2] == pytest.approx(0.83333333)