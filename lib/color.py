import numpy as np
import math
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
except:
    pass

from functools import reduce

import lib.observers as observers


class Color():
    def __init__(self, spectrum,  proportion=1, name="", frequencies=observers.frequencies):
        self.spectrum = np.copy(spectrum)
        # Not sure about storing proportion on the spectrum, but here we go
        self.proportion = proportion
        self.name = name
        self.frequencies = frequencies
        self.imprecise = False
        self.clipped = False

    def color_part(self, x):
        return pow(max(min(x, 1), 0), 1/2.2)

    def to_rgb(self):
        r = np.sum(np.multiply(self.spectrum, observers.red))
        g = np.sum(np.multiply(self.spectrum, observers.green))
        b = np.sum(np.multiply(self.spectrum, observers.blue))
        if (any([x > 1 or x < 0 for x in [r, g, b]])):
            self.imprecise = True
            self.clipped = True

        return [self.color_part(x) for x in [r, g, b]]

    def to_hex(self):
        return "{0:02x}{1:02x}{2:02x}".format(*[int(x * 255) for x in  self.to_rgb()])

    def to_str(self):
        return "{0}: rgb({1}, {2}, {3})".format(self.name, *[int(x * 255) for x in self.to_rgb()])

    def swatch(self):
        box = plt.figure(figsize=(2, 1)).add_subplot(111)
        box.add_patch(
            patches.Rectangle(
                (0, 0.1),
                1,
                0.9,
                color=self.to_rgb()
            )
        )
        box.text(0.01, 0.01, self.to_str(), fontsize=12)

    def plot(self, color=None):
        plt.plot(self.frequencies, self.spectrum, color=(color or self.to_rgb()))

    def p(self, num):
        return Color(self.spectrum, num, self.name)

    def stats_dict(self):
        rgb = self.to_rgb()
        return {            "name": self.name,
            "rgb": rgb,
            "rgb255": [int(x * 255) for x in rgb],
            "hex": "#{0:02x}{1:02x}{2:02x}".format(*[int(x * 255) for x in rgb]),
            "imprecise": self.imprecise,
            "clipped": self.clipped,
        }


class Mix(Color):
    def __init__(self, proportional_colors):
        self.proportional_colors = proportional_colors
        self.name = self.make_name()
        self.proportion = 1

    def additive(self):
        return np.sum([color.spectrum*color.proportion for color in self.proportional_colors])

    def total_portion(self):
        return float(sum([color.proportion for color in self.proportional_colors]))

    @property
    def spectrum(self):
        if len(self.proportional_colors) == 1:
            return self.proportional_colors[0]
        total_portion = self.total_portion()

        power_colors = [np.power(color.spectrum, color.proportion/total_portion) for color in self.proportional_colors]
        return reduce(np.multiply, power_colors)

    def make_name(self):
        total_portion = sum([color.proportion for color in self.proportional_colors])
        return " + ".join(["{0:.1f}% {1}".format(100*color.proportion/total_portion, color.name) for color in self.proportional_colors])



def interpolate(xs, ys, desired_x):
    before = np.where(xs < desired_x)[0][-1]
    after = np.where(xs > desired_x)[0][0]
    # cheating, but doing prop'ly probably unnecessary given how small
    # the steps are in the original data.
    return (ys[before] + ys[after]) / 2
