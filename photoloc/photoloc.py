#!/usr/bin/python
# ------------------------------------------------------------------------------------------------
#
#	photoloc.py
#
#	Version		   Date		Who		Description
#
#	01.00.00	  10/02/20	mjm		Initial version
#
#
# ------------------------------------------------------------------------------------------------
#
#	Note:	To run rawtherapee-cli.exe in batch mode:
#
#			$ rawtherapee-cli.exe -c <dir | file(s)>
#
# ------------------------------------------------------------------------------------------------

import csv
import datetime
import getopt
import logging
import os
import pdb
import string
import sys
import time
import traceback
from exif import Image

from geopy.geocoders import Nominatim
import time
from pprint import pprint


def get_address_by_location(latitude, longitude, language="en"):
    """This function returns an address as raw from a location
    will repeat until success"""
    # build coordinates string to pass to reverse() function
    coordinates = f"{latitude}, {longitude}"
    # sleep for a second to respect Usage Policy
    time.sleep(1)
    try:
        return app.reverse(coordinates, language=language).raw
    except Exception as err1:
        if debug:
            print("(get_address_by_location) ERROR: Exception: ", err1)
            print("(get_address_by_location) ERROR: Exception: Lat: ", latitude, ", Long: ", longitude)
        return get_address_by_location(latitude, longitude)


def usage():
    print("Usage:")
    print("    -p  <path> Starting path to search")
    print(r"        e.g.  -p \"C:\Users\Pugsley\Downloads")
    print("    -k  <keyword> Keyword to search for in file path (case insensitive)")
    print("    -d  Enable debug.  Note: may set debug breakpoints.")
    print("    -v  Enable verbose")
    print("    -h  Print(this help message")


version = "01.00.00"
debug = False
verbose = False
match_list = []
keyword = None
startTime = datetime.datetime.now()
endTime = None
total_files = 0
total_images = 0
total_exif = 0
total_lat_long = 0
search_hits = 0
start_dir = None
keyword_hit = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:vdk:h", ["help", "output="])
except getopt.GetoptError as err:
    # print(help information and exit:
    print(str(err))  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-d":
        debug = True
        print("Set debug from command line")
    elif o == "-r":
        recurse = True
        if debug:
            print("Set recursive search from command line")
    elif o == "-v":
        verbose = True
        if debug:
            print("Set verbose from command line")
    elif o == "-p":
        start_dir = a
        if debug:
            print("Set path to: ", start_dir, " from command line")
    elif o == "-k":
        keyword = a
        print("Set search keyword from command line: ", keyword)
    elif o == "-h":
        usage()
        sys.exit(2)
    else:
        print("ERROR: unhandled option: ", o)
        usage()
        sys.exit(2)

if debug:
    pdb.set_trace()

# Make sure a starting path was set

if start_dir == None:
	print("ERROR: no starting directory path set")
	usage()
	sys.exit(2)

# Make sure it really exists

if not os.path.isdir(start_dir):
	print("ERROR: path '%s' was not found" % (start_dir))
	sys.exit(2)

app = Nominatim(user_agent="tutorial")

for subdirectories, directories, files in os.walk(start_dir):
    for file_name in files:
        file_loc = subdirectories + os.path.sep + file_name
        total_files += 1

        if not file_loc.endswith(".jpeg") and \
                not file_loc.endswith(".jpg") and \
                not file_loc.endswith(".JPG"):
            if debug:
                print("Skipping file: ", file_loc)
            continue

        total_images += 1
        keyword_hit = False

        try:
            with open(file_loc, 'rb') as image_file:
                ...
                if verbose:
                    print("\nChecking image file: ", file_loc)

                my_image = Image(image_file)

                has_lat = has_long = False

                if my_image.has_exif:
                    total_exif += 1
                    #pdb.set_trace()
                    if verbose:
                        print("\nFound Exif data for file: ", file_loc)

                    if hasattr(my_image, 'gps_latitude') and hasattr(my_image, 'gps_latitude_ref'):
                        has_lat = True
                        # NOTE: if Lat Ref is 'S' it is negative...	 same for Long Ref = 'W'
                        if debug:
                            print("GPS Data:")
                            print("\tLatitude:	", my_image.gps_latitude, ", Ref: ", my_image.gps_latitude_ref)

                        lat_degrees = my_image.gps_latitude[0]
                        lat_minutes = my_image.gps_latitude[1]
                        lat_seconds = my_image.gps_latitude[2]

                        latitude = lat_degrees + (lat_minutes / 60) + (lat_seconds / 3600)

                        if my_image.gps_latitude_ref == 'S':
                            latitude = latitude * -1

                        if hasattr(my_image, 'gps_longitude') and hasattr(my_image, 'gps_longitude_ref'):
                            has_long = True
                            long_degrees = my_image.gps_longitude[0]
                            long_minutes = my_image.gps_longitude[1]
                            long_seconds = my_image.gps_longitude[2]

                            if debug:
                                print("\tLongitude: ", my_image.gps_longitude, ", Ref: ", my_image.gps_longitude_ref)

                            longitude = long_degrees + (long_minutes / 60) + (long_seconds / 3600)

                            if my_image.gps_longitude_ref == 'W':
                                longitude = longitude * -1

                        if not has_lat and not has_long:
                            if verbose:
                                print("Continuing due to no lat/long/ref data")
                            continue

                        total_lat_long += 1

                        if debug:
                            print("Lat: ", latitude, " ,", "Long: ", longitude)

                        # get the address info
                        address = get_address_by_location(latitude, longitude)

                        if debug:
                            print("Address latitude: ", address['lat'])
                            print("Address longitude: ", address['lon'])

                        if debug:
                            pprint(address)

                        # print all returned data
                        print("\nAddress data for photo: ", file_name)

                        #pdb.set_trace()

                        if 'house_number' in address['address'] and 'road' in address['address']:
                            print("Address: ", address['address']['house_number'], address['address']['road'])
                        else:
                            if 'road' in address['address']:
                                print("Address: ", address['address']['road'])

                        if 'town' in address['address']:
                            print("City:	", address['address']['town'])
                            if keyword != None and address['address']['town'] == keyword:
                                search_hits += 1
                                keyword_hit = True

                        if 'county' in address['address']:
                            print("County:	  ", address['address']['county'])

                        if 'village' in address['address']:
                            print("Village:	   ", address['address']['village'])
                            if keyword != None and address['address']['village'] == keyword:
                                search_hits += 1
                                keyword_hit = True

                        print("State:	", address['address']['state'])
                        print("Country: ", address['address']['country'])

                        if keyword_hit:
                            match_list.append(file_loc)
                    else:
                        if verbose:
                            print("Skipping image file:",file_loc,"due to no EXIF information")

        except Exception as error:
            if debug:
                print("Exception for file: ", file_name)
                print(error)
                #pdb.set_trace()
                #traceback.print_exc()

# pdb.set_trace()
endTime = datetime.datetime.now()

print("--------------------------------------------------\n")
print("Photoloc.py results from: ", start_dir, ", Finished at: ", endTime.strftime("%c"))

print("Total files: ", total_files)
print("Total images: ", total_images)
print("Total Exif: ", total_exif)
print("Total GPS:  ", total_lat_long)

if keyword != None:
    print("Search hits for keyword (", keyword, "):", search_hits)
    for item in match_list:
        print("\t", item)
