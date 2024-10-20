import cv2
import numpy as np
import pytest
from src.frameQueueClasses import FrameQueue
from src.astaFilter import AstaFilter


@pytest.fixture(params=["data/tonemap_fire.PNG","data/tonemap_dark.PNG","data/tonemap_dark2.PNG"])
def fire_image(request):
    a = cv2.imread(request.param)
    return cv2.cvtColor(a,cv2.COLOR_BGR2HSV).astype(np.float64)


@pytest.fixture
def frame_window():
    a = FrameQueue("data/1110347515-preview.mp4")
    b = a.get_next_frame()
    while b.is_frame_at_edges() != 0:
        b = a.get_next_frame()
    return b


@pytest.fixture
def frame_window_identical_frames():
    a = FrameQueue("data/test_identical_frames.avi")
    b = a.get_next_frame()
    while b.is_frame_at_edges() != 0:
        b = a.get_next_frame()
    return b

@pytest.fixture
def frame_window_all_but_center_blank():
    a = FrameQueue("data/test_all_surrounding_frames_black.avi")
    b = a.get_next_frame()
    while b.is_frame_at_edges() != 0:
        b = a.get_next_frame()
    return b

@pytest.fixture
def spatial_kernels(frame_window):

    return AstaFilter.make_gaussian_kernels(frame_window.get_length())


@pytest.fixture
def asta_filter(frame_window):

    return AstaFilter(frame_window.get_length())


@pytest.fixture
def all_reached_target(frame_window):

 return np.full_like(frame_window.get_main_frame()[:, :, 0], -0.1)

@pytest.fixture
def none_reached_target(frame_window):

 return np.full_like(frame_window.get_main_frame()[:, :, 0], 0.1)

@pytest.fixture
def ones(frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0], 1.0)

@pytest.fixture
def twos(frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0],2.0)

@pytest.fixture
def threes(frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0],3.0)

@pytest.fixture
def fours(frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0], 4.0)

@pytest.fixture
def fives(frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0], 5.0)

@pytest.fixture
def sixes(frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0],6.0)

@pytest.fixture
def sevens(frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0],7.0)

@pytest.fixture
def eights(frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0], 8.0)

@pytest.fixture
def nines(frame_window):
    return np.full_like(frame_window.get_main_frame()[:, :, 0], 9.0)


@pytest.fixture(params=[i/2.0 for i in range(2,19)])

def gains(frame_window,request):
  return np.full_like(frame_window.get_main_frame()[:, :, 0], request.param)

