from tonemap import tone_map


class TestTonemap:



    def test_get_neighborhood_diffs(self):
        for i in range(1,257):
            assert (tone_map(float(i),34) * 256.0) / float(i) > 1.0
            assert (tone_map(float(i), 34) * 256.0) / float(i) < 10.0
        assert tone_map(0.0,34)==0.0
        print  (tone_map(float(18), 34) * 256.0) / float(18)

