from src.tonemap import _tone_map, tonemap_spatially_uniform, find_target_luminance
import src.constants as const

class TestTonemap:


    def test_tone_map_gain_ration_in_range(self):
        for i in range(0,256):
            assert _tone_map(float(i))  >= 0.0
            assert _tone_map(float(i)) <= 255.0
        assert _tone_map(0.0) == 0.0


    def test_tone_map_spatially_uniform(self,fire_image):

        assert tonemap_spatially_uniform(fire_image).max() <= 255.0
        assert tonemap_spatially_uniform(fire_image).min() >= 0.0


    def test_tone_map_spatially_unifor(self, fire_image):
        assert find_target_luminance(fire_image).max() < 10.0
        assert find_target_luminance(fire_image).min() >= 1.0



