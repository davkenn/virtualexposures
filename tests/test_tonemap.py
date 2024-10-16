from src.tonemap import _tone_map
import src.constants as const

class TestTonemap:



    def test_get_neighborhood_diffs(self):
        for i in range(1,257):

            assert (_tone_map(float(i), const.TONEMAP_ATTENUATION) * 256.0) / float(i) > 1.0
            assert (_tone_map(float(i), const.TONEMAP_ATTENUATION) * 256.0) / float(i) < 10.0
        assert _tone_map(0.0, const.TONEMAP_ATTENUATION) == 0.0
        print  (_tone_map(float(18), const.TONEMAP_ATTENUATION) * 256.0) / float(18)

