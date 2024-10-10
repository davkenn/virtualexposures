from __future__ import division
import cv2
import sys

import numpy as np

#import faulthandler
from tonemap import find_target_luminance,tonemap_spatially_uniform
from astaFilter import asta_filter

class FrameQueue(object):
  """Surrounding frame count is the number of frames counting itself.
   Probably need a diff number of surrounding frames for each frame  but
   the best thing to do is probably just overestimate and use less if need be"""
  def __init__(self, video_filename, surrounding_frame_count):
    self.video_filename = video_filename
    #position of current frame in window
    self.current_frame_index = 0
    #overall frame number
    self.current_frame = 1    
    self.frame_window = []
    self.frames_in_video = self.count_frames()

    #window is always odd
    if surrounding_frame_count % 2 == 0:
      surrounding_frame_count += 1

    if surrounding_frame_count > self.frames_in_video:
      surrounding_frame_count = self.frames_in_video

    self.frames_in_window = surrounding_frame_count

    self.video_capt = cv2.VideoCapture(video_filename)

    self.fourcc = int(self.video_capt.get(cv2.CAP_PROP_FOURCC))
    self.fps =  self.video_capt.get(cv2.CAP_PROP_FPS)
    self.size = (int(self.video_capt.get(cv2.CAP_PROP_FRAME_WIDTH)),
                   int(self.video_capt.get(cv2.CAP_PROP_FRAME_HEIGHT)))

#then in other method we will be keeping frames at max surr frame count
    for i in range(self.frames_in_window):
      success,image = self.readVidFrameConvertBGR2YUV()
      self.frame_window.append(image)


  def count_frames(self):
    """Frames in video are counted manually because some file types do not
    have number of frames in their metadata"""
    capt = cv2.VideoCapture(self.video_filename)
    if not capt.isOpened():
      raise ValueError("Invalid input file")
    cnt = 0
    success, image = capt.read()
    while success:
      cnt += 1
      success, image = capt.read()
    return cnt


  def write_vid_frame_test(self, img, filename):
    image = cv2.cvtColor(img, cv2.COLOR_YUV2BGR)
    cv2.imwrite(filename, image)


  def writeVidFrameConvertYUV2BGR(self, img, video_writer):
    image = img[:, :, :].astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR)
    video_writer.write(image)


  def readVidFrameConvertBGR2YUV(self):
    success, img = self.video_capt.read()
    if success:
      image = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
      image = image[:, :, :].astype(np.float64)
      return success, image
    else:
      return success,img


  def get_next_frame(self):
    """This returns a window of frames around the current one.  THe only logic
     comes in the beginning and the end when we have to communicate that the
     current frame is not in the middle of the window"""
    if self.current_frame > self.frames_in_video:
      return None
    half_window = self.frames_in_window // 2 + 1

    if self.current_frame <= half_window:
      self.current_frame_index += 1

    #advance if out from the beginning and still frames left
    if half_window < self.current_frame <= (self.frames_in_video - (half_window - 1)):

         success,image = self.readVidFrameConvertBGR2YUV()

         self.frame_window.append(image)
         self.frame_window.pop(0)

    if self.current_frame > (self.frames_in_video - (half_window - 1)):

      self.current_frame_index += 1

    #THIS LINE MUST BE RIGHT BEFORE RETURN STATEMENT SO I DONT MESS UP LOGIC
    self.current_frame +=1
    #is there a bug in incrementing frame index in framewindow
    return FrameWindow(self.frame_window,self.current_frame_index)


class FrameWindow(object):
  """This is the window around the central frame"""

  def __init__(self, frame_list,curr_frame_index):
    self.frame_list = frame_list
    self.curr_frame_index = curr_frame_index - 1


  def get_main_frame(self):
    return self.frame_list[self.curr_frame_index]


  def get_length(self):
    return len(self.frame_list)


  def is_frame_at_edges(self):
    """Returns an integer indicating if the frame is close to the beginning or
    ending of the video.  If close to the beginning, it will return a negative
    number indicating how far the center frame is offset from the middle of the
    frame window.  If close to the end, it will return a positive number 
    indicating how far the frame is offset from center"""
    middle_frame_index = self.get_length() // 2 # +1 used earlier
    return self.curr_frame_index - middle_frame_index

    
if __name__ == "__main__":
  try:
    frame_queue = FrameQueue('large4.mp4',21)

  except ValueError as err:
    sys.stderr.write("Invalid Input File\n")
    sys.exit()

  vid = cv2.VideoWriter(
      'nek0addspatlllial.avi',
            cv2.VideoWriter.fourcc('M','J','P','G'),
            frame_queue.fps,
            frame_queue.size
  )

  fw = frame_queue.get_next_frame()

  while fw:
    gain_ratios = find_target_luminance(fw.get_main_frame())
    result = asta_filter(fw, gain_ratios)
    result[:,:,0] = tonemap_spatially_uniform(result)
    frame_queue.writeVidFrameConvertYUV2BGR(result,vid)
    print "Done with a frame"
    fw = frame_queue.get_next_frame()

