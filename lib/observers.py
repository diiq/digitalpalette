import numpy as np
import csv
import os

# Currently using Stiles and Burch observer functions; I know that's
# weird, but I coudn't find CIE rgb CMFs, only XYZ. From
# http://cvrl.ioo.ucl.ac.uk/

data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), './rgb10.csv')

def load_observers(file=data_file):
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        arr = np.array([row for row in reader])
    arr = arr.transpose()
    red = np.array([float(x) for x in arr[1]])
    green = np.array([float(x) for x in arr[2]])
    blue = np.array([float(x) for x in arr[3]])
    return red*.21, green*.45, blue*.89

frequencies = np.array(range(390, 831, 5))
red, green, blue = load_observers()
