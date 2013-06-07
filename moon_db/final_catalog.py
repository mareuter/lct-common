#!/usr/bin/python2.7
from symbol import except_clause

# This script will handle creating the actual catalog database for the 
# Lunar information

# Variables that get the fields from the shape file.
# Feature name without diacritical marks
CLEAN_NAME = 1
# Feature diameter
DIAMETER = 4
# Feature center longitude
CENTER_LONG = 5
# Feature center latitude
CENTER_LAT = 6
# Feature type
FEATURE_TYPE = 7
# Minimum and maximum longitude
MIN_LONG = 10
MAX_LONG = 11
# Minimum and maximum latitude
MIN_LAT = 12
MAX_LAT = 13
# Quadrant name and code
QUAD_NAME = 16
QUAD_CODE = 17
# Files for database creation
SHAPEFILE_NAME = "MOON_nomenclature.shp"
INITIAL_CAT = "initial_cat.txt"
OUTPUT_DB = "moon.db"
ANDROID_OUTPUT_DB = "moon_android.db"
# Lunar club codes: 1 - Lunar, 2 - Lunar II, 3 - Both
LUNAR_CODES = (1, 2, 3)
LUNAR_CODE_NAMES = ("Lunar", "LunarII", "Both")
# Lunar club object types
LUNAR_CLUB_TYPES = ("Naked Eye", "Binocular", "Telescopic")

# Get the required list of feature from the initial catalog
cat_file = open(INITIAL_CAT, "r")
feature_dict = {}
for line in cat_file:
    values = line.split('|')
    code = int(values[0]) 
    if code in LUNAR_CODES:
        # If part of Lunar club, get object type
        try:
            otype = int(values[3])
        except IndexError:
            otype = 3
        feature_dict[values[1]] = (code, otype)
cat_file.close()

def fix_longitude(longitude):
    if 180.0 <= longitude < 360.0:
        # West is negative
        return longitude - 360.0
    else:
        return longitude

# Open and read through the shapefile looking for the features in 
# the previously filled dict
import shapefile
import math
records = []
r = shapefile.Reader(SHAPEFILE_NAME)
for sr in r.shapeRecords():
    feature_name = sr.record[CLEAN_NAME]
    if feature_name in feature_dict:
        feature_dia = sr.record[DIAMETER]
        feature_lat = sr.record[CENTER_LAT]
        long = sr.record[CENTER_LONG]
        feature_long = fix_longitude(long)
        feature_type = sr.record[FEATURE_TYPE].split(',')[0]
        feature_delta_lat = math.fabs(sr.record[MAX_LAT] - sr.record[MIN_LAT]) 
        feature_delta_long = math.fabs(sr.record[MAX_LONG] - sr.record[MIN_LONG])
        feature_quad_name = sr.record[QUAD_NAME]
        feature_quad_code = sr.record[QUAD_CODE]
        temp = feature_dict[feature_name][0] - 1
        feature_lunar_code = LUNAR_CODE_NAMES[temp] 
        try:
            feature_lunar_club_type = LUNAR_CLUB_TYPES[feature_dict[feature_name][1]]
        except IndexError:
            feature_lunar_club_type = None

        records.append((feature_name, feature_dia,
                       feature_lat, feature_long, 
                       feature_delta_lat, feature_delta_long,
                       feature_type, feature_quad_name, feature_quad_code,
                       feature_lunar_code, feature_lunar_club_type))

# Adding extra records for lunar domes which do not exist in the shapefile
# Feature diameter is set a longitudinal diameter. To find delta latitude and
# delta longitude, the mean lunar radius of 1737.1 km was used and the given 
# diameter of the feature was used.
arago_alpha = ("Arago Alpha", 24.0, 7.466666, 21.416666, 0.4947, 0.7916, 
               "Dome", "Julius Caesar", "LAC-60", "LunarII", None)
arago_beta = ("Arago Beta", 23.29, 6.083333, 19.93333, 0.6597, 0.7682,
              "Dome", "Julius Caesar", "LAC-60", "LunarII", None)
cauchy_omega = ("Cauchy Omega", 9.6, 7.23333, 38.316666, 0.3166, 0.3166, 
                "Dome", "Taruntius", "LAC-61", "LunarII", None)
cauchy_tau = ("Cauchy Tau", 10.2, 7.53333, 36.73333, 0.3364, 0.3364, 
              "Dome", "Taruntius", "LAC-61", "LunarII", None)
kies_pi = ("Kies Pi", 13.0, -26.93333, -24.23333, 0.4288, 0.4288,
           "Dome", "Pitatus", "LAC-94", "LunarII", None)
milichius_pi = ("Milichius Pi", 10.0, 10.2, -31.2, 0.3298, 0.3298, 
                "Dome", "Kepler", "LAC-57", "LunarII", None)

records.append(arago_alpha)
records.append(arago_beta)
records.append(cauchy_omega)
records.append(cauchy_tau)
records.append(kies_pi)
records.append(milichius_pi)

# Setup SQL table
features_table = []
features_table.append("Id INTEGER PRIMARY KEY")
features_table.append("Name TEXT")
features_table.append("Diameter REAL")
features_table.append("Latitude REAL")
features_table.append("Longitude REAL")
features_table.append("Delta_Latitude REAL")
features_table.append("Delta_Longitude REAL")
features_table.append("Type TEXT")
features_table.append("Quad_Name TEXT")
features_table.append("Quad_Code TEXT")
features_table.append("Lunar_Code TEXT")
features_table.append("Lunar_Club_Type TEXT")

# Create the database for the feature information
import sqlite3

def write_lunar_features(c, table, recs):
    c.execute("DROP TABLE IF EXISTS Features")
    c.execute("CREATE TABLE Features(%s)" % ",".join(table))
    c.executemany("INSERT INTO Features VALUES(null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    recs)

con = sqlite3.connect(OUTPUT_DB)
con.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
with con:
    cur = con.cursor()
    write_lunar_features(cur, features_table, records)
    cur.close()

# Write Android version of the database
con = sqlite3.connect(ANDROID_OUTPUT_DB)
con.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
# Change title of feature table primary key
features_table[0] = "_id INTEGER PRIMARY KEY"
with con:
    cur = con.cursor()
    write_lunar_features(cur, features_table, records)
    cur.execute("DROP TABLE IF EXISTS android_metadata")
    cur.execute("CREATE TABLE android_metadata (locale TEXT DEFAULT 'en_US')")
    cur.execute("INSERT INTO android_metadata VALUES('en_US')")
    cur.close()


