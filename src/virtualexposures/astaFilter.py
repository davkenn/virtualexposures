from __future__ import division

from inspect import currentframe

import cv2
import numpy as np
from numpy.random import normal

from gausskern import get_neighborhood_diffs,calc_temp_std_dev_get_kernel
from gausskern import intensity_gaussian
from scipy import stats


def asta_filter(frame_window, targets):
  """Takes as argument a frame_window which has the current video frame and its
  surrounding frames.  The targetnums argument is a 2d array containing the
  target number of pixels to combine for each pixel in the frame. The function
  first runs the temporal filter to average the values of each pixel across
  time.  Then, for each pixel, it will run the spatial filter for that pixel at
  a strength inversely proportional to how many pixels could be combined with
  the temporal filter.  Finally, it returns a 2d array of all the pixels
  for a given video frame calculated by this filter"""

  frame = frame_window.get_main_frame()

  (numerators, normalizers), short_of_target = temporal_filter(frame_window,
                                                               targets, 92)


  output = np.copy(frame)
  output[:, :, 0] = numerators / normalizers
  
  result_frame = spatial_filter(output, short_of_target)

  return result_frame


def temporal_filter(frame_window, target_numbers, max_error):
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

  intensity_sigma = 4.0
  kernel_dict = make_gaussian_kernels(frame_window,intensity_sigma)
  filter_keys = get_nearest_filter_keys(target_numbers)

  # calculate how short we are in the number of pixels we could average to
  # determine how much to use spatial filter
  ideal_weight = np.ones_like(filter_keys)

 # ls = get_weights_list(frame_window.curr_frame_index, kernel_dict)

  f = np.vectorize(lambda x: kernel_dict[x].item(frame_window.curr_frame_index))
  e = f(filter_keys)

  ideal_weight *= e
  ideal_weight *= intensity_gaussian(0, 4.0)
  ideal_weight *= filter_keys

  numerators, normalizers = average_temporally_adjacent_pixels(
                            frame_window,
                            kernel_dict,
                            filter_keys,
                            max_error
  )

  distances_short_of_target = ideal_weight - normalizers
  print distances_short_of_target.min(),distances_short_of_target.max(),stats.mode(distances_short_of_target,
                   axis=None),np.average(distances_short_of_target)
#   print normalizers.min(), normalizers.max(), stats.mode(normalizers,axis= None),np.average(normalizers)

#also think if you should compare the denom sizes after you just changed the kernel to super big. see if it gathered more weight before

  return (numerators, normalizers), distances_short_of_target


def spatial_filter(temp_filtered_frame, distances_short_of_targets):
  """This function chooses a final pixel value with either no
  spatial filtering, or varying degrees of spatial filtering depending
  on how short the temporal filter came to gathering enough pixels"""
  return temp_filtered_frame
 
  #TODO: add a median filtering step before bilateral filter step

#  some_filtering = cv2.bilateralFilter(
 #                      temp_filtered_frame,
  #                  11,
   #          41,
   #         21
 # )


  some_filtering = cv2.bilateralFilter(
                       temp_filtered_frame,
                    15,
             141,
            81
  )

#  lots_filtering = cv2.bilateralFilter(
 #                      temp_filtered_frame,
  #                  9,
   #          150,
    #        150
  #)

  #need three channels of distances because spatial filter done on all 3  
  dists_short = np.repeat(
                   distances_short_of_targets[:,:,np.newaxis],
            3,
                   axis=2
  )
  #this is used as a cutoff for spots where no further filtering required
  min_values = np.zeros_like(dists_short)
  min_values.fill(0.0)

  middles = np.zeros_like(dists_short)
  middles.fill(0.02)
  a1= np.less(dists_short,min_values)
  filla =np.where(a1, temp_filtered_frame, some_filtering)

  greater_than_zeros = np.greater_equal(dists_short,min_values)
  less_than_highs = np.less(dists_short,middles)
  a_little_short_elems = np.logical_and(greater_than_zeros,less_than_highs)

  some_space_filter_vals_added = np.where(a_little_short_elems,some_filtering,temp_filtered_frame)

  a_lot_short_elems = np.greater_equal(dists_short,middles)

  lots_space_filter_vals_added = np.where(
                                    a_lot_short_elems,
                                    lots_filtering,
                                    some_space_filter_vals_added
  )

  #return lots_space_filter_vals_added
  return filla

def average_temporally_adjacent_pixels(
    frame_window,
    kernel_dict,
    filter_keys,
    max_error
):

  numerators, normalizers = np.zeros_like(filter_keys), np.zeros_like(filter_keys)

  frame = frame_window.get_main_frame()

  for i in xrange(0,frame_window.get_length()):

    other_frame = frame_window.frame_list[i]
    curr_gauss_weights = get_weights_list(i, kernel_dict)
    frame_distance_weights = np.copy(filter_keys)

    make_weights_array(frame_distance_weights, curr_gauss_weights) #in-place change

    pixel_distance_weights = get_neighborhood_diffs(
                             frame[:,:,0],
                             other_frame[:,:,0],
                      2,
                             6
    )

    intensity_weights = intensity_gaussian(pixel_distance_weights, 4.0)
    total_gaussian_weights = intensity_weights * frame_distance_weights

    numerators += total_gaussian_weights * other_frame[:,:,0]
    normalizers += total_gaussian_weights

  return numerators, normalizers


def make_gaussian_kernels(frame_window,intesity_sigma):

    kernel_keys = [] 
    all_kernels = []
 
    for i in xrange(0,20):  #builds 1-d gaussian kernels of length equal to frame window size
      kernel_keys.append(i/2)  #with std. devs between .5 and 9.5
      all_kernels.append(
                  calc_temp_std_dev_get_kernel(i / 2,intesity_sigma)
      )
#maybe move this to the framequeue class
    if frame_window.is_frame_at_edges() != 0: #if near begin or end of video
      all_kernels = rearrange_gaussian_kernels(
                    all_kernels,
                    frame_window.is_frame_at_edges()
      )
   
    return dict(zip(kernel_keys,all_kernels))


def rearrange_gaussian_kernels(all_kernels, distance_off_center):
  """This function is called when the window of surrounding frames
  needed to process a frame is too large to symmetrically take the same
  number of frames from before and after the current frame.  This function
  will rearrange the gaussian kernel in these situations so that the weight
  of each frame still decreases with temporal distance from the current frame."""
 
  resorted_kernels = []
  
  if distance_off_center == 0:
    return all_kernels

  for kernel in all_kernels:

    zero_frames = np.array([[0.0]] * abs(distance_off_center))

    if distance_off_center < 0: #frame is near beginning of video
      kernel = np.concatenate([kernel[-distance_off_center:],zero_frames])

    elif distance_off_center > 0: #frame i/s near end of video
      kernel = np.concatenate([zero_frames, kernel[:-distance_off_center]])

    resorted_kernels.append(np.array(kernel))

  return resorted_kernels


def get_weights_list(index, kernel_dict):
  """This function will return the gaussian distance weights based on index,
  which is both the frame number in the queue and the index to the proper
  gaussian weight"""
  weights_list = []
  #go through dict in order
  for key in sorted(kernel_dict.iterkeys()):
    weights_list.append(kernel_dict[key].item(index))

  return weights_list


def make_weights_array(filter_keys, weights_list):
  """Takes a numpy array of equal dimension to the pixel lum array filled with
  values of about how many pixels need to be combined at each pixel
  (filter_keys).  Associates these with the correct elements in weights_list
  which holds the gaussian weights for the different filter_keys.  Will return
  a numpy array of pixel lum size with values of spatial gaussian weights"""
#what about my filter key 9.5? why are these diff lengths
  filter_keys[filter_keys > 8.6] = weights_list[16] #9.0 weight
  filter_keys[filter_keys > 8.1] = weights_list[15] #8.5 weight
  filter_keys[filter_keys > 7.6] = weights_list[14] #8.0 weight
  filter_keys[filter_keys > 7.1] = weights_list[13] #7.5 weight
  filter_keys[filter_keys > 6.6] = weights_list[12] #7.0 weight
  filter_keys[filter_keys > 6.1] = weights_list[11] #6.5 weight
  filter_keys[filter_keys > 5.6] = weights_list[10] #6.0 weight
  filter_keys[filter_keys > 5.1] = weights_list[9] #5.5 weight
  filter_keys[filter_keys > 4.6] = weights_list[8] #5.0 weight
  filter_keys[filter_keys > 4.1] = weights_list[7] #4.5 weight
  filter_keys[filter_keys > 3.6] = weights_list[6] #4.0 weight
  filter_keys[filter_keys > 3.1] = weights_list[5] #3.5 weight
  filter_keys[filter_keys > 2.6] = weights_list[4] #3.0 weight
  filter_keys[filter_keys > 2.1] = weights_list[3] #2.5 weight
  filter_keys[filter_keys > 1.6] = weights_list[2] #2.0 weight
  filter_keys[filter_keys > 1.1] = weights_list[1] #1.5 weight
  filter_keys[filter_keys == 1.0] = weights_list[0] #1.0 weight

  return filter_keys


def get_nearest_filter_keys(target_nums):
  """Keys in the filter dict are at 1, 1.5, 2, etc..."""
  return np.round(target_nums * 2) / 2
  
