#!/usr/bin/python
from bs4 import BeautifulSoup
from bs4 import Tag, NavigableString
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib2
import sys
import pdb
import re
import string
import getopt
import time
import datetime
import logging
import mysql.connector
from Call import ActiveCall 

version = "01.00.09"

dumpTable = 0
delay = 300
doSendEmail = False
maxIter = 0
debug = False
verbose = False
printRec = 0
startTime = datetime.datetime.now()
startHour = startTime.hour
HOST = "localhost"
PORT = 25
totalEmailsSent = 0
totalEmailsFailed = 0
totalDbMatches = 0
maxEntry = 0

gmailAccount = ""
gmailPassword = ""
maxEntries = 32
numEntries = 0

FOOTER = "<p><br>This email is being sent to you because you subscribed to the PCSOCALLS service.<br>" \
         "To modify or stop your subscription, please send email to mitch@mitchellmcconnell.net"
# fromAddr = 'pcsocalls@gmail.com'
fromAddr = 'pcsocalls@mitchellmcconnell.net'

# mySql connector
cnx = None

# this is the real table with the data  
masterTable = {}

#--------------------------------------------------------------------------
#
#                                d o T e s t s
#
#--------------------------------------------------------------------------
def doTests():

    testCalls = [
        ActiveCall("SO15-099077", "3/9/2015 06:26 AM", "HOMICIDE", "SEMINOLE BLVD", "SEMINOLE", "SMC2"),
        ActiveCall("SO15-099078", "3/9/2015 06:26 AM", "ASSAULT", "322 CASCADE LN", "COUNTY", "SMC3"),
        ActiveCall("SO15-099079", "3/9/2015 06:26 AM", "SUSPICIOUS PERSON", "3301 MCMULLEN BOOTH", "SAFETY HARBOR", "SMC2"),
        ActiveCall("SO15-099080", "3/9/2015 06:26 AM", "DOMESTIC VIOLENCE", "GULF BLVD", "ST PETE BEACH", "SMC4"),
        ActiveCall("SO15-099081", "3/9/2015 06:26 AM", "BURGLARY", "2499 PINELLAS BAYWAY", "TIERRA VERDE", "SMC9"),
        ActiveCall("SO15-099082", "3/9/2015 06:26 AM", "ASSIST OTHER AGENCY", "4344 39TH AVE", "CLEARWATER", "SMC4")
    ]

    for call in testCalls:
        processCall(call)

#--------------------------------------------------------------------------
#
#                             s e n d E m a i l
#
#--------------------------------------------------------------------------
def sendEmail(thisCall, firstName, lastName, emailAddress):
    global verbose
    global totalEmailsSent
    global totalEmailsFailed
    global doSendEmail

    # for debugging, we are going to always pretend we sent it

    totalEmailsSent += 1

    if not doSendEmail:
        return

    BODYTEXT = ""

    PROBLEMBODY = "<h4>Pinellas County Sheriff's Office call problem alert hit:</h4></br></br>" \
        "<table border=\"1\" cellpadding=\"10\">" \
        "<tr><td>{}</td><td>{}</td></tr>" \
        "<tr><td>{}</td><td>{}</td></tr>" \
        "<tr><td>{}</td><td>{}</td></tr>" \
        "<tr><td>{}</td><td>{}</td></tr>" \
        "</table>".format("Problem:", thisCall.problem.lstrip(' '),
                                 "Locality:", thisCall.locality.lstrip(' '),
                                 "Address1:", thisCall.address1.lstrip(' '),
                                 "Occurred at:", thisCall.occurredAt.lstrip(' '))

    BODYTEXT += "\n\n" + PROBLEMBODY

    HTMLHEADER = """\
            <html>
              <head></head>
              <body>
    """

    HTMLFOOTER = """\
            </body>
            </html>
    """

    #print "\n\n\n>>>>>>>>>>>>>>>>>>>>>>>> setting BODYTEXT"
      
    FINALBODY = "{} <h3>Dear {} {}: </h3> {} {} {} {} {}".format(HTMLHEADER, firstName, lastName, "\n\n", BODYTEXT, "\n\n", FOOTER, HTMLFOOTER)

    # send email here
    SUBJECT = "PCSOCALLS notification for locality {}".format(thisCall.locality)
    TO = emailAddress
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
  
    #print "+++++++++++++++++++ FINALBODY: ", FINALBODY, "\n\n\n"
    
    mimeData = MIMEText(BODY, 'html')
    msg.attach(mimeData)
    
    if verbose:
        print "Sending email to ", (firstName + " " + lastName), ", SUBJECT: ", SUBJECT
        print "Problem hit: ",thisCall.problem," for locality: ",thisCall.locality
        
    if debug:
        print "HOST: ",HOST,", PORT: ",PORT

    try:
        server = smtplib.SMTP(HOST, PORT)
        
        server.ehlo()
        server.starttls()
        server.login(gmailAccount, gmailPassword)
      
        server.sendmail(FROM, [TO], msg.as_string())
        server.quit()

    except Exception as e:
        totalEmailsFailed += 1
        print "Caught exception: ", e



#--------------------------------------------------------------------------
#
#                            p r o c e s s C a l l
#
#--------------------------------------------------------------------------
def processCall(thisCall):
    global masterTable
    global cnx
    global verbose
    global debug
    global totalDbMatches
    global numEntries

    if verbose:
        print "\n(processCall) enter, call: ", thisCall

    #pdb.set_trace()

    occurredAtSql = datetime.datetime.now().strftime("%Y-%m-%d") + " " + \
            thisCall.occurredAt.rstrip(" AM").rstrip(" PM")

    key = thisCall.reportNum
    
    if debug:
        print "key = ", key
      
    if not masterTable.has_key(key):
        numEntries += 1

        thisCall.entry = numEntries

        print ">>>> entering call ",thisCall.reportNum,"into map"

        masterTable[key] = thisCall
    else:
        # if we've already seen this one, just don't do anything and return
        return thisCall.entry
      
    cur = cnx.cursor()

    sql = "SELECT firstName, lastName, emailAddress, city, wildcard " + \
        "FROM users " + \
        "WHERE city = '" + thisCall.locality + "'"

    if debug:
        print "sql: ",sql

    cur.execute(sql)
        
    dbRows = cur.fetchall()

    if len(dbRows) == 0:
        print "No database matches found"
        return

    #pdb.set_trace()
    
    for dbRow in dbRows:
        if debug:
            print "Raw SQL data: %s %s %s %s %s %s" % (dbRow[0], dbRow[1], dbRow[2], dbRow[3], dbRow[4])

        firstName = dbRow[0]
        lastName = dbRow[1]
        email = dbRow[2]
        locality = dbRow[3]
        wildcard = dbRow[4]

        if (wildcard in thisCall.problem) and (locality == thisCall.locality):
            totalDbMatches += 1

            if verbose:
                print "Found match for wildcard: ",wildcard,", locality: ",locality

            sendEmail(thisCall, firstName, lastName, email)

    return thisCall.entry

#--------------------------------------------------------------------------
#
#                                  u s a g e
#
#--------------------------------------------------------------------------
def usage():
    print "Usage:"
    print "  -m  [max iterations]"
    print "  -d  Enable debug"
    print "  -s  Email (Smtp host"
    print "  -p  Email (Smtp port"
    print "  -v  Enable verbose"
    print "  -i  [interval] (default: ", delay, ""
    print "  -u  Gmail user account"
    print "  -w  Gmail account password"
    print "  -e  Send email"
    print "  -h  print this help message"


#--------------------------------------------------------------------------
#
#                                    m a i n
#
#--------------------------------------------------------------------------

print "PCSOCalls version ",version,"starting up"

# set up database stuff

cnx = mysql.connector.connect(user='root', password='spam5312', host='127.0.0.1', database='pcsocalls')

try:
    opts, args = getopt.getopt(sys.argv[1:], "m:i:p:s:du:w:vh", ["help", "output="])
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err)  # will logging.infosomething like "option -a not recognized"
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-m":
        maxIter = a
        if debug:
            print "Got maxIter from command line: ", maxIter
    elif o == "-i":
        delay = a
        if debug:
            print "Got delay interval from command line: ", delay
    elif o == "-s":
        HOST = a
        if debug:
            print "Got SMTP host from command line: ", HOST
    elif o == "-u":
        gmailAccount = a
        if debug:
            print "Got Gmail account from command line: ", gmailAccount
    elif o == "-w":
        gmailPassword = a
        if debug:
            print "Got Gmail password from command line: ", gmailPassword
    elif o == "-p":
        PORT = a
        if debug:
            print "Got SMTP port from command line: ", PORT
    elif o == "-d":
        debug = True
        if debug:
            print "Set debug from command line"
    elif o == "-v":
        verbose = True
        if debug:
            print "Set verbose from command line"
    elif o == "-h":
        usage()
        sys.exit(2)
    else:
        print "ERROR: unhandled option: ", o
        usage()
        sys.exit(2)
        
finished = 0
run = 1
numDups = 0

if debug:
    print "\n\nStarting loop....fileName: ", csvFileName, "\n\n"

reportNum = ""
occurredAt = ""
priority = ""
problem = ""
address1 = ""
address2 = ""
address3 = ""
locality = ""
unit = ""

test = False

if (test):
    doTests()
    sys.exit(0)

lastHour = startHour
    
while finished == 0:
    thisTime = datetime.datetime.now()
    thisHour = thisTime.hour

    # every hour, print how long we have been up (we skip the first time)
    
    if ((run % 12) == 0) and (verbose) and (run != 1):
        elapsedTime = thisTime - startTime
        print "Uptime: %s", elapsedTime
		
    # Check to see if we need to flush our output file and start a new one

    if debug:
        print "Current hour: ", thisHour
    
    if thisHour != startHour:
        csvFileName = "PCSOCALLS_" + thisTime.strftime("%Y%m%d_%H") + ".csv"

    if debug:
        print "New fileName: ", csvFileName, "\n\n"
        
    numDisconnected = 0
    numActive = 0
    
    page = urllib2.urlopen("http://www.pcsoweb.com/activecallsdetails")
    soup = BeautifulSoup(page, 'html5lib')
    
    tab = soup.find("table", id="ctl00_mainContent_ctl00_GridView1")

    # pdb.set_trace()

    allRows = tab.findAll('tr')
    print "allRows len: ", len(allRows)
    
    for row in allRows:

        reportNum = ""
        occurredAt = ""
        priority = ""
        problem = ""
        address1 = ""
        locality = ""
        unit = ""

        if debug: print "\n-----------------------------------------------------\n>>>> found row: ", row
        
        # col = row.findAll("td", {"valign" : "top"})
        allDataRows = row.findAll("td")
        if debug: print "len(allDataRows): ", len(allDataRows)
        
        #pdb.set_trace()

        mylist = []
        
        thisCall = ActiveCall()
        
        for data in allDataRows:
            if debug: print "\n\t>>>> found <td> data: ", data, ", contents len: ", len(data.contents), "<<<<"
              
            for item in data.contents:
                if debug: print "raw contents: ", item.encode('latin-1')

                #pdb.set_trace()
                
                # this is just to try and extract the call severity 
                # of of the wrapping <font> tag
                
                for entity in item:
                    #pdb.set_trace()
                    if debug:
                        print "\n\t\t>>>> entity: ", entity, ", len: ", len(entity)
                        print "\t\t>>>> contents: ", entity.contents[1].contents[0]
                        print "\t\t>>>> id: ", entity.contents[1].get('id')

                    if ('report' in entity.contents[1].get('id').encode('latin-1')):
                        reportNum = entity.contents[1].contents[0]
                        if debug: print "#### found report: ", reportNum
                        thisCall.reportNum = reportNum
                      
                    if ('Problem' in entity.contents[1].get('id').encode('latin-1')):
                        problem = entity.contents[1].contents[0]
                        if debug: print "#### found problem: ", problem
                        thisCall.problem = problem
                      

                    if (len(entity) == 7):
                        spans = entity.findAll('span')
                        if debug:
                            print "\t\t>>>> spans size: ", len(spans)
                            print "\t\t>>>> spans[0]: ", spans[0]
                            print "\t\t>>>> spans[1]: ", spans[1]
                      
                        #pdb.set_trace()

                        try:
                            address1 = spans[0].contents[0]
                            thisCall.address1 = address1
                        except Exception as e:
                            print "ERROR: caught address1 exception: ",e
                            pdb.set_trace()
                            print "spans: ",spans
                            print "item: ", item
                            print "entity: ",entity
                            sys.exit(4)

                        # sometimes, the locality is not present
                        try:
                            locality = spans[1].contents[0]
                            thisCall.locality = locality
                        except Exception as e:
                            print "WARNING: caught locality exception, locality not set, key: ",thisCall.reportNum
                            print "spans: ",spans
                            print "item: ", item
                            print "entity: ",entity
                            thisCall.locality = "Not found"
                      
                        if debug:
                            print "#### found address1: ", address1
                            print "#### found locality: ", locality

                    if ('R_time' in entity.contents[1].get('id').encode('latin-1')):
                        occurredAt = entity.contents[1].contents[0]
                        if debug: print "#### found occurredAt: ", occurredAt
                        thisCall.occurredAt = occurredAt
                      
                    if ('Units' in entity.contents[1].get('id').encode('latin-1')):
                        unit = entity.contents[1].contents[0]
                        if debug: print "#### found unit: ", unit
                        thisCall.unit = unit

        # If we had a data row, once we finish with all of the data from the row, process this call

        #pdb.set_trace()

        if len(allDataRows) > 0:
            entry = processCall(thisCall)

            if entry > maxEntry:
                maxEntry = entry

 

    t = time.localtime()
      
    print "Finished pass %s at %02d:%02d:%02d, sleeping %s seconds" % (run, t.tm_hour, t.tm_min, t.tm_sec, delay)
    print "Num entries: %s, Num dups: %s, total emails sent: %s, failed: %s" % \
           (len(masterTable), numDups, totalEmailsSent, totalEmailsFailed)

#    if dumpTable == 1:
#        print masterTable

    print "masterTable size: %s, maxEntry: %s" % (len(masterTable), maxEntry)
    
    print "\nMaster Table dump: \n"
    print "%-15s   %s\n" % ("Key", "Call Data")

    for key in sorted(masterTable):
        print "%-15s : %s" % (key, masterTable[key])

    print "\n"

    if len(masterTable) > maxEntries:
        newOldestIndex = maxEntry - maxEntries
        print "new Oldest index: ",newOldestIndex

        keyList = list()

        # now iterate over both lists, and save a list of all keys that have aged out
        for key in masterTable:
            call = masterTable[key]
            if call.entry <= newOldestIndex:
                print "adding old entry to delete list: ", call.reportNum,", index: ",call.entry
                keyList.append(call.reportNum)

        print "Deleting keys now..."
      
        for item in keyList:
            print "deleting oldest key[s] item: %s" % (item)
            del masterTable[item]

        print "after masterTable size: %s" % (len(masterTable))

      
    run = run + 1

    if verbose:
        print "Sleeping %s secs" % (delay)

    time.sleep(float(delay))

    if (maxIter <> 0) and (run >= maxIter):
      finished = 1

      if verbose:
        print "Stopping due to max iterations reached"
