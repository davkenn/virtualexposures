import pytest
from astaFilter import AstaFilter
from src.virtualexposures.gausskern import intensity_gaussian


class TestAstaFilter:
  @pytest.fixture
  def spatial_kernels(self):
    """This fixture will only be available within the scope of TestGroup"""
    return AstaFilter.make_gaussian_kernels()

  def test_rearrange_moves_right(self,spatial_kernels):
    assert (AstaFilter.rearrange_gaussian_kernels(spatial_kernels,-14)[0][0]
        == AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -13)[0][1])

  def test_rearrange_moves_right_two(self,spatial_kernels):
    assert (AstaFilter.rearrange_gaussian_kernels(spatial_kernels,0)[0][len(spatial_kernels)//2]
    == AstaFilter.rearrange_gaussian_kernels(spatial_kernels, 1)[0][(len(spatial_kernels)//2)+1])

  def test_rearrange_puts_zeroes_at_the_end_near_first_frames(self,spatial_kernels):

    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels,1)[1][0] == 0.0
    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, 14)[1][0] == 0.0

  def test_rearrange_puts_zeroes_at_the_end_near_last_frames(self,spatial_kernels):

    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -14)[1][len(spatial_kernels)-1] == 0.0
    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -1)[1][len(spatial_kernels) - 2] != 0.0









