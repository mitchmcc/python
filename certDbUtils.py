#--------------------------------------------------------------------------------------------------------
#
#   Module: certDbUtils.py
#
#   Author: Mitchell McConnell
#
#---------------------------------------------------------------------------------------------------------
#
#  Date     Who         Description
#
# 06/21/12  mjm         Original version
# 06/25/12  mjm         Added certifications functions
# 07/12/12  mjm         Added logging module and started logging
# 07/13/12  mjm         Added routines to update certconfig tble
#
#---------------------------------------------------------------------------------------------------------

import wx
import sys
import os
from datetime import datetime
from datetime import timedelta
import sqlite3
import group as g
import employee as e
import certification as c
import employeeCertification as ec
import logging

g_groups = {}
g_employees = {}
g_certifications = {}
g_certtracking = {}

debugLoad = 0
debug = 0

logger = logging.getLogger('certTracker')

##logger.debug("dbUtils got logger: %s" % logger
##logger.debug("dbUtils logging level: %s (%s)" % (logging.getLevelName(logger.getEffectiveLevel()), logger.getEffectiveLevel())
##
##logger.debug("dbUtils logger debug test")
##logger.warn("dbUtils logger warning test")
##logger.error("dbUtils logger error test")
##logger.critical("dbUtils logger critical test")


#---------------------------------------------------------------------------------------------------------
#
#                         i n i t L o g g i n g
#
#---------------------------------------------------------------------------------------------------------
##def initLogging():
##    
##    logger.debug("dbUtils got logger: %s" % logger
##    logger.debug("dbUtils logging level: %s (%s)" % (logging.getLevelName(logger.getEffectiveLevel()), logger.getEffectiveLevel())
##
##    logger.debug("dbUtils logger debug test")
##    logger.warn("dbUtils logger warning test")
##    logger.error("dbUtils logger error test")
##    logger.critical("dbUtils logger critical test")
    
#---------------------------------------------------------------------------------------------------------
#
#                         l o a d  G r o u p s
#
#---------------------------------------------------------------------------------------------------------
def loadGroups(con):

    logger.debug("loadGroups: enter")
    
    g_groups.clear()
    
    with con:    
        cur = con.cursor()    

        cur.execute("select * from groups g order by name;")

        rows = cur.fetchall()

        for row in rows:
            newGroup = g.Group(row["id"], row["name"], row["active"])
            g_groups[int(newGroup.getId())] = newGroup

            logger.debug(">>> created group: %s" % newGroup.getName())
                
        logger.debug("Created %d groups " % len(g_groups))

#---------------------------------------------------------------------------------------------------------
#
#                                 a d d G r o u p 
#
#---------------------------------------------------------------------------------------------------------
def addGroup(con, newGroup):

    logger.debug("Adding new group %s" % newGroup.getName())
    
    c = con.cursor()

    try:
        c.execute('insert into groups (name, active) values (?, ?)',
                  (newGroup.getName(), newGroup.isActive()))
    except sqlite3.Error, msg:
        logger.error(msg)

    # or c.lastrowid
    newGroup.setId(c.lastrowid)

    logger.debug("addGroup: new id: %s" % newGroup.getId())

    con.commit()

#---------------------------------------------------------------------------------------------------------
#
#                              u p d a t e G r o u p 
#
#---------------------------------------------------------------------------------------------------------
def updateGroup(con, newGroup):

    logger.debug("Updating group %s, status %s" % (newGroup.getName(), newGroup.isActive()))
    
    c = con.cursor()

    c.execute('update groups set name=?, active=? where id =?',
              (newGroup.getName(), newGroup.isActive(), newGroup.getId()))

    con.commit()


    
#---------------------------------------------------------------------------------------------------------
#
#                       g e t G r o u p L i s t
#
#---------------------------------------------------------------------------------------------------------
def getGroupList():

    # create an empty list
    tmp = []

    # iterate over groups and return a list of the Group objects
    
    for value in g_groups.itervalues():
        tmp.append(value)

    return tmp

#---------------------------------------------------------------------------------------------------------
#
#                       g e t G r o u p M a p
#
#---------------------------------------------------------------------------------------------------------
def getGroupMap():

    return g_groups

#---------------------------------------------------------------------------------------------------------
#
#                         f i n d G r o u p B y I d
#
#---------------------------------------------------------------------------------------------------------
def findGroupById(id):

    # first, look for it in the global map
    
    if g_groups.has_key(id):
        return g_groups[id]

    # try to find it in the database
    
    return None

#---------------------------------------------------------------------------------------------------------
#
#                       f i n d G r o u p B y N a m e
#
#---------------------------------------------------------------------------------------------------------
def findGroupByName(con, name):
    locus = "findGroupByName"

    logger.debug("%s: looking for group: %s" % (locus, name))
    
    with con:    
    
        cur = con.cursor()    

        cur.execute("select * from groups g ;")

        rows = cur.fetchall()

        for row in rows:
            logger.debug("Checking group: %s" % row["name"])
            
            if row["name"] == name:
                group = g.Group(row["id"], row["name"], row["active"])
                return group

        logger.debug("%s: returning None" % name)
        
        return None




#---------------------------------------------------------------------------------------------------------
#
#                         l o a d  E m p l o y e e s
#
#---------------------------------------------------------------------------------------------------------
def loadEmployees(con):

    g_employees.clear()
    
    with con:
    
        cur = con.cursor()    

        cur.execute("select * from employees order by lastName, firstName;")

        rows = cur.fetchall()

        for row in rows:
            emp = e.Employee(int(row["id"]), row["firstName"], row["lastName"],
                       row["active"], row["startdate"], row["groupid"])

            g_employees[int(emp.getId())] = emp

            logger.debug(">>> created employee id %s in map" % emp.getId())

#---------------------------------------------------------------------------------------------------------
#
#                       g e t E m p l o y e e M a p
#
#---------------------------------------------------------------------------------------------------------
def getEmployeeMap():

    return g_employees

#---------------------------------------------------------------------------------------------------------
#
#                       g e t E m p l o y e e L i s t
#
#---------------------------------------------------------------------------------------------------------
def getEmployeeList():

    # create an empty list
    tmp = []

    # iterate over groups and return a list of the Group objects
    
    for value in g_employees.itervalues():
        tmp.append(value)

    return tmp

#---------------------------------------------------------------------------------------------------------
#
#                    f i n d E m p l o y e e B y I d
#
#---------------------------------------------------------------------------------------------------------
def findEmployeeById(id):

    # first, look for it in the global map

    logger.debug("findEmployeeById: looking for id: %s" % id)
    
    if g_employees.has_key(int(id)):
        return g_employees[int(id)]

    # try to find it in the database

    logger.debug("findEmployeeById: id: %s not found" % id)

    return None

#---------------------------------------------------------------------------------------------------------
#
#                                 a d d E m p l o y e e
#
#---------------------------------------------------------------------------------------------------------
def addEmployee(con, newEmpl):

    logger.debug("Adding new employee id %s, name %s status %s groupId %s" % (newEmpl.getId(), newEmpl.getFullName(),
                                                                       newEmpl.isActive(), newEmpl.getGroupId()))
    logger.debug(">>> start date: %s" % newEmpl.getStartDate())
    
    c = con.cursor()

    try:
        c.execute('insert into employees (firstName, lastName, active, startDate, groupId) values (?, ?, ?, ?, ?)',
                  (newEmpl.getFirstName(), newEmpl.getLastName(), newEmpl.isActive(), newEmpl.getStartDate(),
                   newEmpl.getGroupId()))
    except sqlite3.Error, msg:
        logger.error(msg)

    # or c.lastrowid
    newEmpl.setId(c.lastrowid)

    logger.debug("addEmployee: new id: %s" % newEmpl.getId())

    con.commit()

    # iterate over all groupcerts that belong to the group, and add a row to the certificationtracking
    # table

    # a. if initial is set, calc renew date from employee start date + initial days
    # b. if initial is not set, calc renew from employee start date + renewal days 

    with con:    
        cur = con.cursor()    

        cur.execute("select * from groupcerts where groupId = ?;", (newEmpl.getGroupId(),))

        rows = cur.fetchall()

        for row in rows:
            certId = row["certificationId"]

            certObj = findCertificationById(certId)
        
            logger.debug("certId: %s, initial: %s, renewal: %s" % (certObj.getId(), certObj.getInitial(), certObj.getRenewal()))

            initial = certObj.getInitial()
            renewal = certObj.getRenewal()
            
            startdateobj = datetime.date(datetime.strptime(newEmpl.getStartDate(),'%Y%m%d'))

            logger.debug("employee start date: %s, initial: %s, renewal: %s" % (startdateobj,initial,renewal))

            # calculate the renew date

            #certdateobj = datetime.date(datetime.strptime(cert_date, '%Y%m%d'))
            #logger.debug("cert dateobj: %s" % certdateobj

            if initial != None:
                renew_date = startdateobj + timedelta(days=initial)

                logger.debug("calculated renew_date: %s" % renew_date)

            # create the EmployeeCertification object

            tmpId = 0
        
            empCert = ec.EmployeeCertification(tmpId, newEmpl.getId(), certId, None, renew_date)

            addCertTracking(con, empCert)
        
    
    # now add the new employee to the global map

    g_employees[int(newEmpl.getId())] = newEmpl


#---------------------------------------------------------------------------------------------------------
#
#                              u p d a t e E m p l o y e e
#
#---------------------------------------------------------------------------------------------------------
def updateEmployee(con, newEmpl):

    logger.debug("Updating employee %s %s, status %s startDate %s groupId %s, id %s" % \
              (newEmpl.getFirstName(), newEmpl.getLastName(), newEmpl.isActive(),
               newEmpl.getStartDate(), newEmpl.getGroupId(), newEmpl.getId()))
    
    c = con.cursor()

    c.execute('update employees set firstName=?, lastName=?, active=?, startDate=?, groupId=? where id =?',
              (newEmpl.getFirstName(), newEmpl.getLastName(), newEmpl.isActive(),
               newEmpl.getStartDate(), newEmpl.getGroupId(), newEmpl.getId()))

    con.commit()

#---------------------------------------------------------------------------------------------------------
#
#                                 d u m p E m p l o y e e M a p
#
#---------------------------------------------------------------------------------------------------------
def dumpEmployeeMap():
    logger.debug("g_employees map:\n")
    
    for (key, value) in g_employees.items():
        logger.debug("Key: %s   Value: %s" % (key, value))
        


#---------------------------------------------------------------------------------------------------------
#
#                              l o a d  C e r t i f i c a t i o n s
#
#---------------------------------------------------------------------------------------------------------
def loadCertifications(con):
    g_certifications.clear()
    
    with con:    
        cur = con.cursor()    

        cur.execute("select * from certifications order by certification;")

        rows = cur.fetchall()

        for row in rows:
            newCert = c.Certification(row["id"], row["certification"], row["initial"], row["renewal"], row["active"], row["notes"])

            logger.debug("id: %s, cert: %s, initial: %s, renewal: %s, active: %s, notes: %s" % \
                      (row["id"], row["certification"], row["initial"], row["renewal"], row["active"], row["notes"]))
            g_certifications[int(newCert.getId())] = newCert

            logger.debug(">>> created certification id: %s" % newCert.getId())

    logger.debug("Created %d certifications " % len(g_certifications))
        
    return g_certifications


#---------------------------------------------------------------------------------------------------------
#
#                       g e t C e r t i f i c a t i o n L i s t
#
#---------------------------------------------------------------------------------------------------------
def getCertificationList():

    # create an empty list
    tmp = []

    # iterate over certifications and return a list of the Certification objects
    
    for value in g_certifications.itervalues():
        tmp.append(value)

    return tmp

#---------------------------------------------------------------------------------------------------------
#
#                       g e t C e r t i f i c a t i o n M a p 
#
#---------------------------------------------------------------------------------------------------------
def getCertificationMap():

    return g_certifications

#---------------------------------------------------------------------------------------------------------
#
#                       g e t C e r t i f i c a t i o n M a p B y G r o u p
#
#---------------------------------------------------------------------------------------------------------
def getCertificationMapByGroup(con, groupId):

    # create an empty map
    tmp = {}

    c = con.cursor()

    with con:    
        cur = con.cursor()    

        cur.execute("select id as certid, certification from certifications c " +
                    "join groupcerts g where g.groupid =? and g.certificationid = c.id order by certification;", str(groupId))

        rows = cur.fetchall()

        for row in rows:

            logger.debug("getCertMapByGroup: found row, certId: %s, cert: %s" % (row["certid"], row["certification"]))
            
            cert = findCertificationById(row["certid"])
            if cert != None:
                tmp[cert.getId()] = cert

    return tmp

#---------------------------------------------------------------------------------------------------------
#
#                       g e t L i s t F r o m M a p
#
#---------------------------------------------------------------------------------------------------------
def getListFromMap(map):

    # create an empty list
    tmp = []

    # iterate over map and return a list of the objects
    
    for value in map.itervalues():
        tmp.append(value)

    return tmp

#---------------------------------------------------------------------------------------------------------
#
#                                 a d d C e r t i f i c a t i on
#
#---------------------------------------------------------------------------------------------------------
def addCertification(con, newCert):

    logger.debug("Adding new certification %s" % newCert.getCertification())
    
    c = con.cursor()

    try:
        c.execute('insert into certifications (certification, initial, renewal, active, notes) values (?, ?, ?, ?, ?)',
                  (newCert.getCertification(), newCert.getInitial(), newCert.getRenewal(), newCert.isActive(), newCert.getNotes()))
    except sqlite3.Error, msg:
        logger.error("%s: %s" ("ERROR: sqlite exception: ", msg))

    # or c.lastrowid
    newCert.setId(c.lastrowid)

    logger.debug("addCertification: new id: %s" % newCert.getId())

    # add new cert to the global map
    
    g_certifications[int(newCert.getId())] = newCert

    con.commit()

#---------------------------------------------------------------------------------------------------------
#
#                              u p d a t e C e r t i f i c a t i o n
#
#---------------------------------------------------------------------------------------------------------
def updateCertification(con, newCert):

    logger.debug("Updating Certification %s, initial: %s, renewal: %s, status %s, notes: %s" % \
          (newCert.getCertification(), newCert.getInitial(), newCert.getRenewal(), newCert.isActive(), newCert.getNotes()))
    
    c = con.cursor()

    try:
        c.execute('update Certifications set certification=?, initial=?, renewal=?, active=?, notes=? where id =?',
              (newCert.getCertification(),  newCert.getInitial(), newCert.getRenewal(), \
               newCert.isActive(), newCert.getNotes(), newCert.getId()))
    except sqlite3.Error, msg:
        logger.error("%s: %s" % ("ERROR: sqlite exception: ", msg))

    con.commit()



#---------------------------------------------------------------------------------------------------------
#
#                                 d u m p C e r t i f i c a t i o n M a p
#
#---------------------------------------------------------------------------------------------------------
def dumpCertificationMap():
    logger.debug("g_employees map:\n")
    
    for (key, value) in g_certifications.items():
        logger.debug("Key: %s   Value: %s" % (key, value))


#---------------------------------------------------------------------------------------------------------
#
#                         f i n d C e r t i f i c a t i o n B y I d
#
#---------------------------------------------------------------------------------------------------------
def findCertificationById(id):

    # first, look for it in the global map
    
    if g_certifications.has_key(int(id)):
        return g_certifications[int(id)]

    # TODO: try to find it in the database?
    
    return None


#---------------------------------------------------------------------------------------------------------
#
#                              u p d a t e G r o u p C e r t s
#
#  This function is called when a new Cert is added to the GroupCerts table.  After the new entry
#  is entered into the table, an entry is created in the CertTracking table for each employee in that
#  group.
#
#---------------------------------------------------------------------------------------------------------
def updateGroupCerts(con, groupId, certId):

    locus = "updateGroupCerts"

    logger.debug("%s: Updating groupcerts, groupId: %s, certId: %s" % (locus, groupId, certId))

    # Insert the new entry into the GroupCerts table
    
    with con:    
        cur = con.cursor()    

        cur.execute("select count(*) from groupcerts where groupid =? and certificationid =?;", (groupId, certId))

        if cur.rowcount > 0:
            logger.debug("%s: WARNING: record already exists" % locus)
            
            # TODO: return error and put up messagebox
            return
        
        cur.execute("select count(*) from groupcerts where groupid =? and certificationid =?;", (groupId, certId))

        try:
            cur.execute('insert into groupcerts (groupid, certificationid) values(?, ?)',
                  (groupId, certId))
        except sqlite3.Error, msg:
            logger.error("%s: %s: %s" % (locus, "ERROR: sqlite exception: ", msg))

        con.commit()

    # Get the certification table data we need

    with con:    
        cur = con.cursor()

        # TODO: should this query be restricted to Active only?

        cur.execute("select * from certifications where id = ?;", (certId,))

        if cur.rowcount == 0:
            logger.warn("%s: certification %s not found" % (locus, certId))
            
            # TODO: return error and put up messagebox
            return

        rows = cur.fetchall()

        for row in rows:
            initial = row["initial"]
            renewal = row["renewal"]
            
    # Now, iterate over all employees in that group, and create the CertTracking entries

    with con:
    
        cur = con.cursor()    

        cur.execute("select * from employees where groupId = ?;", (groupId,))

        rows = cur.fetchall()

        logger.debug("%s: found %s employees for group %s" % (locus, cur.rowcount, groupId))
            
        for row in rows:
            startDate = row["startdate"]
            empId = row["id"]

            startdateobj = datetime.date(datetime.strptime(str(startDate),'%Y%m%d'))

            if initial == None:
                renewDate = startdateobj + timedelta(days=renewal)
            else:
                renewDate = startdateobj + timedelta(days=initial)

            logger.debug("%s: empId %s, renewDate: %s" % (locus, empId, renewDate))
                
            # Next, create an EmployeeCertification object to insert a record into the CertTracking table;
            # note that the certDate will be None initially

            empCert = ec.EmployeeCertification(0, empId, certId, None, renewDate)

            addCertTracking(con, empCert)
            
    

#---------------------------------------------------------------------------------------------------------
#
#                              d e l e t e F r o m G r o u p C e r t s
#
#  This function is called when a Cert is deleted from, the GroupCerts table.  For each employee in that
#  group, we have to delete all certificationtracking table entries for the employee and cert.
#
#  When finished, we delete the groupcerts entry.
#
#---------------------------------------------------------------------------------------------------------
def deleteFromGroupCerts(con, groupId, certId):

    locus = "deleteFromGroupCerts"

    logger.debug("%s: Deleting from groupcerts, groupId: %s, certId: %s" % (locus, groupId, certId))
    
    # First, iterate over all employees in that group, and create the CertTracking entries

    with con:
    
        cur = con.cursor()    

        cur.execute("select * from employees where groupId = ?;", (groupId,))

        rows = cur.fetchall()

        logger.debug("%s: found %s employees for group %s" % (locus, cur.rowcount, groupId))
            
        for row in rows:
            empId = row["id"]
            deleteFromCertTrackingByEmpId(con, empId)

    with con:    
        cur = con.cursor()    

        try:
            cur.execute('delete from groupcerts where groupid =? and certificationid =?;',
                  (groupId, certId))
        except sqlite3.Error, msg:
            logger.error("%s: %s: %s" % (locus, "ERROR: sqlite exception: ", msg))

        con.commit()

    # reload the certtracking map 

    loadCertTracking(con)

#---------------------------------------------------------------------------------------------------------
#
#                              d e l e t e A l l G r o u p C e r t s
#
#---------------------------------------------------------------------------------------------------------
def deleteAllGroupCerts(con, groupId):

    locus = "deleteAllGroupCerts"

    logger.debug("%s: Deleting from groupcerts, groupId: %s" % (locus, groupId))
    
    with con:    
        cur = con.cursor()    

        try:
            cur.execute('delete from groupcerts where groupid =?;',(groupId,))
        except sqlite3.Error, msg:
            logger.error("%s: %s: %s" % (locus, "ERROR: sqlite exception: ", msg))

        con.commit()


#---------------------------------------------------------------------------------------------------------
#
#                                 a d d A l l G r o u p C e r t s
#
#---------------------------------------------------------------------------------------------------------
def addAllGroupCerts(con, groupId):

    locus = "addAllGroupCerts"

    logger.debug("%s: Adding all groupcerts, groupId: %s" % (locus, groupId))
    
    with con:    
        cur = con.cursor()    

        try:
            cur.execute('insert into groupcerts (groupid, certificationid) select ?, id from certifications;',
                  (groupId,))
        except sqlite3.Error, msg:
            logger.error("%s: %s: %s" % (locus, "ERROR: sqlite exception: ", msg))

        con.commit()

#---------------------------------------------------------------------------------------------------------
#
#                              l o a d  C e r t T r a c k i n g
#
#---------------------------------------------------------------------------------------------------------
def loadCertTracking(con):

    locus = "loadCertTracking"

    logger.debug("%s: ENTER" % locus)
    
    g_certtracking.clear()
    
    with con:    
        cur = con.cursor()    

        cur.execute("select * from certificationtracking;")

        rows = cur.fetchall()

        for row in rows:
            empCert = ec.EmployeeCertification(row["id"], row["employeeId"], row["certificationId"], row["certDate"], row["renewalDate"])

            if debugLoad == 1:
                logger.debug("id: %s, emplId: %s, certId: %s, date: %s, renewalDate: %s" % \
                      (row["id"], row["employeeId"], row["certificationId"], row["certDate"], row["renewalDate"]))
                
            g_certtracking[int(empCert.getId())] = empCert

            if debugLoad == 1:
                logger.debug(">>> created certification empId: %s" % newCert.getEmployeeId())

    logger.debug("%s: Created %d certtracking entries" % (locus, len(g_certtracking)))
        
    return g_certtracking


#---------------------------------------------------------------------------------------------------------
#
#                              g e t C e r t T r a c k i n g M a p
#
#---------------------------------------------------------------------------------------------------------
def getCertTrackingMap(con):
    return g_certtracking


#---------------------------------------------------------------------------------------------------------
#
#                              g e t C e r t N a m e B y I d
#
#---------------------------------------------------------------------------------------------------------
def getCertNameById(certId):
    cert = g_certifications[certId]

    return cert.certification


#---------------------------------------------------------------------------------------------------------
#
#                       g e t C e r t T r a c k i n g M a p B y E m p
#
#---------------------------------------------------------------------------------------------------------
def getCertTrackingMapByEmp(con, empId):

    locus = "getCertTrackingMapByEmp"

    logger.debug("%s: empId: %s, dictionary size: %s" % (locus, empId, len(g_certtracking)))
    
    # create an empty map
    tmp = {}

    for (key,value) in g_certtracking.items():
        logger.debug("%s: >>>>> key: %s, value: %s, empId: %s" % (locus, key, value, value.getEmployeeId()))
                         
        if empId == value.getEmployeeId():
            tmp[key] = value

            logger.debug("%s: >>>>> added entry to cert tracking map" % locus)

    return tmp


#---------------------------------------------------------------------------------------------------------
#
#                              d e l e t e F r o m C e r t T r a c k i n g B y E m p I d
#
#---------------------------------------------------------------------------------------------------------
def deleteFromCertTrackingByEmpId(con, empId):

    locus = "deleteFromCertTrackingByEmpId"

    logger.debug("%s: Deleting from certificationtracking, empId: %s" % (locus, empId))
    
    with con:    
        cur = con.cursor()    

        try:
            cur.execute('delete from certificationtracking where employeeId =?;',
                  (empId, ))
        except sqlite3.Error, msg:
            logger.error("%s: %s: %s" % (locus, "ERROR: sqlite exception: ", msg))

        con.commit()

#---------------------------------------------------------------------------------------------------------
#
#                              d e l e t e F r o m C e r t T r a c k i n g
#
#---------------------------------------------------------------------------------------------------------
def deleteFromCertTracking(con, id):

    locus = "deleteFromCertTracking"

    logger.debug("%s: Deleting from certificationtracking, id: %s" % (locus, id))
    
    with con:    
        cur = con.cursor()    

        try:
            cur.execute('delete from certificationtracking where id =?;',
                  (id, ))
        except sqlite3.Error, msg:
            logger.error("%s: %s: %s" % (locus, "ERROR: sqlite exception: ", msg))

        con.commit()


#---------------------------------------------------------------------------------------------------------
#
#                                 a d d C e r t T r a c k i n g
#
#---------------------------------------------------------------------------------------------------------
def addCertTracking(con, newEmpCert):

    locus = "addCertTracking"

    logger.debug("%s: Adding new cert tracking, empId: %s, certId: %s, certDate: %s, renewDate: %s" % \
        (locus, newEmpCert.getEmployeeId(), newEmpCert.getCertId(), newEmpCert.getCertDate(), newEmpCert.getRenewalDate()))
    
    c = con.cursor()

    try:
        c.execute("select count(*) from certificationtracking where employeeId =? and certificationId =?;",
                  (newEmpCert.getEmployeeId(), newEmpCert.getCertId()))

        if c.rowcount > 0:
            logger.debug("%s: WARNING: record already exists" % locus)
            
            # TODO: return error and put up messagebox
            return

        c.execute('insert into certificationtracking (employeeId, certificationId, certDate, renewalDate) values (?, ?, ?, ?)',
                  (newEmpCert.getEmployeeId(), newEmpCert.getCertId(), newEmpCert.getCertDate(), newEmpCert.getRenewalDate()))
    except sqlite3.Error, msg:
        logger.error("%s: %s: %s" % (locus, "ERROR: sqlite exception: ", msg))
        return

    # or c.lastrowid
    newEmpCert.setId(c.lastrowid)

    logger.debug("%s: added item, new id: %s" % (locus, newEmpCert.getId()))

    # update global map
    
    g_certtracking[int(newEmpCert.getId())] = newEmpCert

    con.commit()

#---------------------------------------------------------------------------------------------------------
#
#                                 insertKey 
#
#---------------------------------------------------------------------------------------------------------
def insertKey(con, newkey):

    print "insertKey: new key: %s" % newkey
    
    logger.debug("Insert key %s" % newkey)
    
    c = con.cursor()

    try:
        c.execute('insert into certConfig (licenseKey) values (?);',
                  (newkey,))
    except sqlite3.Error, msg:
        logger.error(msg)

    logger.debug("insertKey: added key: %s" % newkey)

    con.commit()

#---------------------------------------------------------------------------------------------------------
#
#                                 insertInstallDate
#
#---------------------------------------------------------------------------------------------------------
def insertInstallDate(con, newdate):

    print "insertInstallDate: new key: %s" % newdate
    
    logger.debug("Insert install date %s" % newdate)
    
    c = con.cursor()

    try:
        c.execute('insert into certConfig (installDate) values (?);',
                  (newdate,))
    except sqlite3.Error, msg:
        logger.error(msg)

    logger.debug("insertInstallDate: added install date: %s" % newdate)

    con.commit()



#---------------------------------------------------------------------------------------------------------
#
#                                 getKey 
#
#---------------------------------------------------------------------------------------------------------
def getKey(con):

    c = con.cursor()

    try:
        c.execute('select licenseKey from certConfig;')
    except sqlite3.Error, msg:
        logger.error(msg)

    data = c.fetchone()
    key = data[0]
    
    print "key = %s" % key
    
    if key == None:
        logger.warn("licenseKey not found")
        return None
    else:
        logger.info("Found licenseKey: %s" % key)
        return key
                    

#---------------------------------------------------------------------------------------------------------
#
#                                 getInstallDate 
#
#---------------------------------------------------------------------------------------------------------
def getInstallDate(con):

    locus = "getInstallDate"
    
    c = con.cursor()

    try:
        c.execute('select installDate from certConfig;')
    except sqlite3.Error, msg:
        logger.error(msg)

    data = c.fetchone()

    installDate = data["installDate"]
    
    #print "%s: installDate = %s" % (locus, installDate)
    
    if installDate == None:
        logger.warn("%s: installDate not found" % locus)
        return None
    else:
        logger.info("%s: Found installDate: %s" % (locus, installDate))
        return installDate
                    

#---------------------------------------------------------------------------------------------------------
#
#                                 a d d E m a i l A c c o u n t 
#
#---------------------------------------------------------------------------------------------------------
def addEmailAccount(con, user, password):

    locus = "addEmailAccount"
    
    print "%s: Adding email user %s, password: %s" % (locus, user, password)
    
    logger.debug("%s: Adding email user %s, password: %s" % (locus, user, password))
    
    c = con.cursor()

    # drop any existing data

##    try:
##        c.execute('delete from certConfig;')
##    except sqlite3.Error, msg:
##        print "msg: %s" % msg
##        logger.error(locus + ": delete table failed: " + msg)
##
##    print "Deleted table data"
    
    id = 1
    
    try:
        print "Updating table data"
        
        c.execute('update certConfig set gmailUser = ?, gmailPass = ? where id = 1',
                  (user, password))
    except sqlite3.Error, msg:
        print "msg: %s" % msg
        logger.error(locus + ": update failed: " + msg)

    con.commit()

    

#---------------------------------------------------------------------------------------------------------
#
#                                 g e t E m a i l A c c o u n t 
#
#---------------------------------------------------------------------------------------------------------
def getEmailAccount(con):

    locus = "getEmailAccount"
    
    
    c = con.cursor()

    try:
        c.execute('select * from certConfig where id = 1;')
    except sqlite3.Error, msg:
        logger.error(msg)

    data = c.fetchone()

    if data != None:
        user = data["gmailUser"]
        passw = data["gmailPass"]

        logger.debug("%s: Getting email user %s, password: %s" % (locus, user, passw))
    else:
        user = None
        passw = None
        
    # return as a list

    #print "returning list: %s" % [user,passw]
    
    return [user,passw]
