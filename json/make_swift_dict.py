import csv

ifile = "tz_coords.csv"
with open(ifile) as tzdata:
    csv_reader = csv.reader(tzdata)
    for row in csv_reader:
        if row[0].startswith('#'):
            continue
        print("\"{}\": ({}, {}),".format(row[0], row[1], row[2]))
