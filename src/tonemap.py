from __future__ import division
import cv2
import numpy as np
from math import log10
import constants as const


def find_target_luminance(vid_frame):
  throwaway_blurred = cv2.GaussianBlur(vid_frame[:,:,0],(5,5),0)
  result = _tone_map(throwaway_blurred)
  return (result + 1.0) / (throwaway_blurred + 1.0)


def tonemap_spatially_uniform(vid_frame):
  #is this changing things in place?
  result = np.copy(vid_frame)

  result[:,:,0] =_tone_map(vid_frame[:,:,0])
  return result


def _tone_map(pixel_lum, attenuation= const.TONEMAP_ATTENUATION):
  """Takes as argument an input pixel luminance and maps it to an output pixel
   luminance. """
 #255 in article
  ratio = pixel_lum / 255.0 #255 is max luminance
  num = np.log10(ratio * (attenuation - 1) + 1)
  denom = np.log10(attenuation)
  return (num / denom) * 255.0


def tone_map(pixel_lum, attenuation= const.TONEMAP_ATTENUATION):
  """Takes as argument an input pixel luminance and maps it to an output pixel
   luminance. """
  return (pixel_lum - pixel_lum.min())/(pixel_lum.max()-pixel_lum.min())



