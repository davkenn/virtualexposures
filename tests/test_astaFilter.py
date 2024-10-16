import numpy as np
import pytest
from src.astaFilter import AstaFilter
from src.frameQueueClasses import FrameQueue



class TestAstaFilter:


  def test_less_pixels_gathered_for_larger_gain_ratios(
              self,frame_window,ones,twos,threes,fours,fives,spatial_kernels):
    assert (AstaFilter.average_temporally_adjacent_pixels(frame_window,spatial_kernels,ones)[1].sum() >
              AstaFilter.average_temporally_adjacent_pixels(frame_window, spatial_kernels,twos)[1].sum() >
              AstaFilter.average_temporally_adjacent_pixels(frame_window, spatial_kernels, threes)[1].sum() >
              AstaFilter.average_temporally_adjacent_pixels(frame_window, spatial_kernels, fours)[1].sum() >
              AstaFilter.average_temporally_adjacent_pixels(frame_window, spatial_kernels, fives)[1].sum())


  def test_temporal_filter2(self,frame_window,ones,twos,threes,fours,fives,spatial_kernels):
    a = AstaFilter.temporal_filter(frame_window,ones,spatial_kernels)[1].sum()
    b = AstaFilter.temporal_filter(frame_window, twos, spatial_kernels)[1].sum()
    c = AstaFilter.temporal_filter(frame_window, threes, spatial_kernels)[1].sum()
    d = AstaFilter.temporal_filter(frame_window, fours, spatial_kernels)[1].sum()
    e = AstaFilter.temporal_filter(frame_window, fives, spatial_kernels)[1].sum()

    assert a < b < c < d < e

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


      assert  a.max() < b.max() < c.max() < d.max() <e.max()

  def test_temporal_filter_does_not_alter_argument(self,spatial_kernels,frame_window,fives):
    before = frame_window.get_main_frame()
    _,_ = AstaFilter.temporal_filter(frame_window,fives,spatial_kernels)
    after = frame_window.get_main_frame()
    assert np.array_equal(before,after)


  def test_temporal_filter_result_diff_from_argument(self,spatial_kernels,frame_window,fives):
    before = frame_window.get_main_frame()
    (nums, norms), _ = AstaFilter.temporal_filter(frame_window, fives, spatial_kernels)

    result = np.round(nums / norms)
    assert not np.array_equal(before[:,:,0], result)


  def test_spatial_filter_does_nothing_when_target_met(self,frame_window,all_reached_target):
    before = frame_window.get_main_frame()
    after = AstaFilter.spatial_filter(frame_window.get_main_frame(),all_reached_target)

    assert np.array_equal(before,after)


  def test_spatial_filter_does_something_when_target_not_met(self,frame_window,none_reached_target):
    before = frame_window.get_main_frame()
    after = AstaFilter.spatial_filter(frame_window.get_main_frame(), none_reached_target)

    assert not np.array_equal(before, after)



  def test_asta_filter_does_not_alter_argument(self,asta_filter,frame_window,fives):
    before = frame_window.get_main_frame()
    asta_filter.asta_filter(frame_window,fives)
    after = frame_window.get_main_frame()
    assert np.array_equal(before, after)

  def test_asta_filter_result_diff_from_argument(self, asta_filter, frame_window,
                                               ones):
    before = frame_window.get_main_frame()
    result = asta_filter.asta_filter(frame_window, ones)
    result = np.round(result)

    assert not np.array_equal(before, result)

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









