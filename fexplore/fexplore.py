#!/usr/bin/python
#------------------------------------------------------------------------------------------------
#
#   fexplore.py
#
#   Version        Date     Who     Description
#
#   01.00.00     09/28/20  	mjm    	Initial version
# 
#------------------------------------------------------------------------------------------------
import os
import sys
import glob
import getopt
import pdb

#path = r'/users/mitch/Documents/images/birds/work area/**/*.jpg'
#path = r'/users/mitch/**/*.exe'
path = None

total_skipped = 0
total_files = 0
total_matches = 0
match_list = []
file_ext = None
verbose = False
recurse = None
keyword = None
debug = False

def usage():
  print("Usage:")
  print("  -p  <path> Starting path to search")
  print("  -e  <extension> File extension to search for")
  print("  -r  Enable recursive search")
  print("  -d  Enable debug")
  print("  -v  Enable verbose")
  print("  -k  <keyword> Keyword to search for in file path (case insensitive)")
  print("  -h  Print this help message")
  print("  Examples: ")
  print("     Search for all .exe files recursively starting at c:/users/jsmith")
  print("        python fexplore.py -p \"c:/users/jsmith\" -e \"exe\" -r")
  print("     Search for all .jpg files recursively starting at c:/users/jsmith with 'pool' in the path")
  print("        python fexplore.py -p \"c:\" -e \"jpg\" -r -k pool")


version = "01.00.00"

try:
    opts, args = getopt.getopt(sys.argv[1:], "k:e:p:rdvh", ["help", "output="])
except getopt.GetoptError as err:
    # print(help information and exit:
    print(str(err)) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-d":
        debug = True
        if debug == True:
            print("Set debug from command line")
    elif o == "-r":
        recurse = True
        if debug == True:
            print("Set recursive search from command line")
    elif o == "-v":
        verbose = True
        if debug == True:
            print("Set verbose from command line")
    elif o == "-k":
        keyword = a
        if debug == True:
            print("Set keyword to: ",keyword, " from command line")
    elif o == "-p":
        path = a
        if debug == True:
            print("Set path to: ",path, " from command line")
    elif o == "-e":
        file_ext = a
        if debug == True:
            print("Set file extension to: ",file_ext, " from command line")
    elif o == "-h":
        usage()
        sys.exit(2)
    else:
        print("ERROR: unhandled option: ",o)
        usage()
        sys.exit(2)
        
if verbose:
	print("fexplore version ",version," starting up");

if file_ext == None:
	print("ERROR: no file extension set, use -e option")
	sys.exit(2)

if path == None:
	print("ERROR: no path set, use -p option")
	sys.exit(2)
else:
	if recurse:
		# make sure no ending slash was entered
		path = path.rstrip('/')
		path += "/**/*." + file_ext
		
		if debug:
			print("New value for recursive path: ",path)
			
pdb.set_trace()

for exe in glob.glob(path,recursive=True):
	total_files += 1
	if os.stat(exe).st_size == 0:
		if debug:
			print(">>>> Skipping 0 byte file: ", exe)
		total_skipped += 1
		continue
		
	if keyword != None:
		if keyword.lower() in exe.lower():
			total_matches += 1
			match_list.append(exe)
			if verbose:
				print("Found keyword match for: ", exe)
	if debug or verbose:
		print("File: ",exe)
	

print("Total files for extension",file_ext,":",total_files)
print("Total skipped: ", total_skipped)

if keyword != None:
	print("Total matches found for keyword: ",keyword, ": ",total_matches)
	for item in match_list:
		print("\t",item)


