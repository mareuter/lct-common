# This script creates an average location from every timezone given be the JSON file
# (no oceans) found here: https://github.com/evansiroky/timezone-boundary-builder/releases
import csv
import json
import sys

import numpy as np


def mean_lat_lon(cd):
    fcd = np.array(cd).flatten()
    lat = fcd[1::2]
    lon = fcd[::2]
    return np.mean(lat), np.mean(lon)


try:
    ifile = sys.argv[1]
except IndexError:
    print("Usage: make_tz_average.py <TZ JSON File>")
    sys.exit(254)

tz_data = None
with open(ifile) as json_data:
    tz_data = json.load(json_data)

csv_file = open("tz_coords.csv", "w+")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["#Timezone", "Latitude", "Longitude"])

for info in tz_data["features"]:
    tz_id = info["properties"]["tzid"]
    coords = info["geometry"]["coordinates"]
    lats = []
    lons = []
    for coord in coords:
        for c in coord:
            lat, lon = mean_lat_lon(c)
            lats.append(lat)
            lons.append(lon)
    mlat = np.mean(np.array(lats))
    mlon = np.mean(np.array(lons))
    csv_writer.writerow([tz_id, mlat, mlon])
