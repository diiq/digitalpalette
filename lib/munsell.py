# coding: utf-8
import csv
import numpy as np
import math
import os
import re

import lib.color as color
import lib.observers as observers
import pandas as pd

# Munsell reflectance curves are from
# http://www.munsellcolourscienceforpainters.com/MunsellResources/MunsellResources.html

DATA_FILE = './lib/munsell.csv'


# Munsell hues are almost-numbered; for the sake of doing math, we'll
# have to convert the number+letters hue into just-a-number between 1
# and 100; 50 steps takes you to a (pretty darn exact) complement.

HUE_NAMES = ['R', 'YR', 'Y', 'GY', 'G', 'BG', 'B', 'PB', 'P', 'RP']
HUE_NAMES = dict((v, 10 * k) for k, v in enumerate(HUE_NAMES))
hue_regex = re.compile('(\d+(\.\d+)?)([RYGBP]{1,2})')
def numerical_hue(hue):
    """Parse a hue name into a float from 0 to 100."""
    match = hue_regex.match(hue)
    return float(match[1]) + HUE_NAMES[match[3]]

# The Munsell space is continuous, but we only have samples. Define
# methods for interpolating.

def nearest_hues(hue):
    # There is a sample hue every 2.5 steps, so round to the nearest 2.5
    low_hue = math.floor(hue * 1/2.5)*2.5
    high_hue = (math.ceil(hue * 1/2.5)*2.5) % 100
    return low_hue, high_hue

def mix_to_hue(hue, value, chroma):
    low_hue, high_hue = nearest_hues(hue)
    low_col = get_color_for(low_hue, value, chroma)
    if (low_hue == hue):
        return low_col
    high_col = get_color_for(high_hue, value, chroma)
    mix = color.Mix([high_col.p(hue - low_hue), low_col.p(high_hue - hue)])
    mix.hue = hue
    mix.value = value
    mix.chroma = chroma
    return mix

def nearest_values(value):
    # there's a value sample every 1 step
    low_value = float(math.floor(value))
    high_value = float(math.ceil(value))
    return low_value, high_value

def mix_to_value(hue, value, chroma):
    low_value, high_value = nearest_values(value)
    low_col = get_color_for(hue, low_value, chroma)
    if (low_value == value):
        return low_col
    high_col = get_color_for(hue, high_value, chroma)
    mix = color.Mix([high_col.p(value - low_value), low_col.p(high_value - value)])
    mix.hue = hue
    mix.value = value
    mix.chroma = chroma
    return mix

def nearest_chromas(chroma):
    # there's a chroma sample every 2 steps
    low_chroma = math.floor(chroma * 1/2) * 2.0
    high_chroma = math.ceil(chroma * 1/2) * 2.0
    return low_chroma, high_chroma

def mix_to_chroma(hue, value, chroma):
    low_chroma, high_chroma = nearest_chromas(chroma)
    low_col = get_color_for(hue, value, low_chroma)
    if (low_chroma == chroma):
        return low_col
    high_col = get_color_for(hue, value, high_chroma)
    mix = color.Mix([high_col.p(chroma - low_chroma), low_col.p(high_chroma - chroma)])
    mix.hue = hue
    mix.value = value
    mix.chroma = chroma
    return mix


def complement(hue):
    return (hue + 50) % 100

# TODO: tests for this
# Grays/0 chroma for all hues
# Find the corners of the tree in the form of constraints
# Then it's a linear programming problem?


def load_colors(file=DATA_FILE):
    colors = []
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        arr = [row for row in reader]
    for row in arr[1:1486]:
        colors.append(color.Color([float(f) for f in row[8:8+36]], 1, row[1], row[2], *[float(f) for f in row[3:5]]))
    return colors

colors = load_colors()

pc = pd.DataFrame(
    [[color.hue, numerical_hue(color.hue), color.value, color.chroma, color] for color in colors],
    index=[color.name for color in colors],
    columns=["hue_name", "hue", "value", "chroma", "color"])


def get_color_for(hue, value, chroma):
    print("get", hue, chroma, value)
    # This is a bullshit tree-recursive way to do this;
    # probably you could triangulate colors somehow, but
    # axis-units are not simply convertable, and this is functional.
    if isinstance(hue, str):
        hue = numerical_hue(hue)
    if hue == 0:
        hue = 100

    options = pc[pc.hue == hue]
    if len(options) >= 1:
        options = pc[(pc.hue == hue) & (pc.value == value)]
        if len(options) >= 1:
            options = pc[(pc.hue == hue) & (pc.value == value) & (pc.chroma == chroma)]
            if len(options) >= 1:
                options = pc[(pc.hue == hue) & (pc.value == value) & (pc.chroma == chroma)]
                return options.color[0]
            else:
                return mix_to_chroma(hue, value, chroma).to_color()
        else:
            return mix_to_value(hue, value, chroma).to_color()
    else:
        return mix_to_hue(hue, value, chroma).to_color()
