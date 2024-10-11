from __future__ import division
import cv2
import numpy as np
import sys
#if I normalize here like I did in neighborhood kernel I think I would
#just be doing it twice but it wouldnt affect correctness because im normalizing
#again anyways
def get_1d_kernel(size, std_dev):
  kernel_t = cv2.getGaussianKernel(size,std_dev)
  return kernel_t


def get_2d_kernel(size, std_dev):
  """Returns a kernel of size by size with standard deviation given in other arg"""
  kernel_x = cv2.getGaussianKernel(size, std_dev)
  kernel_y = cv2.getGaussianKernel(size, std_dev)
  kernel = kernel_y * kernel_x.T
  return kernel


def get_kernel_center(kernel):
  return kernel.item(len(kernel) // 2)


def calc_temp_std_dev_get_kernel(target_num,intensity_sigma):
  """This function will make it so if all temporal pixels had identical
  neighborhoods, the contribution of the neighborhood pixels would be 
  equal to 2 * target_num * G_center where G_center is the weight on center
  pixel.  Returns a pair of the kernel as well as the scaled target"""
  #I have attenuation at 34 so I need to handle target_nums of up to
  #to 10.  If I had a much greater attenuation, I would need to change this
  #algorithm
  size = 29
  if target_num < 1.0:
    a = get_1d_kernel(size,0.0)
    a = 0.0 * a
    a[len(a)//2] = 1.0
    return a
  if target_num > 10.0:
    sys.stderr.write("Mapping should not go over 9")
    sys.exit()
  target_before_distance_sigma = intensity_gaussian(0,intensity_sigma) * 2.0 * target_num

  std_dev = 0.5
  summation = 0.0
  kernel = get_1d_kernel(size, std_dev)
  total = get_kernel_center(kernel) * target_before_distance_sigma
  while summation < total:
    if std_dev > 10.0:
      size +=2
      std_dev = 0.1
      continue
    total = target_before_distance_sigma * get_kernel_center(kernel)
    kernel = get_1d_kernel(size,std_dev)
    std_dev += 0.1
    summation = np.zeros_like(kernel)
    summation =intensity_gaussian(summation,intensity_sigma)
    summation = kernel * summation
    summation = summation.sum()




  #paper changes both neighborhood size and std dev dynamically..
  #I have a fixed size neighborhood and just change std dev dynamically

 # if window_size < 19: #if I want smaller window must change atten
  #  sys.stderr.write("window size is too small to handle all cases")
   # sys.exit()

  return kernel


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

  neighborhood_diffs = np.abs(np.subtract(neighborhood_1,neighborhood_2))

  return neighborhood_diffs
  #from paper: "The neighborhood size, often between 3 and 5, can be 
  #varied depending on noise as can [std_dev] (usually between 2 and 6)
  g_kernel = get_neighborhood_compare_kernel(5, 2)

  #TODO: do i really want BORDER_REPLICATE?
  neigh_diffs = np.array(neighborhood_diffs,dtype='float64')


def intensity_gaussian(x, sigma):
    """
    Computes the Gaussian function for a given x and standard deviation (sigma).
    """
    return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(
      -0.5 * ((x ** 2) / (sigma ** 2)))

if __name__ == "__main__":

  for i in xrange(1, 20):
    pass
  
  j = np.array([[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]])
  l = np.array([[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]])
  m = np.array([[2.0,5.5,6.6],[7.7,15.0,0.0],[5.5,1.0,7.0]])

 # print calc_temp_std_dev_get_kernel(2.0, 19)
