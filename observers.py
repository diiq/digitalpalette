import numpy as np
import csv


# Currently using Stiles and Burch observer functions; I know that's
# weird, but I coudn't find CIE rgb CMFs, only XYZ. From
# http://cvrl.ioo.ucl.ac.uk/

def load_observers(file='./rgb10.csv'):
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
