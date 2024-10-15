from __future__ import division
import cv2
import numpy as np
from math import log10


def find_target_luminance(vid_frame):
  throwaway_copy = np.copy(vid_frame[:,:,0])
  throwaway_blurred = cv2.GaussianBlur(throwaway_copy,(5,5),0)
  result = _tone_map_vectorized(throwaway_blurred, 34)

  result *= 255

 # return divide_if_nonzero_vec(result, vid_frame[:, :, 0]) #bug
  return _divide_if_nonzero_vectorized(result, throwaway_blurred)


def tonemap_spatially_uniform(vid_frame):
  #is this changing things in place?
  result = np.copy(vid_frame)
  result[:,:,2] = _tone_map_vectorized(vid_frame[:,:,2], 34)
  result[:,:,2] *= 255
  return result


def _tone_map(pixel_lum, attenuation):
  """Takes as argument an input pixel luminance and maps it to an output pixel
   luminance. """
  ratio = pixel_lum / 255.0 #255 is max luminance
  num = log10(ratio * (attenuation - 1) + 1)
  denom = log10(attenuation)
  return num / denom


def _tone_map_vectorized(vid_frame, attenuation):
  tone_map_vector_function = np.vectorize(_tone_map)
  return tone_map_vector_function(vid_frame,attenuation)


def _divide_if_nonzero(num, denom):
  #where the start and end luminances are both 1
  if denom == 0.0 and num == 0.0:
    return 1.0
  elif denom == 0.0:
    return num
  else:
    return num / denom


def _divide_if_nonzero_vectorized(num_array, denom_array):
  vec_divide_nonzero = np.vectorize(_divide_if_nonzero)
  return vec_divide_nonzero(num_array,denom_array)



