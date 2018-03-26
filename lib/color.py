import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from functools import reduce

import observers


class Color():
    def __init__(self, spectrum, proportion=1, name=""):
        self.spectrum = np.copy(spectrum)
        # Not sure about storing proportion on the spectrum, but here we go
        self.proportion = proportion
        self.name = name

    def color_part(self, x):
        return pow(max(min(x, 1), 0), 1/2)

    def to_rgb(self):
        r = np.sum(np.multiply(self.spectrum, observers.red))
        g = np.sum(np.multiply(self.spectrum, observers.green))
        b = np.sum(np.multiply(self.spectrum, observers.blue))
        return np.array([self.color_part(x) for x in [r, g, b]])

    def to_str(self):
        return "{0}: rgb({1:.2}, {2:.2}, {3:.2})".format(self.name, *self.to_rgb())

    def swatch(self):
        box = plt.figure(figsize=(10, 5)).add_subplot(111)
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
        plt.plot(observers.frequencies, self.spectrum, color=(color or self.to_rgb()))

    def p(self, num):
        return Color(self.spectrum, num, self.name)


class Mix():
    def __init__(self, proportional_colors):
        self.proportional_colors = proportional_colors

    def additive(self):
        return np.sum([color.spectrum*color.proportion for color in self.proportional_colors])

    def to_color(self, name=None):
        if len(self.proportional_colors) == 1:
            return self.proportional_colors[0]
        total_portion = float(sum([color.proportion for color in self.proportional_colors]))

        power_colors = [np.power(color.spectrum, color.proportion/total_portion) for color in self.proportional_colors]
        return Color(reduce(np.multiply, power_colors), 1, name or self.name())

    def to_rgb(self):
        self.to_color().to_rgb()

    def name(self):
        total_portion = sum([color.proportion for color in self.proportional_colors])
        return " + ".join(["{0:.1f}% {1}".format(100*color.proportion/total_portion, color.name) for color in self.proportional_colors])