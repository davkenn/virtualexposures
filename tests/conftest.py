import numpy as np
import pytest
from src.frameQueueClasses import FrameQueue
from src.astaFilter import AstaFilter


@pytest.fixture
def frame_window():
    a = FrameQueue("data/1110347515-preview.mp4")
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
