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



    def test_calc_temp_std_dev_get_kernel(self,target_num=2.0):
        a =gausskern.calc_temp_std_dev_get_kernel(2.0,4.0)
        b = gausskern.calc_temp_std_dev_get_kernel(3.0,4.0)
        c = gausskern.calc_temp_std_dev_get_kernel(6.0, 4.0)
        d = gausskern.calc_temp_std_dev_get_kernel(7.0, 4.0)

        assert (gausskern.get_kernel_center(a) > gausskern.get_kernel_center(b) >
                gausskern.get_kernel_center(c) > gausskern.get_kernel_center(d))
