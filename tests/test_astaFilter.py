import numpy as np
import pytest
from src.astaFilter import AstaFilter
from src.frameQueueClasses import FrameQueue


class TestAstaFilter:

  @pytest.fixture
  def spatial_kernels(self):
    """This fixture will only be available within the scope of TestGroup"""
    return AstaFilter.make_gaussian_kernels(41)


  @pytest.fixture
  def frame_window(self):
    a = FrameQueue("data/1110347515-preview.mp4", 41)
    b = a.get_next_frame()
    while b.is_frame_at_edges()!= 0:
      b = a.get_next_frame()
      print b.is_frame_at_edges()

    return b


  @pytest.fixture
  def pixel_targets(self,frame_window):
    return np.ones_like(frame_window.get_main_frame()[:,:,0])

  @pytest.fixture
  def ones(self, frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0], 1.0)

  @pytest.fixture
  def twos(self, frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0],2.0)

  @pytest.fixture
  def threes(self, frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0],3.0)

  @pytest.fixture
  def fours(self, frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0], 4.0)

  @pytest.fixture
  def fives(self, frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0], 5.0)

  def test_temporal_filter(self,frame_window,ones,fives,spatial_kernels):
    assert (AstaFilter.average_temporally_adjacent_pixels(frame_window,spatial_kernels,ones)[1].sum() >
             AstaFilter.average_temporally_adjacent_pixels(frame_window, spatial_kernels,fives)[1].sum())


  def test_temporal_filter2(self,frame_window,ones,twos,threes,fours,fives,spatial_kernels):
  #  a = AstaFilter.temporal_filter(frame_window,ones,spatial_kernels)[1].sum()
    b = AstaFilter.temporal_filter(frame_window, twos, spatial_kernels)[
      1].sum()
    c = AstaFilter.temporal_filter(frame_window, threes, spatial_kernels)[
      1].sum()
    d = AstaFilter.temporal_filter(frame_window, fours, spatial_kernels)[
      1].sum()
    e = AstaFilter.temporal_filter(frame_window, fives, spatial_kernels)[
      1].sum()

    assert  b > c > d > e

  def test_temporal_filter3(self, frame_window, ones, twos, threes, fours,
                            fives, spatial_kernels):

      a = AstaFilter.temporal_filter(frame_window, ones, spatial_kernels)[
        1]

      b = AstaFilter.temporal_filter(frame_window, twos, spatial_kernels)[
        1]

      c = AstaFilter.temporal_filter(frame_window, threes, spatial_kernels)[
        1]
      d = AstaFilter.temporal_filter(frame_window, fours, spatial_kernels)[
        1]
      e = AstaFilter.temporal_filter(frame_window, fives, spatial_kernels)[
        1]


      assert  a.max() > b.max() < c.max() < d.max() #> np.median(e)

  def test_rearrange_moves_right(self,spatial_kernels):
    assert (AstaFilter.rearrange_gaussian_kernels(spatial_kernels,-14)[1.0][0]
        == AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -13)[1.0][1])

  def test_rearrange_moves_right_two(self,spatial_kernels):
    assert (AstaFilter.rearrange_gaussian_kernels(spatial_kernels,0)[1.0][len(spatial_kernels)//2]
    == AstaFilter.rearrange_gaussian_kernels(spatial_kernels, 1)[1.0][(len(spatial_kernels)//2)+1])

  def test_rearrange_puts_zeroes_at_the_end_near_first_frames(self,spatial_kernels):

    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels,1)[1.0][0] == 0.0
    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, 14)[1.0][0] == 0.0

  def test_rearrange_puts_zeroes_at_the_end_near_last_frames(self,spatial_kernels):

    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -14)[1.0][len(spatial_kernels)-1] == 0.0
    assert AstaFilter.rearrange_gaussian_kernels(spatial_kernels, -1)[1.0][len(spatial_kernels) - 2] != 0.0









