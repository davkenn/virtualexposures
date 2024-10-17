import numpy as np
import pytest
from src.astaFilter import AstaFilter

class TestAstaFilter:

  def test_less_pixels_gathered_for_larger_gain_ratios(
              self,frame_window,ones,twos,threes,fours,fives,spatial_kernels):
    assert (AstaFilter.average_temporally_adjacent_pixels(frame_window,spatial_kernels,ones)[1][0].sum() >
              AstaFilter.average_temporally_adjacent_pixels(frame_window, spatial_kernels,twos)[1][0].sum() >
              AstaFilter.average_temporally_adjacent_pixels(frame_window, spatial_kernels, threes)[1][0].sum() >
              AstaFilter.average_temporally_adjacent_pixels(frame_window, spatial_kernels, fours)[1][0].sum() >
              AstaFilter.average_temporally_adjacent_pixels(frame_window, spatial_kernels, fives)[1][0].sum())


  def test_temporal_filter2(self,frame_window,ones,twos,threes,fours,fives,spatial_kernels):
    a = AstaFilter.temporal_filter(frame_window,ones,spatial_kernels)[1].sum()
    b = AstaFilter.temporal_filter(frame_window, twos, spatial_kernels)[1].sum()
    c = AstaFilter.temporal_filter(frame_window, threes, spatial_kernels)[1].sum()
    d = AstaFilter.temporal_filter(frame_window, fours, spatial_kernels)[1].sum()
    e = AstaFilter.temporal_filter(frame_window, fives, spatial_kernels)[1].sum()

    assert a < b < c < d < e

  def test_temporal_filter3(self, frame_window, ones, twos, threes, fours,
                            fives, spatial_kernels):

      a = AstaFilter.temporal_filter(frame_window, ones, spatial_kernels)[1]
      b = AstaFilter.temporal_filter(frame_window, twos, spatial_kernels)[1]
      c = AstaFilter.temporal_filter(frame_window, threes, spatial_kernels)[1]
      d = AstaFilter.temporal_filter(frame_window, fours, spatial_kernels)[1]
      e = AstaFilter.temporal_filter(frame_window, fives, spatial_kernels)[1]

      assert  a.max() < b.max() < c.max() < d.max() <e.max()

  def test_temporal_filter_does_not_alter_argument(self,spatial_kernels,frame_window,fives):
    before = frame_window.get_main_frame()
    _,_ = AstaFilter.temporal_filter(frame_window,fives,spatial_kernels)
    after = frame_window.get_main_frame()
    assert np.array_equal(before,after)


  def test_temporal_filter_result_diff_from_argument(self,spatial_kernels,frame_window,fives):
    before = frame_window.get_main_frame()
    (nums, norms), _ = AstaFilter.temporal_filter(frame_window, fives, spatial_kernels)
    assert not np.array_equal(before[:,:,0], np.round(nums[0]/norms[0]))


  def test_spatial_filter_does_nothing_when_target_met(self,frame_window,all_reached_target):
    before = frame_window.get_main_frame()
    after = AstaFilter.spatial_filter(frame_window.get_main_frame(),all_reached_target)

    assert np.array_equal(before,after)


  def test_spatial_filter_does_something_when_target_not_met(self,frame_window,none_reached_target):
    before = frame_window.get_main_frame()
    after = AstaFilter.spatial_filter(frame_window.get_main_frame(), none_reached_target)
    # i would usually have to round before in spatial filter but not here bc im not performing temporal filter
    assert not np.array_equal(np.round(before), np.round(after))


  def test_asta_filter_does_not_alter_argument(self,asta_filter,frame_window,fives):
    before = frame_window.get_main_frame()
    asta_filter.asta_filter(frame_window,fives)
    after = frame_window.get_main_frame()
    assert np.array_equal(before, after)


  def test_asta_filter_result_diff_from_argument(self, asta_filter, frame_window,
                                               ones):
    before = frame_window.get_main_frame()
    result = asta_filter.asta_filter(frame_window, ones)
    assert not np.array_equal(before, np.round(result))











