import csv
import numpy as np
import math
import color


# The data I have are poorly calibrated; reflectance never drops below
# 20% and often goes over 100%. These factors attempt to correct for
# that, but work imperfectly.
OFFSET = 18
DIVISOR = 750

def interpolate(xs, ys, desired_x):
    before = np.where(xs < desired_x)[0][-1]
    after = np.where(xs > desired_x)[0][0]
    # cheating, but doing prop'ly probably unnecessary given how small
    # the steps are in the original data.
    return (ys[before] + ys[after]) / 2


def load_paints(file='./paints.csv'):
    paints = {}
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        arr = np.array([row for row in reader])
    arr = arr.transpose()
    spectra, frequencies = arr[1:, :], np.array([float(f) for f in arr[0, 1:]])
    for paint in spectra:
        paints[paint[0]] = (np.array([min(100+OFFSET, max(float(f), OFFSET + .001)) for f in paint[1:]]) - OFFSET)/DIVISOR

    desired_frequencies = range(390, 831, 5)
    for name in paints:
        paints[name] = np.array([interpolate(frequencies, paints[name], x) for x in desired_frequencies])

    frequencies = np.array(desired_frequencies)
    return paints, frequencies


paints, frequencies = load_paints()


burnt_umber = color.Color(paints['burntumber'], 1, "Burnt umber")
raw_umber = color.Color(paints['rawumber'], 1, "Raw umber")
burnt_sienna = color.Color(paints['burntsienna'], 1, "Burnt Sienna")
raw_sienna = color.Color(paints['rawsienna'], 1, "rawsienna")
red_ochre = color.Color(paints['redochre'], 1, "redochre")
red_lead = color.Color(paints['redlead'], 1, "redlead")
cadmium_red = color.Color(paints['cadmiumred'], 1, "cadmiumred")
alizarin = color.Color(paints['alizarin'], 1, "alizarin")
madder_lake = color.Color(paints['madderlake'], 1, "madderlake")
lacdye = color.Color(paints['lacdye'], 1, "lacdye")
carmine_lake = color.Color(paints['carminelake'], 1, "carminelake")
vermilion = color.Color(paints['vermilion'], 1, "vermilion")
real_gar = color.Color(paints['realgar'], 1, "realgar")
yellow_lake = color.Color(paints['yellowlake'], 1, "yellow lake")
massicot = color.Color(paints['massicot'], 1, "massicot")
yellow_ochre = color.Color(paints['yellowochre'], 1, "yellowochre")
gamboge = color.Color(paints['gamboge'], 1, "gamboge")
naples_yellow = color.Color(paints['naplesyellow'], 1, "naplesyellow")
lead_tin_yellow = color.Color(paints['leadtinyellow..II'], 1, "leadtinyellow")
saffron = color.Color(paints['saffron'], 1, "saffron")
orpiment = color.Color(paints['orpiment'], 1, "orpiment")
cobalt_yellow = color.Color(paints['cobaltyellow'], 1, "cobaltyellow")
cadmium_yellow = color.Color(paints['cadmiumyellow'], 1, "cadmiumyellow")
chrome_green = color.Color(paints['chromegreen'], 1, "chromegreen")
cobalt_green = color.Color(paints['cobaltgreen'], 1, "cobaltgreen")
cadmium_green = color.Color(paints['cadmiumgreen'], 1, "cadmiumgreen")
green_earth = color.Color(paints['greenearth'], 1, "greenearth")
viridian = color.Color(paints['viridian'], 1, "viridian")
phthalo_green = color.Color(paints['phthalogreen'], 1, "phthalogreen")
verdigris = color.Color(paints['verdigris'], 1, "verdigris")
malachite = color.Color(paints['malachite'], 1, "malachite")
bluebice = color.Color(paints['bluebice'], 1, "bluebice")
cobalt_blue = color.Color(paints['cobaltblue'], 1, "cobaltblue")
azurite = color.Color(paints['azurite'], 1, "azurite")
egyptian_blue = color.Color(paints['egyptianblue'], 1, "egyptianblue")
ultramarine = color.Color(paints['ultramarine'], 1, "ultramarine")
phthalo_blue = color.Color(paints['phthaloblue'], 1, "phthaloblue")
smalt = color.Color(paints['smalt'], 1, "smalt")
indigo = color.Color(paints['indigo'], 1, "indigo")
maya_blue = color.Color(paints['mayablue'], 1, "mayablue")
prussian_blue = color.Color(paints['prussianblue'], 1, "prussianblue")
cobalt_violet = color.Color(paints['cobaltviolet'], 1, "cobaltviolet")
ivory_black = color.Color(paints['ivoryblack'], 1, "ivoryblack")
vine_black = color.Color(paints['vineblack'], 1, "vineblack")
bone_black = color.Color(paints['boneblack'], 1, "boneblack")
lamp_black = color.Color(paints['lampblaxk'], 1, "lampblack")
gypsum = color.Color(paints['gypsum'], 1, "gypsum")
chalk = color.Color(paints['chalk'], 1, "chalk")
lead_white = color.Color(paints['leadwhite'], 1, "leadwhite")
zinc_white = color.Color(paints['zincwhite'], 1, "zincwhite")
titanium_white = color.Color(paints['titaniumwhite'], 1, "titaniumwhite")
lithopone = color.Color(paints['lithopone'], 1, "lithopone")


color_names = ["lithopone",
               "titanium_white",
               "zinc_white",
               "lead_white",
               "chalk",
               "gypsum",
               "lamp_black",
               "bone_black",
               "vine_black",
               "ivory_black",
               "cobalt_violet",
               "prussian_blue",
               "maya_blue",
               "indigo",
               "smalt",
               "phthalo_blue",
               "ultramarine",
               "egyptian_blue",
               "azurite",
               "cobalt_blue",
               "bluebice",
               "malachite",
               "verdigris",
               "phthalo_green",
               "viridian",
               "green_earth",
               "cadmium_green",
               "cobalt_green",
               "chrome_green",
               "cadmium_yellow",
               "cobalt_yellow",
               "orpiment",
               "saffron",
               "lead_tin_yellow",
               "naples_yellow",
               "gamboge",
               "yellow_ochre",
               "massicot",
               "yellow_lake",
               "real_gar",
               "vermilion",
               "carmine_lake",
               "lacdye",
               "madder_lake",
               "alizarin",
               "cadmium_red",
               "red_lead",
               "red_ochre",
               "raw_sienna",
               "burnt_sienna",
               "raw_umber",
               "burnt_umber"]
