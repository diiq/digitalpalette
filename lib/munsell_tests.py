import lib.munsell as munsell
import unittest


class TestNumericalHue(unittest.TestCase):
    def test_numerical_hue(self):
        hue = munsell.numerical_hue("5.0Y")
        self.assertEquals(hue, 25.0)

        hue = munsell.numerical_hue("2.7BG")
        self.assertEquals(hue, 52.7)


class TestNameForHue(unittest.TestCase):
    def test_name_for_hue(self):
        name = munsell.name_for_hue(25)
        self.assertEquals(name, "5.0Y")

        name = munsell.name_for_hue(52.7)
        self.assertEquals(name, "2.7BG")

        name = munsell.name_for_hue(97.5)
        self.assertEquals(name, "7.5RP")


class TestNameForColor(unittest.TestCase):
    def test_name_for_color(self):
        name = munsell.name_for_color(25, 3, 2)
        self.assertEquals(name, "5.0Y 3.0/2.0")

        name = munsell.name_for_color(52.7, 4, 1.1)
        self.assertEquals(name, "2.7BG 4.0/1.1")


class TestNearestHues(unittest.TestCase):
    def test_low_hue_in_mid_range(self):
        low_hue, high_hue = munsell.colors.nearest_hues(32.2)
        self.assertEquals(low_hue, 30.0)

    def test_high_hue_in_mid_range(self):
        low_hue, high_hue = munsell.colors.nearest_hues(32.2)
        self.assertEquals(high_hue, 32.5)

    def test_low_hue_unchanged(self):
        low_hue, high_hue = munsell.colors.nearest_hues(32.5)
        self.assertEquals(low_hue, 32.5)

    def test_high_hue_unchanged(self):
        low_hue, high_hue = munsell.colors.nearest_hues(32.5)
        self.assertEquals(high_hue, 32.5)


class TestNearestValues(unittest.TestCase):
    def test_low_value_in_mid_range(self):
        low_value, high_value = munsell.colors.nearest_values(5.2)
        self.assertEquals(low_value, 5)

    def test_high_value_in_mid_range(self):
        low_value, high_value = munsell.colors.nearest_values(5.2)
        self.assertEquals(high_value, 6)

    def test_low_value_unchanged(self):
        low_value, high_value = munsell.colors.nearest_values(5)
        self.assertEquals(low_value, 5.0)

    def test_high_value_unchanged(self):
        low_value, high_value = munsell.colors.nearest_values(5)
        self.assertEquals(high_value, 5.0)


class TestNearestChromas(unittest.TestCase):
    def test_low_chroma_in_mid_range(self):
        low_chroma, high_chroma = munsell.colors.nearest_chromas(5.2)
        self.assertEquals(low_chroma, 4)

    def test_high_chroma_in_mid_range(self):
        low_chroma, high_chroma = munsell.colors.nearest_chromas(5.2)
        self.assertEquals(high_chroma, 6)

    def test_low_chroma_unchanged(self):
        low_chroma, high_chroma = munsell.colors.nearest_chromas(4)
        self.assertEquals(low_chroma, 4.0)

    def test_high_chroma_unchanged(self):
        low_chroma, high_chroma = munsell.colors.nearest_chromas(4)
        self.assertEquals(high_chroma, 4.0)


class TestComplement(unittest.TestCase):
    def test_without_overflow(self):
        new_hue = munsell.complement(20)
        self.assertEquals(new_hue, 70)

    def test_with_overflow(self):
        new_hue = munsell.complement(70)
        self.assertEquals(new_hue, 20)


class TestGetColorFor(unittest.TestCase):
    # Brittle tests, but it's someplace to start for refactoring db
    def test_direct_sample(self):
        new_color = munsell.colors.get_color_for(5, 5, 6)
        self.assertListEqual(list(new_color.to_rgb()), [0.6733446600403031, 0.4058324881477391, 0.39677207929969144])

    def test_hue_interpolation(self):
        new_color = munsell.colors.get_color_for(5.5, 5, 6)
        self.assertListEqual(list(new_color.to_rgb()), [0.674749439767226, 0.40717094319347696, 0.3912341887734641])

    def test_value_interpolation(self):
        new_color = munsell.colors.get_color_for(5, 5.5, 6)
        self.assertListEqual(list(new_color.to_rgb()), [0.724002585921689, 0.4562163455617211, 0.44522484509479693])

    def test_chroma_interpolation(self):
        new_color = munsell.colors.get_color_for(5, 5, 5.5)
        self.assertListEqual(list(new_color.to_rgb()), [0.6600346240464608, 0.41275205649334307, 0.4034785099114721])

    def test_multi_interpolation(self):
        new_color = munsell.colors.get_color_for(5.5, 5.5, 5.5)
        self.assertListEqual(list(new_color.to_rgb()), [0.7094404463114915, 0.4628979516270451, 0.4457307548127278])

    def test_multi_interpolation_hvc(self):
        new_color = munsell.colors.get_color_for(5.5, 4.5, 3.5)
        self.assertEqual(new_color.hue, 5.5)
        self.assertEqual(new_color.value, 4.5)
        self.assertEqual(new_color.chroma, 3.5)
        self.assertEqual(new_color.name, "5.5R 4.5/3.5")

    def test_extreme_lows(self):
        new_color = munsell.colors.get_color_for(2, 1, 0)
        self.assertEqual(new_color.hue, 2)
        self.assertListEqual(list(new_color.to_rgb()), [0.11650938827685081, 0.11650938827685069, 0.11650938827685073])

    def test_extreme_highs(self):
        new_color = munsell.colors.get_color_for(85, 7, 12)
        self.assertEqual(new_color.hue, 85)
        self.assertListEqual(list(new_color.to_rgb()), [0.7668171130344671, 0.6399528239862932, 0.862195224973096])

class TestColorSampleExists(unittest.TestCase):
    def test_color_sample_exists(self):
        self.assertEqual(munsell.colors.color_sample_exists(5, 5, 6), True)
        self.assertEqual(munsell.colors.color_sample_exists(5.4, 5, 6), False)
        self.assertEqual(munsell.colors.color_sample_exists(5.2, 5.1, 6.1), False)

class MunsellColor(unittest.TestCase):
    def test_spectrum(self):
        self.assertEqual(len(munsell.MunsellColor("5R", 2, 2).spectrum), 36)

    def do_things_without_errors(self):
        # sloppy TODO
        r = munsell.MunsellColor("6.0GY", 1, 7)
        b = munsell.MunsellColor("6.0GY", 9, 7)
        ladder = munsell.numerical_ladder(r, b, 6)
        [x.to_rgb() for x in ladder]
        [x.in_sunlight().to_rgb() for x in ladder]
        [x.in_shadow().to_rgb() for x in ladder]
