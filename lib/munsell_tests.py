import lib.munsell as munsell
import unittest


class TestNumericalHue(unittest.TestCase):
    pass


class TestNearestHues(unittest.TestCase):
    def test_low_hue_in_mid_range(self):
        low_hue, high_hue = munsell.nearest_hues(32.2)
        self.assertEquals(low_hue, 30.0)

    def test_high_hue_in_mid_range(self):
        low_hue, high_hue = munsell.nearest_hues(32.2)
        self.assertEquals(high_hue, 32.5)

    def test_low_hue_unchanged(self):
        low_hue, high_hue = munsell.nearest_hues(32.5)
        self.assertEquals(low_hue, 32.5)

    def test_high_hue_unchanged(self):
        low_hue, high_hue = munsell.nearest_hues(32.5)
        self.assertEquals(high_hue, 32.5)


class TestNearestValues(unittest.TestCase):
    def test_low_value_in_mid_range(self):
        low_value, high_value = munsell.nearest_values(5.2)
        self.assertEquals(low_value, 5)

    def test_high_value_in_mid_range(self):
        low_value, high_value = munsell.nearest_values(5.2)
        self.assertEquals(high_value, 6)

    def test_low_value_unchanged(self):
        low_value, high_value = munsell.nearest_values(5)
        self.assertEquals(low_value, 5.0)

    def test_high_value_unchanged(self):
        low_value, high_value = munsell.nearest_values(5)
        self.assertEquals(high_value, 5.0)


class TestNearestChromas(unittest.TestCase):
    def test_low_chroma_in_mid_range(self):
        low_chroma, high_chroma = munsell.nearest_chromas(5.2)
        self.assertEquals(low_chroma, 4)

    def test_high_chroma_in_mid_range(self):
        low_chroma, high_chroma = munsell.nearest_chromas(5.2)
        self.assertEquals(high_chroma, 6)

    def test_low_chroma_unchanged(self):
        low_chroma, high_chroma = munsell.nearest_chromas(4)
        self.assertEquals(low_chroma, 4.0)

    def test_high_chroma_unchanged(self):
        low_chroma, high_chroma = munsell.nearest_chromas(4)
        self.assertEquals(high_chroma, 4.0)


class TestComplement(unittest.TestCase):
    def test_without_overflow(self):
        new_hue = munsell.complement(20)
        self.assertEquals(new_hue, 70)

    def test_with_overflow(self):
        new_hue = munsell.complement(70)
        self.assertEquals(new_hue, 20)
