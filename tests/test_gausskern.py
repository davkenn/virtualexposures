import numpy as np
import pytest

from gausskern import (get_neigh_diffs, get_kernel_with_dynamic_std_dev,
                       get_kernel_center, intensity_gaussian,
                       _intensity_gaussian)




class TestGausskern:

    def test_get_neighborhood_diffs(self):
        j = np.array([[11, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.int32)
        l = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.int32)
        assert get_neigh_diffs(j, l)[0,0] == 10.0
        assert get_neigh_diffs(j, l)[0, 1] == 0.0


    def test_calc_temp_std_dev_get_kernel(self):
        a = get_kernel_with_dynamic_std_dev(2.0, 21)
        b = get_kernel_with_dynamic_std_dev(3.0, 21)
        c = get_kernel_with_dynamic_std_dev(6.0, 21)
        d = get_kernel_with_dynamic_std_dev(7.0, 21)

        assert (get_kernel_center(a) > get_kernel_center(b) >
                get_kernel_center(c) > get_kernel_center(d))


    def test_intensity_gaussian_perfect_match(self):
        a = _intensity_gaussian(0.0,1.0)
        b = _intensity_gaussian(0.0,2.0)
        c = _intensity_gaussian(0.0,3.0)
        d = _intensity_gaussian(0.0,4.0)

        assert a > b > c > d

    def test_intensity_gaussian_bad_match(self):
        a = _intensity_gaussian(5.0,1.0)
        b = _intensity_gaussian(5.0,2.0)
        c = _intensity_gaussian(5.0,3.0)
        d = _intensity_gaussian(5.0,4.0)

        assert a < b < c < d

    def test_intensity_gaussian_edges(self):
        a = intensity_gaussian(4.0)
        b = intensity_gaussian(5.0)
        c = intensity_gaussian(6.0)
        d = intensity_gaussian(7.0)

        assert a > b > c > d






