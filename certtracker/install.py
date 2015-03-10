#---------------------------------------------------------------------------------------------------------
#
#   Module: install.py
#
#   Author: Mitchell McConnell
#
#---------------------------------------------------------------------------------------------------------
#
#  Date     Who         Description
#
# 07/13/12  mjm         Original version
#
#---------------------------------------------------------------------------------------------------------

import wx
import sys
import os
import getopt
import string
import datetime 
import logging
import sqlite3
import certDbUtils as dbUtils
import certErrors as cterr

logger = logging.getLogger('certTracker')
logger.setLevel(logging.WARN)

fh = logging.FileHandler('install.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
ch.setFormatter(formatter)
logger.addHandler(ch)


try:
    opts, args = getopt.getopt(sys.argv[1:], "u:p:", ["help", "output="])
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
    
user = None
password = None

for o, a in opts:
    if o == "-u":
        user = a
    elif o == "-p":
        password = a
    else:
	assert False, "unhandled option"

print "you entered user: %s, password: %s" % (user, password)

dbPath = os.environ['CERTTRACKER_HOME']
dbName = os.environ['CERTTRACKER_DB']
dbFile = dbPath + '/' + dbName

if not os.path.isfile(dbFile):
    print "Error opening database file: \n%s\n\nPlease check file name and path" % dbFile
    sys.exit(cterr.CT_DATABASE_NOT_FOUND)

try:
    con = sqlite3.connect(dbFile)
    con.row_factory = sqlite3.Row
except sqlite3.Error, e:
    print "Error opening database: %s" % e
    sys.exit(cterr.CT_DATABASE_CONNECT_ERROR)

dbUtils.addEmailAccount(con, user, password)

# now try and read them back

emailAccount = dbUtils.getEmailAccount(con)
gmailUser = emailAccount[0]
gmailPass = emailAccount[1]

print "got emailAccount info, user: %s, pass: %s" % (emailAccount[0], emailAccount[1])
