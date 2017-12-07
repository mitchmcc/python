#!/usr/bin/python
#------------------------------------------------------------------------------------------------
#
#   pcsocalls.py
#
#   Version        Date     Who     Description
#
#   01.00.11      12/07/17  mjm     Fixed wildcard bug
#
#------------------------------------------------------------------------------------------------

from bs4 import BeautifulSoup
from bs4 import Tag, NavigableString
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import urllib2
import os
import csv
import sys
import pdb
import re
import string
import getopt
import time
import datetime
import logging
import sqlite3
import signal
 
def signal_handler(signal, frame):
        print('Ctrl+C handler: ')
        print 'Entering pdb...'
        pdb.set_trace()
        #sys.exit(0)

def usage():
  logging.info("Usage:")
  logging.info("  -m  [max iterations]")
  logging.info("  -d  Enable debug")
  logging.info("  -s  Email (Smtp) host")
  logging.info("  -p  Email (Smtp) port")
  logging.info("  -v  Enable verbose")
  logging.info("  -i  [interval] (default: ",delay,")")
  logging.info("  -u  Gmail user account")
  logging.info("  -w  Gmail account password")
  logging.info("  -e  Send email")
  logging.info("  -c  Save data as csv file")
  logging.info("  -h  logging.info(this help message")

version = "01.00.11"

dumpTable = 0
delay =   300
maxIter = 0
debug = 0
verbose = 0
printRec = 1
startTime = datetime.datetime.now()
startHour = startTime.hour
sendEmail = 0
saveCsvData = 0
HOST = "localhost"
PORT = 25
emailsSent = 0
totalEmailsSent = 0
useGmail = 1
gmailAccount = ""
gmailPassword = ""
maxEntries = 32
databaseName = 'pcsocalls.db'

# Note: may not be complete

problemNameList = [
                    'ACCIDENT',
                    'AMBULANCE / FIRE DEPT CALL',
                    'ANIMAL CALL',
                    'ARMED PERSON',
                    'ARMED ROBBERY - IN PROGRESS',
                    'ASSIST CITIZEN',
                    'ASSIST MOTORIST',
                    'ASSIST OTHER AGENCY',
                    'BOMB THREAT / DEVICE',
                    'BURGLARY - IN PROGRESS',
                    'BURGLARY - NOT IN PROGRESS',
                    'CIVIL MATTER',
                    'CONTACT',
                    'DECEASED PERSON',
                    'DIRECTED PATROL',
                    'DOMESTIC - IN PROGRESS',
                    'DRUG CALL - NOT IN PROGRESS',
                    'EMOT. DIST. PERSON / BAKER ACT',
                    'HARASSING PHONE CALL',
                    'HIT AND RUN',
                    'INFORMATION / OTHER',
                    'INJUNCTION SERVICE / VIOLATION',
                    'LOST / STOLEN / RECOVERED TAG',
                    'NOISE'
                    'OVERDOSE',
                    'PANHANDLER / SOLICITOR',
                    'RECOVERED VEHICLE',
                    'SPECIAL DETAIL',
                    'SUPPLEMENT',
                    'SUSPICIOUS PERSON',
                    'THEFT - NOT IN PROGRESS',
                    'TRAFFIC / DWLSR',
                    'TRAFFIC VIOLATION',
                    'TRAFFIC STOP',
                    'TRAFFIC CONTROL',
                    'TRANSPORT',
                    'TRAFFIC HAZARD / OBSTRUCTION',
                    'TRESPASS',
                    'VEH ABANDONED / ILLEGALLY PARK'
                    ]

# set up logging the way we want it
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)

logging.info("PCSOCalls version %s starting up",version)

sys.exit

FOOTER = "<p><br>This email is being sent to you because you subscribed to the PCSOCALLS service.<br>" \
         "To modify or stop your subscription, please send email to mitchmcconnell2@outlook.com <br><br>" 

#fromAddr = 'pcsocalls@gmail.com'
fromAddr = 'mitchmcconnell2@outlook.com'

signal.signal(signal.SIGINT, signal_handler)

try:
    opts, args = getopt.getopt(sys.argv[1:], "n:m:i:p:s:du:w:vhecD:", ["help", "output="])
except getopt.GetoptError, err:
    # logging.info(help information and exit:
    logging.info(str(err)) # will logging.infosomething like "option -a not recognized"
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-m":
        maxIter = int(a)
        if debug == 1:
            logging.info("Got maxIter from command line: ",maxIter)
    elif o == "-i":
        delay = a
        if debug == 1:
            logging.info("Got delay interval from command line: ",delay)
    elif o == "-s":
        HOST = a
        if debug == 1:
            logging.info("Got SMTP host from command line: ",HOST)
    elif o == "-u":
        gmailAccount = a
        if debug == 1:
            logging.info("Got Gmail account from command line: ",gmailAccount)
    elif o == "-n":
        databaseName = a
        if debug == 1:
            logging.info("Got database name from command line: ",databaseName)
    elif o == "-w":
        gmailPassword = a
        if debug == 1:
            logging.info("Got Gmail password from command line: ",gmailPassword)
    elif o == "-D":
        delay = a
        if debug == 1:
            logging.info("Got delay from command line: ",delay)
    elif o == "-p":
        PORT = a
        if debug == 1:
            logging.info("Got SMTP port from command line: ",PORT)
    elif o == "-d":
        debug = 1
        if debug == 1:
            logging.info("Set debug from command line")
    elif o == "-e":
        sendEmail = 1
        if debug == 1:
            logging.info("Set sendEmail from command line")
    elif o == "-c":
        saveCsvData = 1
        if debug == 1:
            logging.info("Set saveCsvData from command line")
    elif o == "-v":
        verbose = 1
        if debug == 1:
            logging.info("Set verbose from command line")
    elif o == "-h":
        usage()
        sys.exit(2)
    else:
        logging.info("ERROR: unhandled option: ",o)
        usage()
        sys.exit(2)
        
# set up database stuff

# see if file exists

if not os.path.isfile(databaseName):
	logging.error("ERROR: file " + databaseName + " not found")
	sys.exit(4)

conn = sqlite3.connect(databaseName)
		
finished = 0
run = 1
numDups = 0
numEntries = 0

if (sendEmail == 0) and (saveCsvData == 0):
  logging.info("ERROR: must set either email option (-e) or save CSV data option (-c)")
  sys.exit(3)

# this is the real table with the data  
masterTable = {}

# this table just allows us to manage the number of entries we keep [key] = entryNum
keyTable = {}

csvFileName = "PCSOCALLS_" + startTime.strftime("%Y%m%d_%H") + ".csv"

if debug == 1:
    logging.info("\n\nStarting loop....fileName: ",csvFileName,"\n\n")

lastHour = startHour
    
#pdb.set_trace()

while finished == 0:

    thisTime = datetime.datetime.now()
    thisHour = thisTime.hour

    # every hour, print how long we have been up (we skip the first time)
    
    if ((run % 12) == 0) and (verbose == 1) and (run != 1):
      elapsedTime = thisTime - startTime
      logging.info("Uptime: %s", elapsedTime)
		
    # Check to see if we need to flush our output file and start a new one

    if debug == 1:
      logging.info("Current hour: %s",thisHour)
    
    if thisHour != startHour:
        csvFileName = "PCSOCALLS_" + thisTime.strftime("%Y%m%d_%H") + ".csv"

        if debug == 1:
            logging.info("New fileName: ",csvFileName,"\n\n")
        
    numDisconnected = 0
    numActive = 0
    key = None
    emailsSent = 0

    page = urllib2.urlopen("http://pcsoweb.com/activecallsdetails")
    soup = BeautifulSoup(page, 'html5lib')
    
    #pdb.set_trace()
	
    numFound = 0
    reportNum = None
    occurredAt = None
    problem = None
    address1 = None
    address2 = None
    address3 = None
    locality = None
    unit = None

    tab = soup.find("table")
    
    for htmlrow in tab.find_all('tr'):
        col = htmlrow.find_all('td')
        
		    # col is a list of BS tags

        #print "col: ", col
		
        for data in col:
            #print "data: ", data
            spanList = data.find_all('span')

            for sp in spanList:
                #print "Span: ",sp
                print "Span Id: ",sp['id'], "Text: ",sp.get_text()	
                #pdb.set_trace()

                if "report" in sp['id']:
                  reportNum = sp.get_text().strip()

                if "R_time" in sp['id']:
                  occurredAt = sp.get_text().strip() 

                if "Problem" in sp['id']:
                  problem = sp.get_text().strip()

                if "R_address" in sp['id']:
                  address1 = sp.get_text().strip()

                if "City" in sp['id']:
                  locality = sp.get_text().strip() 

                  #if locality == 'ST PETE BEACH':
                  #  pdb.set_trace()

                if "Units" in sp['id']:
                  unit = sp.get_text().strip()

                if reportNum != None:
                  print "Report: ",reportNum
                  numFound += 1
                  key = reportNum
                if occurredAt != None:
                  print "Occurred: ",occurredAt
                if problem != None:
                  print "Problem: ",problem
                if locality != None:
                  print "Locality: ",locality
                if address1 != None:
                  print "Address: ",address1
                if unit != None:
                  print "Unit: ",unit  

        print "---------------------------------------------------\n"         	

        #pdb.set_trace()

        if reportNum == None:
          print ">>>>>> continuing <<<<<<"
          continue

        print "ReportNum: ",reportNum,", Problem: ",problem, ", Where: ", occurredAt, ", Address1: ",address1

        # this prevents us from sending multiple emails for the same problem (reportNum)

        if not masterTable.has_key(key):
            masterTable[key] = key
            numEntries += 1

            print "setting masterTable key: ",key

            #pdb.set_trace()
            occurredDatetime = datetime.datetime.strptime(occurredAt, '%m/%d/%Y %H:%M %p')
            #occurredAtSql = occurredAt.rstrip(" AM").rstrip(" PM")
            occurredAtSql = occurredDatetime.isoformat()

            keyTable[key] = numEntries

            if saveCsvData == 1:
                with open(csvFileName, 'a') as csvfile:
                    fw = csv.writer(csvfile, delimiter=',')
                    fw.writerow(map(str,[reportNum,problem,occurredAtSql,address1,locality,unit]))
                    
                #if (debug == 1) or (verbose == 1):
                logging.info("Inserted CSV row, index: %s",key)

            #pdb.set_trace()

            if sendEmail == 1:
                #logging.info("Sending email set.... locality = %s, problem = %s",locality,problem)
                  
                problemHit = 0

                # Get user data 

                cur = conn.cursor()
                cur.execute("SELECT firstName, lastName, emailAddress, minPriority, city, wildcard " +
                  " from users where active = '1' and city = ?", (locality,))
                 
                dbrows = cur.fetchall()
                 
                #if locality == "UNINCORPORATED":
                #  pdb.set_trace()

                for row in dbrows:

                  #pdb.set_trace()

                  logging.info("Raw SQL data: %s %s %s %s %s %s" % (row[0], row[1], row[2], row[3], row[4], row[5]))

                  firstName = row[0]
                  lastName = row[1]
                  minPri = row[3]
                  wildcard = row[5]
                  city = row[4]

                  problemHit = 0
                  sendUserEmail = 0
                  PRIORITYBODY = None
                  PROBLEMBODY = None
                  BODYTEXT = ""

                  #if debug == 1:
                  logging.info("ReportNum: %s",reportNum)
                  logging.info("problem: %s,  wildcard: %s",problem, wildcard)
                  
                  if locality != city:
                    continue

                  # if wildcard is null, we send everything... otherwise, parse the csv-separated wildcard list and
                  # see if we find any hits

                  if wildcard != None:
                    #pdb.set_trace()
                    wclist = wildcard.split(',')

                    for wc in wclist:
                      if ((wildcard == None) or 
                        (problem is not None) and 
                            ((wildcard is not None) and 
                              (problem.find(wc) != -1))):
                        problemHit = 1
                        sendUserEmail = 1
                  else:
                    problemHit = 1
                    sendUserEmail = 1

                  if problemHit == 1:

                    #if debug == 1:
                    #logging.info("No wildcard set or found match for problem: %s",problem)
                      
                    PROBLEMBODY="<h4>Pinellas County Sheriff's Office call problem alert hit:</h4></br></br>" \
                    "<table border=\"1\" cellpadding=\"10\">" \
                    "<tr><td>{}</td><td>{}</td></tr>" \
                    "<tr><td>{}</td><td>{}</td></tr>" \
                    "<tr><td>{}</td><td>{}</td></tr>" \
                    "<tr><td>{}</td><td>{}</td></tr>" \
                    "<tr><td>{}</td><td>{}</td></tr>" \
                    "</table>".format("Report Num:",reportNum.lstrip(' '),
                                      "Problem:", problem.lstrip(' '),
                                      "Locality:", locality.lstrip(' '),
                                      "Address:", address1.lstrip(' '),
                                      "Occurred at:", occurredAt.lstrip(' '))

                  if problemHit == 1:
                    BODYTEXT += "\n\n" + PROBLEMBODY

                  if sendUserEmail == 1:

                    HTMLHEADER = """\
                    <html>
                      <head></head>
                      <body>
                    """

                    HTMLFOOTER = """\
                    </body>
                    </html>
                    """

                    WILDCARD_NOTICE = ""

                    #pdb.set_trace()

                    if (wildcard != None):
                      WILDCARD_NOTICE = "Your wildcard settings: " + wildcard

                    #logging.info("\n\n\n>>>>>>>>>>>>>>>>>>>>>>>> setting BODYTEXT"

                    FINALBODY = "{} <h3>Dear {} {}: </h3> {} {} {} {} {} {} {}".format(HTMLHEADER, 
                              firstName,
                              lastName,
                              "\n\n",
                              BODYTEXT,
                              "\n\n",
                              FOOTER,
                              "\n\n",
                              WILDCARD_NOTICE,
                              "\n\n",
                              "Generated by pcsocalls.py version " + version,
                              HTMLFOOTER)

                    #logging.info("+++++++++++++++++++ BODYTEXT: ",BODYTEXT,"\n\n\n"
                    
                    # send email here
                    SUBJECT = "PCSOCALLS notification for locality {}".format(locality)
                    TO = row[2]
                    FROM = fromAddr

                    # Create message container - the correct MIME type is multipart/alternative.
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = SUBJECT
                    msg['From'] = FROM
                    msg['To'] = TO

                    BODY = string.join((
                            "",
                            FINALBODY
                            ), "\r\n")

                    mimeData = MIMEText(BODY,'html')
                    msg.attach(mimeData)
                    
                    if verbose == 1:
                      logging.info("Sending email to %s Subject: %s, problem: %s",row[2], SUBJECT, problem)
                      #pdb.set_trace()

                    if debug == 1:
                      logging.info(">>>> BODY: ",BODY)

                    server = smtplib.SMTP(HOST, PORT)
                    
                    if useGmail == 1:
                      server.starttls()
                      server.login(gmailAccount, gmailPassword)
                      
                    server.sendmail(FROM, [TO], msg.as_string())
                    server.quit()

                    logging.info("Finished sending...")

                    totalEmailsSent += 1
                    emailsSent += 1
                    
        else:
            #if debug == 1:
            # Note: this is not an error, it just means that we have already seen this and hence it
            # is in the map
            #logging.info("found duplicate key: %s",key)
            numDups += 1

    if verbose == 1: 
      print "Num found this pass: ",numFound

      t = time.localtime()
      
      logging.info("Finished pass %s at %02d:%02d:%02d, sleeping %s seconds" % (run, t.tm_hour, t.tm_min, t.tm_sec, delay))
      logging.info("Num entries: %s, Num dups: %s, emails sent: %s (total emails: %s)",numEntries,numDups,emailsSent,totalEmailsSent)

    if dumpTable == 1:
        logging.info(masterTable)

    logging.info("before masterTable size: %s",len(masterTable))
    
    if numEntries > maxEntries:
      firstEntry = numEntries - maxEntries

      keyList = list()

      logging.info("Checking old keys, firstEntry = %s",firstEntry)
      
      # now iterate over both lists, and save a list of all keys that have aged out
      for key in keyTable:
        if keyTable[key] <= firstEntry:
          logging.info("Storing key %s",key)
          keyList.append(key)

      logging.info("Deleting keys now...")
      
      for item in keyList:
          logging.info("deleting oldest key[s] item: %s",item)
          del keyTable[item]
          del masterTable[item]

    logging.info("after masterTable size: %s",len(masterTable))
      
    run = run + 1
    
    if maxIter <> 0:
      maxIter = maxIter + 1

    time.sleep(float(delay))

    if (maxIter <> 0) and (run >= maxIter):
      finished = 1

      if verbose == 1:
        logging.info("Stopping due to max iterations reached")
