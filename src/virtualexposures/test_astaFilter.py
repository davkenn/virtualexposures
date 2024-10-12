import pytest
from astaFilter import AstaFilter


class TestAstaFilter:

    @pytest.fixture
    def spatial_kernels(self):
        """This fixture will only be available within the scope of TestGroup"""
        return AstaFilter.make_gaussian_kernels(4.0)

    def test_get_neighborhood_diffs(self,spatial_kernels):
        print AstaFilter.rearrange_gaussian_kernels(spatial_kernels,-len(spatial_kernels)//2)



