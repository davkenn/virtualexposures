from __future__ import division
from inspect import currentframe
from numpy.random import normal
from gausskern import get_neighborhood_diffs,get_kernel_with_dynamic_std_dev
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
    ideal_weight *= intensity_gaussian(0, 2.5)
    ideal_weight *= rounded_targets

    numerators, normalizers = AstaFilter.average_temporally_adjacent_pixels(
                                         frame_window,
                                         gaussian_space_kernels,
                                         rounded_targets
    )
    print rounded_targets.max(),rounded_targets.min()
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
    # return temp_filtered_frame
    # TODO: add a median filtering step before bilateral filter step

    some_filtering = cv2.bilateralFilter(
      temp_filtered_frame.astype(np.float32),
      5,
      35,
      35
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

    for i in xrange(2,20):  # builds 1-d gaussian kernels of length equal to frame window size
      kernel_keys.append(i / 2)  # with std. devs between .5 and 9.5
      all_kernels.append(
        get_kernel_with_dynamic_std_dev(i / 2, intensity_sigma)
      )

    return dict(zip(kernel_keys, all_kernels))

  @staticmethod
  def average_temporally_adjacent_pixels(
            frame_window,
            gaussian_space_kernels,
            rounded_targets
  ):

    numerators = np.zeros_like(rounded_targets)
    normalizers= np.zeros_like(rounded_targets)

    frame = frame_window.get_main_frame()

    for i in xrange(0, frame_window.get_length()):

      other_frame = frame_window.frame_list[i]

      curr_gauss_weights = get_weights_list(i, gaussian_space_kernels)

      space_distance_weights = make_weights_array(
                              np.copy(rounded_targets),
                              curr_gauss_weights
      )

      intensity_distances = get_neighborhood_diffs(
                               frame[:, :, 0],
                               other_frame[:, :, 0]
      )

      intensity_weights = intensity_gaussian(intensity_distances, 2.5)
      total_gaussian_weights = space_distance_weights * intensity_weights

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
    copy = dict(gaussian_space_kernels)
    if distance_off_center == 0:
      return copy

    for key in gaussian_space_kernels:
    #  zero_frames = np.array([[0.0] * abs(distance_off_center)])
      zero_frames = np.array([[0.0]] * abs(distance_off_center))

      if distance_off_center < 0:  # frame is near beginning of video

        copy[key] = (
          np.concatenate(
            [
              gaussian_space_kernels[key][-distance_off_center:],
              zero_frames
            ]
          )
        )

      elif distance_off_center > 0:  # frame i/s near end of video

        copy[key] = (
          np.concatenate(
            [
              zero_frames,
              gaussian_space_kernels[key][:-distance_off_center]

            ]
          )
        )

    return copy


def get_weights_list(index, kernel_dict):
  """This function returns the gaussian distance weights based on frame index,
  which is both the frame index in the frame queue and the index to the proper
  gaussian weight"""
  weights_list = []
  #go through dict in order
  for key in sorted(kernel_dict.iterkeys()):
    weights_list.append(kernel_dict[key].item(index))

  return weights_list


def make_weights_array(rounded_targets, weights_list):
  """Takes a numpy array of equal dimension to the pixel lum array filled with
  values of about how many pixels need to be combined at each pixel
  (filter_keys).  Associates these with the correct elements in weights_list
  which holds the gaussian weights for the different filter_keys.  Will return
  a numpy array of pixel lum size with values of spatial gaussian weights"""
#what about my filter key 9.5? why are these diff lengths
  rounded_targets[rounded_targets > 8.6] = weights_list[16] #9.0 weight
  rounded_targets[rounded_targets > 8.1] = weights_list[15] #8.5 weight
  rounded_targets[rounded_targets > 7.6] = weights_list[14] #8.0 weight
  rounded_targets[rounded_targets > 7.1] = weights_list[13] #7.5 weight
  rounded_targets[rounded_targets > 6.6] = weights_list[12] #7.0 weight
  rounded_targets[rounded_targets > 6.1] = weights_list[11] #6.5 weight
  rounded_targets[rounded_targets > 5.6] = weights_list[10] #6.0 weight
  rounded_targets[rounded_targets > 5.1] = weights_list[9] #5.5 weight
  rounded_targets[rounded_targets > 4.6] = weights_list[8] #5.0 weight
  rounded_targets[rounded_targets > 4.1] = weights_list[7] #4.5 weight
  rounded_targets[rounded_targets > 3.6] = weights_list[6] #4.0 weight
  rounded_targets[rounded_targets > 3.1] = weights_list[5] #3.5 weight
  rounded_targets[rounded_targets > 2.6] = weights_list[4] #3.0 weight
  rounded_targets[rounded_targets > 2.1] = weights_list[3] #2.5 weight
  rounded_targets[rounded_targets > 1.6] = weights_list[2] #2.0 weight
  rounded_targets[rounded_targets > 1.1] = weights_list[1] #1.5 weight
  rounded_targets[rounded_targets == 1.0] = weights_list[0] #1.0 weight

  return rounded_targets

def get_nearest_dict_keys(target_nums):
  """Keys in the filter dict are at 1, 1.5, 2, etc..."""
  return np.round(target_nums * 2) / 2
  
