from __future__ import division
from inspect import currentframe
from numpy.random import normal
from gausskern import get_neighborhood_diffs,calc_temp_std_dev_get_kernel
from gausskern import intensity_gaussian
from scipy import stats
import cv2
import sys
import numpy as np
from functools import partial
from tonemap import find_target_luminance,tonemap_spatially_uniform


class AstaFilter(object):
  """Surrounding frame count is the number of frames counting itself.
   Probably need a diff number of surrounding frames for each frame  but
   the best thing to do is probably just overestimate and use less if need be"""
  def __init__(self,intensity_sigma):

    self.gaussian_space_kernels = self.make_gaussian_kernels(intensity_sigma)
    self.intensity_sigma = intensity_sigma
    self.gaussian_intensity_kernel = partial(
                                     intensity_gaussian,
                                     sigma = intensity_sigma,

    )


  def asta_filter(self, frame_window,pixel_targets):
    """Takes as argument a frame_window which has the current video frame and its
    surrounding frames.  The targetnums argument is a 2d array containing the
    target number of pixels to combine for each pixel in the frame. The function
    first runs the temporal filter to average the values of each pixel across
    time.  Then, for each pixel, it will run the spatial filter for that pixel at
    a strength inversely proportional to how many pixels could be combined with
    the temporal filter.  Finally, it returns a 2d array of all the pixels
    for a given video frame calculated by this filter"""

    output_1 = np.copy(frame_window.get_main_frame())

    (numerators, normalizers), short_of_target = AstaFilter.temporal_filter(
                                                 frame_window,
                                                 pixel_targets,
                                                 self.gaussian_space_kernels
    )

    output_1[:, :, 0] = numerators / normalizers
  
    output_2 = AstaFilter.spatial_filter(output_1, short_of_target)

    return output_2


  @staticmethod
  def temporal_filter(frame_window, pixel_targets, gaussian_space_kernels):
    """This function averages the current frame pixel intensity values with the
    values of the same pixel in surrounding frames.  It takes a gaussian average
    of these nearby pixels with weight decreasing with temporal distance from
    current frame being processed.  It will only take nearby pixels with similar
    neighborhoods and ignore those with very different neighborhoods.  It takes
    as argument (1) the window of surrounding frames, (2) a 2d targetnums array
    with the approximate number of pixels that must be averaged at each pixel
    and (3) a max_error which determines how similar temporally adjacent frames
    must be for them to be included in the average of nearby pixels.  This
    function returns both the temporally averaged pixel values and how short we
   were from combining enough pixels at each location with this temporal step."""

    gaussian_space_kernels = AstaFilter.rearrange_gaussian_kernels(
                                        gaussian_space_kernels,
                                        frame_window.is_frame_at_edges()
    )
    # calculate how short we are in the number of pixels we could average to
    # determine how much to use spatial filter
    rounded_targets = get_nearest_dict_keys(pixel_targets)

    get_space_kernel = np.vectorize(
           lambda x:
             gaussian_space_kernels[x].item(frame_window.curr_frame_index)
    )
    space_kernel = get_space_kernel(rounded_targets)

    ideal_weight = np.ones_like(rounded_targets)

    ideal_weight *= space_kernel
    ideal_weight *= intensity_gaussian(0, 4.0)
    ideal_weight *= rounded_targets

    numerators, normalizers = AstaFilter.average_temporally_adjacent_pixels(
                                         frame_window,
                                         gaussian_space_kernels,
                                         rounded_targets
    )

    distances_short_of_target = ideal_weight - normalizers
    print distances_short_of_target.min(),distances_short_of_target.max(),stats.mode(distances_short_of_target,axis=None),np.average(distances_short_of_target)
    print normalizers.min(), normalizers.max(), stats.mode(normalizers,axis=None), np.average(normalizers)

    # also think if you should compare the denom sizes after you just changed the kernel to super big. see if it gathered more weight before

    return (numerators, normalizers), distances_short_of_target


  @staticmethod
  def spatial_filter(temp_filtered_frame, distances_short_of_targets):
    """This function chooses a final pixel value with either no
    spatial filtering, or varying degrees of spatial filtering depending
    on how short the temporal filter came to gathering enough pixels"""
    print "CALLED"
    # return temp_filtered_frame
    # TODO: add a median filtering step before bilateral filter step

    some_filtering = cv2.bilateralFilter(
      temp_filtered_frame.astype(np.float32),
      5,
      15,
      15
    )

    #  lots_filtering = cv2.bilateralFilter(
    #                      temp_filtered_frame,
    #                  9,
    #          150,
    #        150
    # )

    # need three channels of distances because spatial filter done on all 3
    dists_short = np.repeat(
      distances_short_of_targets[:, :, np.newaxis],
      3,
      axis=2
    )
    # this is used as a cutoff for spots where no further filtering required
    min_values = np.zeros_like(dists_short)
    min_values.fill(0.0)

    middles = np.zeros_like(dists_short)
    middles.fill(0.02)
    a1 = np.less(dists_short, min_values)
    filla = np.where(a1, temp_filtered_frame, some_filtering)

    greater_than_zeros = np.greater_equal(dists_short, min_values)
    less_than_highs = np.less(dists_short, middles)
    a_little_short_elems = np.logical_and(greater_than_zeros, less_than_highs)

    some_space_filter_vals_added = np.where(a_little_short_elems,
                                            some_filtering,
                                            temp_filtered_frame)

    a_lot_short_elems = np.greater_equal(dists_short, middles)

    #  lots_space_filter_vals_added = np.where(
    #                                   a_lot_short_elems,
    #                                  lots_filtering,
    #                                 some_space_filter_vals_added
    #  )

    # return lots_space_filter_vals_added
    return filla


  @staticmethod
  def make_gaussian_kernels(intensity_sigma):

    kernel_keys = []
    all_kernels = []

    for i in xrange(0,20):  # builds 1-d gaussian kernels of length equal to frame window size
      kernel_keys.append(i / 2)  # with std. devs between .5 and 9.5
      all_kernels.append(
        calc_temp_std_dev_get_kernel(i / 2, intensity_sigma)
      )

    return dict(zip(kernel_keys, all_kernels))

  @staticmethod
  def average_temporally_adjacent_pixels(
            frame_window,
            gaussian_space_kernels,
            rounded_targets
  ):

    numerators, normalizers = np.zeros_like(rounded_targets), np.zeros_like(rounded_targets)

    frame = frame_window.get_main_frame()

    for i in xrange(0, frame_window.get_length()):
      other_frame = frame_window.frame_list[i]

      p = np.vectorize( lambda x : gaussian_space_kernels[x][i])

      frame_distance_weights = p(rounded_targets)

      pixel_distance_weights = get_neighborhood_diffs(
                               frame[:, :, 0],
                               other_frame[:, :, 0]
      )

      intensity_weights = intensity_gaussian(pixel_distance_weights, 4.0)
      total_gaussian_weights = frame_distance_weights * intensity_weights

      numerators += total_gaussian_weights * other_frame[:, :, 0]
      normalizers += total_gaussian_weights

    return numerators, normalizers


  @staticmethod
  def rearrange_gaussian_kernels(gaussian_space_kernels,distance_off_center):
    """This function is called when the window of surrounding frames
    needed to process a frame is too large to symmetrically take the same
    number of frames from before and after the current frame.  This function
    will rearrange the gaussian kernel in these situations so that the weight
    of each frame still decreases with temporal distance from the current frame."""

    if distance_off_center == 0:
      return gaussian_space_kernels

    for key in gaussian_space_kernels:
   #   zero_frames = np.array([[0.0] * abs(distance_off_center)])
      zero_frames = np.array([[0.0]] * abs(distance_off_center))

      if distance_off_center < 0:  # frame is near beginning of video

        gaussian_space_kernels[key] = (
          np.concatenate(
            [
              gaussian_space_kernels[key][-distance_off_center:],
              zero_frames
            ]
          )
        )

      elif distance_off_center > 0:  # frame i/s near end of video

        gaussian_space_kernels[key] = (
          np.concatenate(
            [
              zero_frames,
              gaussian_space_kernels[key][:-distance_off_center]

            ]
          )
        )

    return gaussian_space_kernels


def get_nearest_dict_keys(target_nums):
  """Keys in the filter dict are at 1, 1.5, 2, etc..."""
  return np.round(target_nums * 2) / 2
  
