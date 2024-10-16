import numpy as np
import pytest
from src.astaFilter import AstaFilter


class TestGaussianSpaceKernels:

  def test_rearrange_moves_right(self, spatial_kernels):
    assert (AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -14)[1.0][0] ==
            AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -13)[1.0][1])


  def test_rearrange_moves_right_two(self, spatial_kernels):
    assert (AstaFilter.rearrange_gaussian_kernels(spatial_kernels, 0)[1.0][len(spatial_kernels) // 2]
            == AstaFilter.rearrange_gaussian_kernels(spatial_kernels, 1)[1.0][(len(spatial_kernels) // 2) + 1])


  def test_rearrange_puts_zeroes_at_the_end_near_first_frames(self, spatial_kernels):
    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, 1)[1.0][0] == 0.0
    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, 14)[1.0][0] == 0.0


  def test_rearrange_puts_zeroes_at_the_end_near_last_frames(self, spatial_kernels):
    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -14)[1.0][len(spatial_kernels) - 1] == 0.0
    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -1)[1.0][len(spatial_kernels) - 2] != 0.0


  def test_spatial_kernels_for_different_gain_ratios_are_all_different(self, spatial_kernels):
    ls = []
    for kernel in spatial_kernels.values():
        ls.append(kernel)
    assert [np.array_equal(ls[i], ls[j]) for i in range(len(ls) - 1) for j in range(i + 1, len(ls))].count(True) == 0


  def test_spatial_kernels_all_sum_to_one(self, spatial_kernels):
    for kernel in spatial_kernels.values():
        assert kernel.sum() == pytest.approx(1.0)
