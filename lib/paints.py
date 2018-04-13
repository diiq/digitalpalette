import csv
import numpy as np
import math
import os

import lib.color as color

# Data from 10.18236/econs2.201410 . It's shite and I hate it.
# Same data as https://chsopensource.org/tools-2/pigments-checker/
# The data I have are poorly calibrated; reflectance never drops below
# 20% and often goes over 100%. These factors attempt to correct for
# that, but work imperfectly.
OFFSET = 18
DIVISOR = 750
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), './paints.csv')

def load_paints(file=data_file):
    paints = {}
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        arr = np.array([row for row in reader])
    arr = arr.transpose()
    spectra, frequencies = arr[1:, :], np.array([float(f) for f in arr[0, 1:]])
    for paint in spectra:
        paints[paint[0]] = (np.array([min(100+OFFSET, max(float(f), OFFSET + .001)) for f in paint[1:]]) - OFFSET)/DIVISOR

    desired_frequencies = range(380, 731, 10)
    for name in paints:
        paints[name] = np.array([color.interpolate(frequencies, paints[name], x) for x in desired_frequencies])

    frequencies = np.array(desired_frequencies)
    return paints, frequencies


paints, frequencies = load_paints()


burnt_umber = color.Color(paints['burntumber'], 1, "Burnt Umber")
raw_umber = color.Color(paints['rawumber'], 1, "Raw Umber")
burnt_sienna = color.Color(paints['burntsienna'], 1, "Burnt Sienna")
raw_sienna = color.Color(paints['rawsienna'], 1, "Raw Sienna")
red_ochre = color.Color(paints['redochre'], 1, "Red Ochre")
red_lead = color.Color(paints['redlead'], 1, "Red Lead")
cadmium_red = color.Color(paints['cadmiumred'], 1, "Cadmium Red")
alizarin = color.Color(paints['alizarin'], 1, "Alizarin")
madder_lake = color.Color(paints['madderlake'], 1, "Madder Lake")
lacdye = color.Color(paints['lacdye'], 1, "Lac dye")
carmine_lake = color.Color(paints['carminelake'], 1, "Carmine Lake")
vermilion = color.Color(paints['vermilion'], 1, "Vermilion")
real_gar = color.Color(paints['realgar'], 1, "Real Gar")
yellow_lake = color.Color(paints['yellowlakeresed'], 1, "Yellow Lake")
massicot = color.Color(paints['massicot'], 1, "Massicot")
yellow_ochre = color.Color(paints['yellowochre'], 1, "Yellow Ochre")
gamboge = color.Color(paints['gamboge'], 1, "Gamboge")
naples_yellow = color.Color(paints['naplesyellow'], 1, "Naples Yellow")
lead_tin_yellow = color.Color(paints['leadtinyellow..II'], 1, "Lead Tin Yellow")
saffron = color.Color(paints['saffron'], 1, "Saffron")
orpiment = color.Color(paints['orpiment'], 1, "Orpiment")
cobalt_yellow = color.Color(paints['cobaltyellow'], 1, "Cobalt Yellow")
cadmium_yellow = color.Color(paints['cadmiumyellow'], 1, "Cadmiumy Yellow")
chrome_green = color.Color(paints['chromegreen'], 1, "Chrome Green")
cobalt_green = color.Color(paints['cobaltgreen'], 1, "Cobalt Green")
cadmium_green = color.Color(paints['cadmiumgreen'], 1, "Cadmium Green")
green_earth = color.Color(paints['greenearth'], 1, "Green Earth")
viridian = color.Color(paints['viridian'], 1, "Viridian")
phthalo_green = color.Color(paints['phthalogreen'], 1, "Phthalo Green")
verdigris = color.Color(paints['verdigris'], 1, "Verdigris")
malachite = color.Color(paints['malachite'], 1, "Malachite")
bluebice = color.Color(paints['bluebice'], 1, "Blue Bice")
cobalt_blue = color.Color(paints['cobaltblue'], 1, "Cobalt Blue")
azurite = color.Color(paints['azurite'], 1, "Azurite")
egyptian_blue = color.Color(paints['egyptianblue'], 1, "Egyptian Blue")
ultramarine = color.Color(paints['ultramarine'], 1, "Ultramarine")
phthalo_blue = color.Color(paints['phthaloblue'], 1, "Phthaloblue")
smalt = color.Color(paints['smalt'], 1, "Smalt")
indigo = color.Color(paints['indigo'], 1, "Indigo")
maya_blue = color.Color(paints['mayablue'], 1, "Mayablue")
prussian_blue = color.Color(paints['prussianblue'], 1, "Prussian Blue")
cobalt_violet = color.Color(paints['cobaltviolet'], 1, "Cobalt Violet")
ivory_black = color.Color(paints['ivoryblack'], 1, "Ivory Black")
vine_black = color.Color(paints['vineblack'], 1, "Vine Black")
bone_black = color.Color(paints['boneblack'], 1, "Bone Black")
lamp_black = color.Color(paints['lampblaxk'], 1, "Lamp Black")
gypsum = color.Color(paints['gypsum'], 1, "Gypsum")
chalk = color.Color(paints['chalk'], 1, "Chalk")
lead_white = color.Color(paints['leadwhite'], 1, "Lead White")
zinc_white = color.Color(paints['zincwhite'], 1, "Zinc White")
titanium_white = color.Color(paints['titaniumwhite'], 1, "Titanium White")
lithopone = color.Color(paints['lithopone'], 1, "Lithopone")


color_names = ["lithopone",
               "titanium_white",
               "zinc_white",
               "lead_white",
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
               "raw_umber",
               "burnt_umber"]
