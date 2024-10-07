from __future__ import division
import cv2
import numpy as np
import sys
#if I normalize here like I did in neighborhood kernel I think I would
#just be doing it twice but it wouldnt affect correctness because im normalizing
#again anyways
def get_1d_kernel(size, std_dev):
  if size % 2 == 0:
    size += 1
  kernel_t = cv2.getGaussianKernel(size,std_dev)
  return kernel_t


def get_2d_kernel(size, std_dev):
  """Returns a kernel of size by size with standard deviation given in other arg"""
  if size % 2 == 0:
    size += 1
  #adapted from Howse book
  kernel_x = cv2.getGaussianKernel(size, std_dev)
  kernel_y = cv2.getGaussianKernel(size, std_dev)
  kernel = kernel_y * kernel_x.T
  return kernel


def get_kernel_center(kernel):
  return kernel.item(len(kernel) // 2)


def calc_temp_std_dev_get_kernel(target_num, window_size):
  """This function will make it so if all temporal pixels had identical
  neighborhoods, the contribution of the neighborhood pixels would be 
  equal to 2 * target_num * G_center where G_center is the weight on center
  pixel.  Returns a pair of the kernel as well as the scaled target"""
  #I have attenuation at 34 so I need to handle target_nums of up to
  #to 10.  If I had a much greater attenuation, I would need to change this
  #algorithm
  
  if target_num > 9:
    sys.stderr.write("Mapping should not go over 9")
    sys.exit()

  #paper changes both neighborhood size and std dev dynamically..
  #I have a fixed size neighborhood and just change std dev dynamically

  if window_size < 19: #if I want smaller window must change atten
    sys.stderr.write("window size is too small to handle all cases")
    sys.exit()

  temp_std_dev = 0.5
  kernel = get_1d_kernel(window_size, temp_std_dev)
  target_weighted = 2 * target_num * get_kernel_center(kernel) * 1.0    #1.0 is because center has
                                                                      #perfect match with itself 
  neighborhood_weight = kernel.sum() - get_kernel_center(kernel)

  while abs(neighborhood_weight - target_weighted) > .05:

    temp_std_dev += 0.01
    kernel = get_1d_kernel(window_size, temp_std_dev)
    target_weighted = 2 * target_num * get_kernel_center(kernel) * 1.0
    neighborhood_weight = kernel.sum() - get_kernel_center(kernel)
  
  return target_weighted, kernel

#TODO: I am normalizing before the operation in getting neighborhood
 #, is this wrong?
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

def get_neighborhood_diffs(neighborhood_1, neighborhood_2, min_diff, max_diff):
  """This function will calculate the differences between two
  numpy array images (lums) passed as arguments at every pixel. Then it will scale
  the result to be between zero and one. Assume that below some threshold
  (min_diff) the neighborhoods should be considered as identical and above
  some threshold (max_diff) the neighborhoods will be considered as different
  as they possibly can be (returns 0)"""

  e = np.subtract(neighborhood_1,neighborhood_2)
  neighborhood_diffs = np.abs(e)


  #from paper: "The neighborhood size, often between 3 and 5, can be 
  #varied depending on noise as can [std_dev] (usually between 2 and 6)
  g_kernel = get_neighborhood_compare_kernel(5, 2)

  #TODO: do i really want BORDER_REPLICATE?
  neigh_diffs = np.array(neighborhood_diffs,dtype='float64')



  diffs_each_pixel = cv2.filter2D(neigh_diffs,
                       -1,g_kernel,borderType=cv2.BORDER_REPLICATE)



#  values = np.zeros_like(diffs_each_pixel)

  values = distance_metric(neigh_diffs, min_diff, max_diff)


  return neighborhood_1

def distance_metric(distance, mn, mx):
  """Parallel version of sequential distanceMetric2
  function below."""

  distance = distance - mn
  mx = mx - mn
  zeros = np.zeros_like(distance)

  a = np.less(distance,zeros)
  dist = np.where(a,zeros,distance)

  b = np.greater(dist,mx)
  dis = np.where(b,mx,dist)

  return (mx - dis) / mx


def distance_metric2(distance, mn, mx):
  """Sequential distance metric.  Not used in final program
  for performance reasons"""
  distance = distance - mn
  mx = mx - mn

  if distance < 0:
    distance = 0
  elif distance > mx:
    distance = mx

  return (mx - distance) / mx

if __name__ == "__main__":

  for i in xrange(1, 20):
    pass
  #  print "MIN 4, MAX 16, ARG ",str(i),"=",distance_metric(i, 4, 16)

  
  j = np.array([[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]])
  l = np.array([[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]])
  m = np.array([[2.0,5.5,6.6],[7.7,15.0,0.0],[5.5,1.0,7.0]])
  print distance_metric2(5.5,1.0,7.0)
  print distance_metric(m,1.0,7.0)
  #print  get_neighborhood_diffs(j, l, 4, 16)

 # print calc_temp_std_dev_get_kernel(2.0, 19)
