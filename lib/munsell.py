# coding: utf-8
import csv
import numpy as np
import math
import os
import re

import lib.color as color
import lib.observers as observers
import sqlite3


# Munsell reflectance curves are from
# http://www.munsellcolourscienceforpainters.com/MunsellResources/MunsellResources.html

DATA_FILE = './lib/munsell.csv'
class MissingColorError(Exception): pass

class MunsellSample(color.Color):
    def __init__(self, spectrum, hue=None, value=None, chroma=None, frequencies=observers.frequencies):
        super().__init__(spectrum, 1, name_for_color(hue, value, chroma))
        self.frequencies = frequencies
        self.hue = hue
        self.value = value
        self.chroma = chroma


# Munsell hues are almost-numbered; for the sake of doing math, we'll
# have to convert the number+letters hue into just-a-number between 1
# and 100; 50 steps takes you to a (pretty darn exact) complement.

HUE_NAMES = ['R', 'YR', 'Y', 'GY', 'G', 'BG', 'B', 'PB', 'P', 'RP', "XXXXX"]
HUE_NAMES_TO_NUMBERS = {v: 10 * i for i, v in enumerate(HUE_NAMES)}
hue_regex = re.compile('(\d+(\.\d+)?)([RYGBP]{1,2})')
def numerical_hue(hue):
    """Parse a hue name into a float from 0 to 100."""
    if isinstance(hue, str):
        match = hue_regex.match(hue)
        if match:
            return float(match[1]) + HUE_NAMES_TO_NUMBERS[match[3]]
        else:
            return float(hue)
    return hue

def name_for_hue(hue):
    if isinstance(hue, str):
        hue = numerical_hue(hue)
    hue = hue % 100
    return "{0:1.1f}{1}".format(hue % 10, HUE_NAMES[int(math.floor(hue / 10))])

def name_for_color(hue, value, chroma):
    return "{0} {1:1.1f}/{2:1.1f}".format(name_for_hue(hue), value, chroma)

name_regex = re.compile('(.*[RYGBP]{1,2}) ?(.*)[\,\/](.*)')
def color_from_name(name):
    match = name_regex.match(name)
    return MunsellColor(name_for_hue(match[1]), float(match[2]), float(match[3]))


# We'll need to rapidly search by hue, value, and chroma, so we create
# an in-memory database of color samples.
class MunsellSampleDatabase():
    def __init__(self):
        self.create_database()
        self.load_colors()
        self.insert_colors()

    def load_colors(self, file=DATA_FILE):
        colors = []
        with open(file) as csvfile:
            reader = csv.reader(csvfile)
            arr = [row for row in reader]
        for row in arr[1:1488]:
            colors.append(MunsellSample([float(f) for f in row[8:8+36]], numerical_hue(row[2]), *[float(f) for f in row[3:5]]))
        self.color_list = colors

    def create_database(self):
        # God knows this is a bad idea
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        c = conn.cursor()
        c.execute('CREATE TABLE colors (hue float, value float, chroma float, i integer)')
        self.cursor = c

    def insert_colors(self):
        self.cursor.executemany("INSERT INTO colors VALUES (?, ?, ?, ?)", [(color.hue, color.value, color.chroma, i) for i, color in enumerate(self.color_list)])

    def color_sample_exists(self, hue=None, value=None, chroma=None):
        if (value == 1):
            return False
        pairs = [["hue=?", hue], ["value=?", value], ["chroma=?", chroma]]
        string = "SELECT i FROM colors WHERE " + " AND ".join([str(q[0]) for q in pairs if q[1] != None])
        vals = [q[1] for q in pairs if q[1] != None]
        return not not self.cursor.execute(string, vals).fetchone()

    def color_sample(self, hue, value, chroma):
        ind = self.cursor.execute(
            "SELECT i FROM colors WHERE hue=? AND value=? AND chroma=?",
            (hue, value, chroma)).fetchone()[0]
        return self.color_list[ind]

    def max_chroma_sample(self, hue, value):
        ind = self.cursor.execute(
            "SELECT i FROM colors WHERE hue=? AND value=? ORDER BY chroma DESC",
            (hue, value)).fetchone()
        ind = ind[0]
        return self.color_list[ind]


class ExpandedMunsellSampleDatabase(MunsellSampleDatabase):
    def __init__(self):
        super().__init__()
        self.insert_overchromas()
        self.insert_grays()
        self.insert_whites_and_blacks()

    # Use titanium white and bone black for 0 and 10 values. Lies.
    def insert_whites_and_blacks(self):
        white = self.color_list[1485]
        black = self.color_list[1486]
        i = len(self.color_list) - 1
        for doublehue in range(5, 201, 5):
            for chroma in range(0, 3, 2):
                hue = doublehue / 2.0

                nblack = black.p(1)
                nblack.hue = hue
                nblack.value = 0
                nblack.chroma = chroma
                self.color_list.append(nblack)
                i += 1
                self.cursor.execute("INSERT INTO colors VALUES (?, ?, ?, ?)", (hue, 0, chroma, i))

                nwhite = white.p(1)
                nwhite.hue = hue
                nwhite.value = 10
                nwhite.chroma = chroma
                self.color_list.append(nwhite)
                i += 1
                self.cursor.execute("INSERT INTO colors VALUES (?, ?, ?, ?)", (hue, 10, chroma, i))

    ### GRAYS ###
    # The sample data contains no 0-chroma samples. I'd like spectra
    # for real munsell grays, but this is a start; I interpolate
    # between two low-chroma complements at the desired value, then
    # flatten the resulting spectra to the average value. NOT perfect,
    # lots of easily disproven assumptions, there, but it's what I can
    # do
    def how_gray(self, color):
        rgb = color.to_rgb()
        diff = max(rgb) - min(rgb)
        return 1 - diff

    def better(self, mix_a, mix_b):
        return self.how_gray(mix_a) > self.how_gray(mix_b)

    def find_grayest(self, a, b):
        mix = color.Mix([a, b])
        ap = 1
        new_mix = color.Mix([a.p(1.05), b])
        # todo binary search
        if self.better(new_mix, mix):
            while self.better(new_mix, mix):
                ap += .05
                mix = new_mix
                new_mix = color.Mix([a.p(ap), b])
        else:
            new_mix = color.Mix([a.p(0.95), b])
            while self.better(new_mix, mix):
                ap -= .05
                mix = new_mix
                new_mix = color.Mix([a.p(ap), b])
        flat_spectrum = [sum(mix.spectrum)/len(mix.spectrum)] * len(mix.spectrum)
        return MunsellSample(flat_spectrum, a.hue, a.value, 0)

    def insert_grays(self):
        chroma = 2
        i = len(self.color_list) - 1
        for doublehue in range(5, 201, 5):
            hue = doublehue / 2.0
            for value in range(2, 10):
                this_color = self.get_color_for(hue, value, chroma)
                comp = self.get_color_for(complement(hue), value, chroma)
                sample = self.find_grayest(this_color, comp)

                self.color_list.append(sample)
                i += 1
                self.cursor.execute("INSERT INTO colors VALUES (?, ?, ?, ?)", (hue, value, 0, i))

    ### OVERCHROMAS ###
    # Now the hax really begin :( There are some high-chroma values
    # which are useful for interpolation but missing from the data.
    # Overchromas are me attempting to extrapolate those samples from
    # existing ones.
    def calculate_overchroma(self, hue, value, direction=-1):
        current = self.max_chroma_sample(hue, value)

        if not self.color_sample_exists(hue, value + direction * 2, current.chroma + 2):
            return
        if not self.color_sample_exists(hue, value + direction * 1, current.chroma + 2):
            return

        a_col = self.color_sample(hue, value + direction * 1,  current.chroma + 2)
        b_col = self.color_sample(hue, value + direction * 2,  current.chroma + 2)

        spectrum = np.add(np.subtract(a_col.spectrum, b_col.spectrum), a_col.spectrum).clip(min=0)
        return MunsellSample(spectrum, hue, value, a_col.chroma)


    def insert_overchromas(self):
        i = len(self.color_list) - 1
        insertions = []
        for doublehue in range(5, 201, 5):
            hue = doublehue / 2.0
            for value in range(2, 10):
                if value > 2:
                    c = self.calculate_overchroma(hue, value, -1)
                    if c:
                        self.color_list.append(c)
                        i += 1
                        insertions.append([hue, value, c.chroma, i])
                if value < 8:
                    c = self.calculate_overchroma(hue, value, 1)
                    if c:
                        self.color_list.append(c)
                        i += 1
                        insertions.append([hue, value, c.chroma, i])

        for it in insertions:
            self.cursor.execute("INSERT INTO colors VALUES (?, ?, ?, ?)", it)


class InterpolatedMunsellColorDatabase(ExpandedMunsellSampleDatabase):
    # The Munsell space is continuous, but we only have samples. These
    # are methods for interpolating between samples. We restrict
    # interpolation to between on-axis values, as there's no
    # conversion factor between hue/chroma/value step sizes.
    def nearest_hues(self, hue):
        # There is a sample hue every 2.5 steps, so round to the nearest 2.5
        low_hue = math.floor(hue * 1/2.5)*2.5
        high_hue = math.ceil(hue * 1/2.5)*2.5
        return low_hue, high_hue

    def mix_to_hue(self, hue, value, chroma, depth=0):
        low_hue, high_hue = self.nearest_hues(hue)
        low_col = self._get_color_for(low_hue, value, chroma, depth+1)
        if (low_hue == hue):
            return low_col
        high_col = self._get_color_for(high_hue % 100, value, chroma, depth+1)
        mix = color.Mix([high_col.p(hue - low_hue), low_col.p(high_hue - hue)])
        return MunsellSample(mix.spectrum, hue, value, chroma)

    def nearest_values(self, value):
        # TODO sometimes there's an 8.5
        # there's a value sample every 1 step but not at 1
        low_value = math.floor(value)
        if low_value == 1.0:
            low_value = 0
        high_value = math.ceil(value)
        if high_value == 1.0:
            high_value = 2.0
        return low_value, high_value

    def mix_to_value(self, hue, value, chroma, depth=0):
        low_value, high_value = self.nearest_values(value)
        low_col = self._get_color_for(hue, low_value, chroma, depth+1)
        if (low_value == value):
            return low_col
        high_col = self._get_color_for(hue, high_value, chroma, depth+1)
        mix = color.Mix([high_col.p(value - low_value), low_col.p(high_value - value)])
        return MunsellSample(mix.spectrum, hue, value, chroma)

    def nearest_chromas(self, chroma):
        # there's a chroma sample every 2 steps
        low_chroma = math.floor(chroma * 1/2) * 2.0
        high_chroma = math.ceil(chroma * 1/2) * 2.0
        return low_chroma, high_chroma

    def mix_to_chroma(self, hue, value, chroma, depth=0):
        low_chroma, high_chroma = self.nearest_chromas(chroma)
        low_col = self._get_color_for(hue, value, low_chroma, depth+1)
        if (low_chroma == chroma):
            return low_col
        high_col = self._get_color_for(hue, value, high_chroma, depth+1)
        mix = color.Mix([high_col.p(chroma - low_chroma), low_col.p(high_chroma - chroma)])
        return MunsellSample(mix.spectrum, hue, value, chroma)

    def _get_color_for(self, hue, value, chroma, depth=0):
        if depth >= 4:
            raise MissingColorError(
                "Unable to get color for {0}".format(name_for_color(hue, value, chroma)),
                hue, value, chroma)

        # This is a bullshit tree-recursive way to do this;
        # probably you could triangulate colors somehow, but
        # axis-units are not simply convertable, and this is functional.
        hue = numerical_hue(hue)
        if hue == 0:
            hue = 100

        if self.color_sample_exists(hue):
            if self.color_sample_exists(hue, value):
                if self.color_sample_exists(hue, value, chroma):
                    return self.color_sample(hue, value, chroma)
                else:
                    return self.mix_to_chroma(hue, value, chroma, depth)
            else:
                return self.mix_to_value(hue, value, chroma, depth)
        else:
            return self.mix_to_hue(hue, value, chroma, depth)


    # For many, many, many applications, we want to gracefully fail
    # when there is no color at the desired chroma; here, if a color
    # is non-interpolatable, we try again at a lower chroma.
    def get_color_for(self, hue, value, chroma):
        try:
            return self._get_color_for(hue, value, chroma, 0)
        except MissingColorError as err:
            failed_chroma = err.args[3]
            if failed_chroma < 1:
                raise
            else:
                lower_chroma, _ = self.nearest_chromas(chroma - 0.01)
                return self.get_color_for(hue, value, lower_chroma)


###
# Here's the fun stuff! Lighting, ladders, mixing, etc.

class MunsellColor(color.Color):
    def __init__(self, hue, value, chroma):
        self.name = name_for_color(hue, value, chroma)
        self.hue = numerical_hue(hue)
        self.value = value
        self.chroma = chroma
        self.actual_chroma = chroma
        self.proportion = 1
        self.imprecise = False
        self.clipped = False

    @property
    def spectrum(self):
        col = colors.get_color_for(self.hue, self.value, self.chroma)
        if col.chroma != self.chroma:
            self.imprecise = True
            self.actual_chroma = col.chroma
            self.name = col.name
        return col.spectrum

    def complement(self):
        return MunsellColor(complement(self.hue), self.value, self.chroma)

    def in_sunlight(self):
        return MunsellColor(self.hue, 2 + self.value * 0.8, self.chroma)

    def in_shadow(self, sky_color=None):
        if not sky_color:
            sky_color = MunsellColor("5PB", self.value * 0.8, 10)
        shade = MunsellColor(self.hue, self.value * 0.8, self.chroma)
        return color.Mix([sky_color.p(0.3), shade])

    def stats_dict(self):
        d = super().stats_dict()
        d["hue"] = self.hue
        d["value"] = self.value
        d["chroma"] = self.actual_chroma
        d["attempted_chroma"] = self.chroma
        return d

def complement(hue):
    return (hue + 50) % 100


def numerical_mix(a, b, proportion, shortest_route=True):

    def mod_additive_proportional(a, b, proportion, mod=100):
        if abs(a - b) < 50:
            return additive_proportional(a, b, proportion)
        else:
            return long_way_additive_proportional(a, b, proportion)

    def long_way_additive_proportional(a, b, proportion, mod=100):
        if a < b:
            return additive_proportional(a+mod, b, proportion) % mod
        else:
            return additive_proportional(a, b+mod, proportion) % mod

    def additive_proportional(a, b, proportion):
        return a * proportion + b * (1 - proportion)

    if shortest_route:
        hue = mod_additive_proportional(a.hue, b.hue, proportion)
    else:
        hue = long_way_additive_proportional(a.hue, b.hue, proportion)

    value = additive_proportional(a.value, b.value, proportion)
    chroma = additive_proportional(a.chroma, b.chroma, proportion)
    return MunsellColor(hue, value, chroma)

def numerical_ladder(a, b, steps):
    count = steps - 1
    return [numerical_mix(b, a, float(x)/count) for x in range(steps)]

def mix_ladder(a, b, steps):
    count = steps - 1.0
    return [color.Mix([b.p(x/count), a.p((count-x)/count)]) for x in range(steps)]

def rainbow(value, chroma, steps, offset=0):
    a = MunsellColor(offset, value, chroma)
    b = MunsellColor((offset - .01) % 100, value, chroma)
    return [numerical_mix(b, a, float(x)/steps, False) for x in range(steps)]


def page(hue, value_steps=10, chroma_steps=10):
    return [[MunsellColor(hue, value, chroma) for chroma in np.arange(0, 16.1, 16.0/(chroma_steps-1))] for value in np.arange(1, 9.1, 8.0/(value_steps-1))]



colors = InterpolatedMunsellColorDatabase()
