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


# Munsell hues are almost-numbered; for the sake of doing math, we'll
# have to convert the number+letters hue into just-a-number between 1
# and 100; 50 steps takes you to a (pretty darn exact) complement.

HUE_NAMES = ['R', 'YR', 'Y', 'GY', 'G', 'BG', 'B', 'PB', 'P', 'RP', "XXXXX"]
HUE_NAMES_TO_NUMBERS = dict((v, 10 * k) for k, v in enumerate(HUE_NAMES))
hue_regex = re.compile('(\d+(\.\d+)?)([RYGBP]{1,2})')
def numerical_hue(hue):
    """Parse a hue name into a float from 0 to 100."""
    if isinstance(hue, str):
        match = hue_regex.match(hue)
        return float(match[1]) + HUE_NAMES_TO_NUMBERS[match[3]]
    return hue

def name_for_hue(hue):
    return "{0:1.1f}{1}".format(hue % 10, HUE_NAMES[int(math.floor(hue / 10))])

def name_for_color(hue, value, chroma):
    return "{0} {1:1.1f}/{2:1.1f}".format(name_for_hue(hue), value, chroma)

# The Munsell space is continuous, but we only have samples. Define
# methods for interpolating.

def nearest_hues(hue):
    # There is a sample hue every 2.5 steps, so round to the nearest 2.5
    low_hue = math.floor(hue * 1/2.5)*2.5
    high_hue = (math.ceil(hue * 1/2.5)*2.5) % 100
    return low_hue, high_hue

def mix_to_hue(hue, value, chroma, depth=0):
    low_hue, high_hue = nearest_hues(hue)
    low_col = _get_color_for(low_hue, value, chroma, depth+1)
    if (low_hue == hue):
        return low_col
    high_col = _get_color_for(high_hue, value, chroma, depth+1)
    mix = color.Mix([high_col.p(hue - low_hue), low_col.p(high_hue - hue)]).to_color()
    mix.hue = hue
    mix.value = value
    mix.chroma = chroma
    mix.name = name_for_color(hue, value, chroma)
    return mix

def nearest_values(value):
    # TODO sometimes there's an 8.5
    # there's a value sample every 1 step but not at 1
    low_value = math.floor(value)
    if low_value == 1.0:
        low_value = 0
    high_value = math.ceil(value)
    if high_value == 1.0:
        high_value = 2.0
    return low_value, high_value

def mix_to_value(hue, value, chroma, depth=0):
    low_value, high_value = nearest_values(value)
    low_col = _get_color_for(hue, low_value, chroma, depth+1)
    if (low_value == value):
        return low_col
    high_col = _get_color_for(hue, high_value, chroma, depth+1)
    mix = color.Mix([high_col.p(value - low_value), low_col.p(high_value - value)]).to_color()
    mix.hue = hue
    mix.value = value
    mix.chroma = chroma
    mix.name = name_for_color(hue, value, chroma)
    return mix

def nearest_chromas(chroma):
    # there's a chroma sample every 2 steps
    low_chroma = math.floor(chroma * 1/2) * 2.0
    high_chroma = math.ceil(chroma * 1/2) * 2.0
    return low_chroma, high_chroma

def mix_to_chroma(hue, value, chroma, depth=0):
    low_chroma, high_chroma = nearest_chromas(chroma)
    low_col = _get_color_for(hue, value, low_chroma, depth+1)
    if (low_chroma == chroma):
        return low_col
    high_col = _get_color_for(hue, value, high_chroma, depth+1)
    mix = color.Mix([high_col.p(chroma - low_chroma), low_col.p(high_chroma - chroma)]).to_color()
    mix.hue = hue
    mix.value = value
    mix.chroma = chroma
    mix.name = name_for_color(hue, value, chroma)
    return mix

def color_sample_exists(hue=None, value=None, chroma=None):
    if (value == 1):
        return False
    pairs = [["hue=?", hue], ["value=?", value], ["chroma=?", chroma]]
    string = "SELECT i FROM colors WHERE " + " AND ".join([str(q[0]) for q in pairs if q[1] != None])
    vals = [q[1] for q in pairs if q[1] != None]
    return not not CURSOR.execute(string, vals).fetchone()

def color_sample(hue, value, chroma):
    ind = CURSOR.execute(
        "SELECT i FROM colors WHERE hue=? AND value=? AND chroma=?",
        (hue, value, chroma)).fetchone()[0]
    return COLORS[ind]

def max_chroma_sample(hue, value):
    ind = CURSOR.execute(
        "SELECT i FROM colors WHERE hue=? AND value=? ORDER BY chroma DESC",
        (hue, value)).fetchone()
    ind = ind[0]
    return COLORS[ind]

class MissingColorError(Exception): pass

def _get_color_for(hue, value, chroma, depth=0):
    if depth >= 4:
        raise MissingColorError("Unable to get color for {0}".format(name_for_color(hue, value, chroma)), hue, value, chroma)
    # This is a bullshit tree-recursive way to do this;
    # probably you could triangulate colors somehow, but
    # axis-units are not simply convertable, and this is functional.
    hue = numerical_hue(hue)
    if hue == 0:
        hue = 100

    if color_sample_exists(hue):
        if color_sample_exists(hue, value):
            if color_sample_exists(hue, value, chroma):
                return color_sample(hue, value, chroma)
            else:
                return mix_to_chroma(hue, value, chroma, depth)
        else:
            return mix_to_value(hue, value, chroma, depth)
    else:
        return mix_to_hue(hue, value, chroma, depth)


def get_color_for(hue, value, chroma):
    try:
        return _get_color_for(hue, value, chroma, 0)
    except MissingColorError as err:
        failed_chroma = err.args[3]
        #print(err.args)
        if failed_chroma < 1:
            raise
        else:
            #print("Unable to get color for {0}".format(name_for_color(hue, value, chroma)))
            lower_chroma, _ = nearest_chromas(chroma - 0.01)
            #print("Trying color {0}".format(name_for_color(hue, value, lower_chroma)))
            return get_color_for(hue, value, lower_chroma)


# We'll need to rapidly search by hue, value, and chroma, so we create
# an in-memory database of color samples.

def load_colors(file=DATA_FILE):
    colors = []
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        arr = [row for row in reader]
    for row in arr[1:1488]:
        colors.append(color.Color([float(f) for f in row[8:8+36]], 1, row[1], numerical_hue(row[2]), *[float(f) for f in row[3:5]]))
    return colors

def create_database():
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute('CREATE TABLE colors (hue float, value float, chroma float, i integer)')
    return c

def insert_colors():
    CURSOR.executemany("INSERT INTO colors VALUES (?, ?, ?, ?)", [(color.hue, color.value, color.chroma, i) for i, color in enumerate(COLORS)])
    insert_overchromas()
    insert_whites_and_blacks()
    insert_grays()


# Use titanium white and bone black for 0 and 10 values. Lies.
def insert_whites_and_blacks():
    white = COLORS[1485]
    black = COLORS[1486]
    i = len(COLORS) - 1
    for doublehue in range(5, 201, 5):
        for chroma in range(0, 6, 2):
            hue = doublehue / 2.0

            nblack = black.p(1)
            nblack.hue = hue
            nblack.value = 0
            nblack.chroma = chroma
            COLORS.append(nblack)
            i += 1
            CURSOR.execute("INSERT INTO colors VALUES (?, ?, ?, ?)", (hue, 0, chroma, i))

            nwhite = white.p(1)
            nwhite.hue = hue
            nwhite.value = 10
            nwhite.chroma = chroma
            COLORS.append(nwhite)
            i += 1
            CURSOR.execute("INSERT INTO colors VALUES (?, ?, ?, ?)", (hue, 10, chroma, i))

# I really need spectra for real munsell grays, but this is a start, I
# guess? Some are still 2% off pure, though, and that is very visible.
def how_gray(color):
    rgb = color.to_rgb()
    diff = max(rgb) - min(rgb)
    return 1 - diff

def better(mix_a, mix_b):
    return how_gray(mix_a) > how_gray(mix_b)

def find_grayest(a, b):
    mix = color.Mix([a, b]).to_color()
    ap = 1
    new_mix = color.Mix([a.p(1.05), b]).to_color()
    # todo binary search
    if better(new_mix, mix):
        while better(new_mix, mix):
            ap += .05
            mix = new_mix
            new_mix = color.Mix([a.p(ap), b]).to_color()
    else:
        new_mix = color.Mix([a.p(0.95), b]).to_color()
        while better(new_mix, mix):
            ap -= .05
            mix = new_mix
            new_mix = color.Mix([a.p(ap), b]).to_color()
    return mix

def insert_grays():
    chroma = 2
    i = len(COLORS) - 1
    for doublehue in range(5, 201, 5):
        hue = doublehue / 2.0
        for value in range(0, 10):
            this_color = get_color_for(hue, value, chroma)
            comp = get_color_for(complement(hue), value, chroma)
            mix = find_grayest(this_color, comp)
            mix.hue = hue
            mix.value = value
            mix.chroma = 0
            mix.name = name_for_color(hue, value, 0)
            mix.spectrum = [sum(mix.spectrum)/len(mix.spectrum)] * len(mix.spectrum)
            COLORS.append(mix)
            i += 1
            CURSOR.execute("INSERT INTO colors VALUES (?, ?, ?, ?)", (hue, value, 0, i))


def calculate_overchroma(hue, value, direction=-1):
    current = max_chroma_sample(hue, value)
    if not color_sample_exists(hue, value + direction * 2):
        return
    a_col = max_chroma_sample(hue, value + direction * 1)
    if a_col.chroma < current.chroma:
        return
    b_col = max_chroma_sample(hue, value + direction * 2)
    if b_col.chroma < current.chroma:
        return
    if b_col.chroma < a_col.chroma:
        a_col = color_sample(hue, value + direction * 1, b_col.chroma)
    if b_col.chroma > a_col.chroma:
        b_col = color_sample(hue, value + direction * 2, a_col.chroma)


    c = color.Color(np.add(np.subtract(a_col.spectrum, b_col.spectrum), a_col.spectrum).clip(min=0))
    c.hue = hue
    c.value = value
    c.chroma = a_col.chroma
    c.name = name_for_color(hue, value, a_col.chroma)
    return c


def insert_overchromas():
    i = len(COLORS) - 1
    insertions = []
    for doublehue in range(5, 201, 5):
        hue = doublehue / 2.0
        for value in range(2, 10):
            if value > 2:
                c = calculate_overchroma(hue, value, -1)
                if c:
                    COLORS.append(c)
                    i += 1
                    insertions.append([hue, value, c.chroma, i])
            if value < 8:
                c = calculate_overchroma(hue, value, 1)
                if c:
                    COLORS.append(c)
                    i += 1
                    insertions.append([hue, value, c.chroma, i])

    for it in insertions:
        CURSOR.execute("INSERT INTO colors VALUES (?, ?, ?, ?)", it)


# Actual mixing and stuff

class MunsellColor():
    def __init__(self, hue, value, chroma):
        self.hue = numerical_hue(hue)
        self.value = value
        self.chroma = chroma

    def color(self):
        return get_color_for(self.hue, self.value, self.chroma)

    def p(self, v):
        return self.color().p(v)

    def swatch(self):
        return self.color().swatch()

    def complement(self):
        return MunsellColor(complement(self.hue), self.value, self.chroma)

    def sunlight(self):
        return MunsellColor(self.hue, 2 + self.value * 0.8, self.chroma)

    def shadow(self, sky_color=None):
        if not sky_color:
            sky_color = MunsellColor("5PB", self.value * 0.8, 10)
        shade = MunsellColor(self.hue, self.value * 0.8, self.chroma)
        return color.Mix([sky_color.p(0.3), shade.color()]).to_color()

    @property
    def proportion(self):
        return self.color().proportion


def complement(hue):
    return (hue + 50) % 100

def additive_proportional(a, b, proportion):
    return a * proportion + b * (1 - proportion)

def additive_proportional_color(a, b, proportion):
    hue = additive_proportional(a.hue, b.hue, proportion)
    value = additive_proportional(a.value, b.value, proportion)
    chroma = additive_proportional(a.chroma, b.chroma, proportion)
    return MunsellColor(hue, value, chroma)

def numerical_ladder(a, b, steps):
    # todo: never goes through 0() even if that's the short road
    count = steps - 1
    return [additive_proportional_color(b, a, float(x)/count) for x in range(steps)]

def mix_ladder(a, b, steps):
    count = steps - 1.0
    return [color.Mix([b.p(x/count), a.p((count-x)/count)]).to_color() for x in range(steps)]



COLORS = load_colors()
CURSOR = create_database()
insert_colors()
