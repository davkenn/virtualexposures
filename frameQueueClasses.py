from __future__ import division
import cv2
import sys
#import faulthandler
#import numpy as np
from tonemap import find_target_luminance,tonemap_spatially_uniform
from astaFilter import asta_filter
 
class FrameQueue(object):
  """Surrounding frame count is the number of frames counting itself.
   Probably need a diff number of surrounding frames for each frame  but
   the best thing to do is probably just overestimate and use less if need be"""
  def __init__(self, video_filename, surrounding_frame_count):
    #position of current frame in window
    self.current_frame_index = 0
    #overall frame number
    self.current_frame = 1    
    self.frame_window = []
    #window is always odd
    if surrounding_frame_count % 2 == 0:
      surrounding_frame_count += 1

    self.frames_in_window = surrounding_frame_count

    self.frames_in_video = self.count_frames(video_filename)

    if surrounding_frame_count > self.frames_in_video:
      surrounding_frame_count = self.frames_in_video

    self.frames_in_window = surrounding_frame_count

    self.video_capt = cv2.VideoCapture(video_filename)


    self.fourcc = int(self.video_capt.get(cv2.CAP_PROP_FOURCC))
    self.fps =  self.video_capt.get(cv2.CAP_PROP_FPS)
    self.size = (int(self.video_capt.get(cv2.CAP_PROP_FRAME_WIDTH)),
                   int(self.video_capt.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fc = int(self.video_capt.get(cv2.CAP_PROP_FRAME_COUNT))

    ctr = self.frames_in_window
#then in other method we will be keeping frames at max surr frame count
    while ctr > 0:

      success,image = self.readVidFrameConvertBGR2YUV()
      self.frame_window.append(image)
      ctr -= 1

  def write_vid_frame_test(self, img, filename):
    image = cv2.cvtColor(img, cv2.COLOR_YUV2BGR)
    cv2.imwrite(filename, image)

  def writeVidFrameConvertYUV2BGR(self,img,videowriter):
    image = cv2.cvtColor(img, cv2.COLOR_YUV2BGR)
    videowriter.write(image)

  def readVidFrameConvertBGR2YUV(self):
    success, img = self.video_capt.read()
    if success:
      image = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
      return success, image
    else:
      return success,img


  """Use this instead of prop so that videos without metadata can have a correct count"""
  def count_frames(self, video_filename):
    capt = cv2.VideoCapture(video_filename)
    if not capt.isOpened():
      raise ValueError("Invalid input file")
    cnt = 0
    success,image = capt.read()
    while success:
      cnt += 1
      success,image = capt.read()
    return cnt
    
  """This returns a window of frames around the current one.  THe only logic comes
  in the beginning and the end when we have to communicate that the current frmae
  is not in the middle of the window"""      
  def get_next_frame(self):
    if self.current_frame > self.frames_in_video:
      return None
    half_window = self.frames_in_window // 2 + 1

    if self.current_frame <= half_window:
      self.current_frame_index += 1

    #advance if out from the beginning and still frames left
    if half_window < self.current_frame <= (self.frames_in_video - (half_window - 1)):

         success,image = self.readVidFrameConvertBGR2YUV()
         #FIFO OP IN NEXT TWO LINES
         self.frame_window.append(image)
         self.frame_window.pop(0)

    if self.current_frame > (self.frames_in_video - (half_window - 1)):

      self.current_frame_index += 1

    #THIS LINE MUST BE RIGHT BEFORE RETURN STATEMENT SO I DONT MESS UP LOGIC
    self.current_frame +=1
    return FrameWindow(self.frame_window,self.current_frame_index)


"""This is the window around the central frame"""
class FrameWindow(object):
  """Given a list of all of its frames at the beginning and this can never be changed. curr_frame_index is 1-indexed rather than 0-indexed"""
  def __init__(self, frame_list,curr_frame_index):

    self.frame_list = frame_list
    self.curr_frame_index = curr_frame_index - 1

  def getMainFrame(self):

    return self.frame_list[self.curr_frame_index]

  def getLength(self):
    return len(self.frame_list)

  def get_other_frames(self):
    return self.frame_list[0:self.curr_frame_index] + \
           self.frame_list[self.curr_frame_index + 1:]

  def is_frame_at_edges(self):
    """Returns an integer indicating if the frame is close to the beginning or
    ending of the video.  If close to the beginning, it will return a negative
    number indicating how far the center frame is offset from the middle of the
    frame window.  If close to the end, it will return a positive number 
    indicating how far the frame is offset from center"""
    middle_frame_index = self.getLength() // 2 # +1 used earlier
    return self.curr_frame_index - middle_frame_index


    
if __name__ == "__main__":

 # faulthandler.enable()
  try:
    frame_queue = FrameQueue('large.mp4',19)
  except ValueError as err:
    sys.stderr.write("Invalid Input File\n")
    sys.exit()

  vid = cv2.VideoWriter('new.avi', cv2.VideoWriter.fourcc('M','J','P','G'),
                                  frame_queue.fps,frame_queue.size)


  fw = frame_queue.get_next_frame()


  while fw:
    gain_ratios = find_target_luminance(fw.getMainFrame())
    result = asta_filter(fw, gain_ratios)
    result = tonemap_spatially_uniform(result)
    frame_queue.writeVidFrameConvertYUV2BGR(result,vid)
    print "Done with a frame"
    fw = frame_queue.get_next_frame()

