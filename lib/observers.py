import numpy as np
import csv
import os

# http://www.munsellcolourscienceforpainters.com/MunsellResources/MunsellResources.html

data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), './rgb10.csv')

def load_observers(file=data_file):
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        arr = np.array([row for row in reader])
    red = np.array([float(x) for x in arr[1][0:]])
    green = np.array([float(x) for x in arr[2][0:]])
    blue = np.array([float(x) for x in arr[3][0:]])
    return red, green, blue

frequencies = np.array(range(380, 731, 10))
red, green, blue = load_observers()
