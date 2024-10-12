from __future__ import division
import cv2
import sys
import numpy as np
from tonemap import find_target_luminance,tonemap_spatially_uniform
from astaFilter import AstaFilter

class FrameQueue(object):
  """Surrounding frame count is the number of frames counting itself.
   Probably need a diff number of surrounding frames for each frame  but
   the best thing to do is probably just overestimate and use less if need be"""
  def __init__(self, video_filename, surrounding_frame_count):
    self.video_filename = video_filename
    #position of current frame in window
    self.current_frame_index = -1
    #overall frame number
    self.current_frame = 1
    self.frame_window = []

    #window is always odd
    self.video_capt = cv2.VideoCapture(video_filename)
    if not self.video_capt.isOpened():
      raise ValueError("Invalid input file: " + video_filename)

#    self.fourcc = int(self.video_capt.get(cv2.CAP_PROP_FOURCC))
    fps =  self.video_capt.get(cv2.CAP_PROP_FPS)
    dims = (int(self.video_capt.get(cv2.CAP_PROP_FRAME_WIDTH)),
                   int(self.video_capt.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    self.video_writer = cv2.VideoWriter('ne.avi',
                                        cv2.VideoWriter.fourcc(
                                            'M', 'J', 'P','G'),
                                        fps,
                                        dims

    )

    self.frames_in_video = self.count_frames()

    if surrounding_frame_count % 2 == 0:
      surrounding_frame_count += 1

    if surrounding_frame_count > self.frames_in_video:
      surrounding_frame_count = self.frames_in_video

#maybe set this to a constant need same value in other file
    self.frames_in_window = surrounding_frame_count

    for i in range(self.frames_in_window):
      success,image = self.readVidFrameConvertBGR2YUV()
      self.frame_window.append(image)


  def count_frames(self):
    """Frames in video are counted manually because some file types do not
    have number of frames in their metadata"""

    cnt = 0
    success, image = self.video_capt.read()
    while success:
      cnt += 1
      success, image = self.video_capt.read()
    self.video_capt.release()
    self.video_capt.open(self.video_filename)
    return cnt


  def writeVidFrameConvertYUV2BGR(self, img):
    image = img[:, :, :].astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR)
    self.video_writer.write(image)


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
    elif self.current_frame <= (self.frames_in_video - (half_window - 1)):

         success,image = self.readVidFrameConvertBGR2YUV()

         self.frame_window.append(image)
         self.frame_window.pop(0)

    else:
      self.current_frame_index += 1

    #THIS LINE MUST BE RIGHT BEFORE RETURN STATEMENT SO I DONT MESS UP LOGIC
    self.current_frame +=1
    #is there a bug in incrementing frame index in framewindow
    return FrameWindow(self.frame_window,self.current_frame_index)

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
    elif self.current_frame <= (self.frames_in_video - (half_window - 1)):

         success,image = self.readVidFrameConvertBGR2YUV()

         self.frame_window.append(image)
         self.frame_window.pop(0)

    else:
      self.current_frame_index += 1

    #THIS LINE MUST BE RIGHT BEFORE RETURN STATEMENT SO I DONT MESS UP LOGIC
    self.current_frame +=1
    #is there a bug in incrementing frame index in framewindow
    return FrameWindow(self.frame_window,self.current_frame_index)

class FrameWindow(object):
  """This is the window around the central frame"""

  def __init__(self, frame_list,curr_frame_index):
    self.frame_list = frame_list
    self.curr_frame_index = curr_frame_index
    print self.curr_frame_index


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
    middle_frame_index = self.get_length() // 2
    return self.curr_frame_index - middle_frame_index

    
if __name__ == "__main__":
  try:
    frame_queue = FrameQueue('large6.mp4',25)
  except ValueError as err:
    sys.stderr.write(err.message)
    sys.exit()

  fw = frame_queue.get_next_frame()

  filter_var = AstaFilter(2.5)


  while fw:
    gain_ratios = find_target_luminance(fw.get_main_frame())

    assert np.all(np.array(list(map(lambda x: x < 10.0, gain_ratios))))
    result = filter_var.asta_filter(fw, gain_ratios)
    result[:,:,0] = tonemap_spatially_uniform(result)
    frame_queue.writeVidFrameConvertYUV2BGR(result)
    print "Done with a frame"
    fw = frame_queue.get_next_frame()


