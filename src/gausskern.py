from __future__ import division

from xmllib import space

import cv2
import numpy as np
import sys

INTENSITY_SIGMA = 4.0

def get_1d_kernel(size, std_dev):
  kernel_t = cv2.getGaussianKernel(size*2+1,std_dev)

  for i in range(len(kernel_t)):
    a = abs((len(kernel_t)//2)- i)
    kernel_t[i] = _intensity_gaussian(a,std_dev)
  kernel = np.array([[0.0]] *41)
  center_indices = [slice(int((l - s) / 2), int((l + s) / 2))
                    for l, s in zip(kernel.shape, kernel_t.shape)]

  result = np.copy(kernel)
  result[tuple(center_indices)] = kernel_t
  return result


def get_2d_kernel(size, std_dev):
  """Returns a kernel of size by size with standard deviation given in other arg"""
  kernel_x = cv2.getGaussianKernel(size, std_dev)
  kernel_y = cv2.getGaussianKernel(size, std_dev)
  kernel = kernel_y * kernel_x.T
  return kernel


def get_kernel_center(kernel):
  return kernel.item(len(kernel) // 2)


def get_kernel_with_dynamic_std_dev(target_num, size):
  """This function will make it so that if all temporal pixels had identical
  neighborhoods, the summation of all frames would be (roughly) equal to
  2 * target_num * G_center where G_center is the weight of the center
  pixel in the spatial temporal kernel.  Returns the generated spatial (as
  in spatial distance in time) kernel"""
  #I have attenuation at 34 so I need to handle target_nums of up to
  #to 10.  If I had a much greater attenuation, I would need to change this
  #algorithm
  if target_num > 10.0:
    sys.stderr.write("Mapping should not go over 9.5")
    sys.exit()
  if size < 21:
    sys.stderr.write("Kernel size must be at least 21")
    sys.exit()

  target_before_distance_sigma = intensity_gaussian(0.0) * 2.0 * target_num
  kernel_size = 5
  std_dev = 0.05
  summation = 0.0
  space_kernel = get_1d_kernel(find_radius(std_dev), std_dev)
  total = get_kernel_center(space_kernel) * target_before_distance_sigma

  while summation < total:
    std_dev += 0.005
    space_kernel = get_1d_kernel(find_radius(std_dev),std_dev)
    total = target_before_distance_sigma * get_kernel_center(space_kernel)

    all_pixels = intensity_gaussian(np.zeros_like(space_kernel)) * space_kernel
    summation = all_pixels.sum()

  return space_kernel


def find_radius(sigma):
  return int(np.floor(2*sigma))

  #return math.ceil(sigma * np.sqrt(2*np.log(255)) -1)



def get_neighborhood_compare_kernel(size, std_dev):
  """Calls get2DKernel to create a gaussian neighborhood comparison kernel.
  It sets center pixel to zero because a pixel is not included in its neighborhood 
  (think shot noise)"""
  kernel = get_2d_kernel(size, std_dev)
  middle_idx = size // 2 # was middle_idx = size // 2
  # just compare neighborhoods, leave center pixel out
  kernel[middle_idx][middle_idx] = 0.0
  kernel = kernel / kernel.sum() #normalize

  return kernel


def get_neigh_diffs(neighborhood_1, neighborhood_2):
  """This function will calculate the differences between two
  numpy array images (lums) passed as arguments at every pixel. Then it will scale
  the result to be between zero and one. Assume that below some threshold
  (min_diff) the neighborhoods should be considered as identical and above
  some threshold (max_diff) the neighborhoods will be considered as different
  as they possibly can be (returns 0)"""
  return np.abs(np.subtract(neighborhood_1,neighborhood_2))


def intensity_gaussian(pixel_value_difference):
  """Computes the Gaussian function for a given x and standard deviation (sigma).
  """
  return _intensity_gaussian(pixel_value_difference)

def _intensity_gaussian(pixel_value_difference, sigma= INTENSITY_SIGMA):
  return np.exp((-(pixel_value_difference ** 2) / (2 * (sigma ** 2))))     / (sigma * np.sqrt(2 * np.pi))
 #   return ((1 / (sigma * np.sqrt(2 * np.pi))) *
   #         np.exp(-0.5 * ((pixel_value_difference ** 2) / (sigma ** 2))))


def _centralize_weights(kernel):
  kernel[0] = 0.0
  kernel[1] = 0.0
  kernel[len(kernel)-1] = 0.0
  kernel[len(kernel)-1] = 0.0
  kernel = kernel / kernel.sum()
  return kernel