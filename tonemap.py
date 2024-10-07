from __future__ import division
import cv2
import numpy as np
from math import log10


def tone_map(pixel_lum, attenuation):
  """Takes as argument an input pixel luminance and maps it to an output pixel
   luminance. """
  ratio = pixel_lum / 255 #255 is max luminance
  num = log10(ratio * (attenuation - 1) + 1)
  denom = log10(attenuation)
  return num/denom


def tone_map_vectorized(vid_frame, attenuation):
  lum = vid_frame[:, :, 0]
  tone_map_vector_function = np.vectorize(tone_map)
  return tone_map_vector_function(lum,attenuation)
  

def divide_if_nonzero(num, denom):
  if denom == 0.0:
    return 1.0
  return num / denom


def divide_if_nonzero_vec(num_array, denom_array):
  vec_divide_nonzero = np.vectorize(divide_if_nonzero)
  return vec_divide_nonzero(num_array,denom_array)


def  find_target_luminance(vid_frame):
  throwaway_copy = np.copy(vid_frame)
  throwaway_blurred = cv2.GaussianBlur(throwaway_copy,(7,7),0)
  original_luminances = np.copy(vid_frame[:, :, 0])
  print original_luminances
  result = tone_map_vectorized(throwaway_blurred, 34)
  result *= 255
  return divide_if_nonzero_vec(result, throwaway_blurred[:, :, 0])


def tonemap_spatially_uniform(vid_frame):
  result = tone_map_vectorized(vid_frame, 34)
  result *= 255
  vid_frame[:, :, 0] = result.astype(int)
  return vid_frame

if __name__ == "__main__":
  
  for i in xrange(0,255):
    print i, " ", tone_map(i, 40) * 255
