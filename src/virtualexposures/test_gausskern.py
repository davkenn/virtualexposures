import numpy as np
import pytest

from gausskern import (get_neighborhood_diffs, calc_temp_std_dev_get_kernel,
                       get_kernel_center, intensity_gaussian)




class TestGausskern:

    def test_get_neighborhood_diffs(self):
        j = np.array([[11, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.int32)
        l = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.int32)
        assert get_neighborhood_diffs(j, l)[0,0]==10.0
        assert get_neighborhood_diffs(j, l)[0, 1] == 0.0



    def test_calc_temp_std_dev_get_kernel(self):
        a = calc_temp_std_dev_get_kernel(2.0,4.0)
        b = calc_temp_std_dev_get_kernel(3.0,4.0)
        c = calc_temp_std_dev_get_kernel(6.0, 4.0)
        d = calc_temp_std_dev_get_kernel(7.0, 4.0)

        assert (get_kernel_center(a) > get_kernel_center(b) >
                get_kernel_center(c) > get_kernel_center(d))


    def test_intensity_gaussian_perfect_match(self):
        a = intensity_gaussian(0.0,1.0)
        b = intensity_gaussian(0.0,2.0)
        c = intensity_gaussian(0.0,3.0)
        d = intensity_gaussian(0.0,4.0)

        assert a > b > c > d

    def test_intensity_gaussian_bad_match(self):
        a = intensity_gaussian(5.0,1.0)
        b = intensity_gaussian(5.0,2.0)
        c = intensity_gaussian(5.0,3.0)
        d = intensity_gaussian(5.0,4.0)

        assert a < b < c < d

    def test_intensity_gaussian_edges(self):
        a = intensity_gaussian(4.0, 4.0)
        b = intensity_gaussian(5.0, 4.0)
        c = intensity_gaussian(6.0, 4.0)
        d = intensity_gaussian(7.0, 4.0)

        assert a > b > c > d

    def test_intensity_gaussian_edges(self):
        a = intensity_gaussian(4.0, 4.0)
        b = intensity_gaussian(5.0, 4.0)
        c = intensity_gaussian(6.0, 4.0)
        d = intensity_gaussian(7.0, 4.0)

        assert a > b > c > d




