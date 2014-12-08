#---------------------------------------------------------------------------------------------------------
#
#   Module: certTracker.py
#
#   Author: Mitchell McConnell
#
#---------------------------------------------------------------------------------------------------------
#
#  Date     Who         Description
#
# 06/21/12  mjm         Original version
# 07/12/12  mjm         Added logging module and started logging
# 07/13/12  mjm         Added license key and registration code
#
#---------------------------------------------------------------------------------------------------------

import wx
import sys
import os
import string
import datetime 
import sqlite3
import smtplib
import socket
import group as g
import employee as e
import certification as c
import certDbUtils as dbUtils
import employeeCertification as ec
from datetime import datetime
import time
from datetime import timedelta
import logging
from certDialogs import RegisterDialog
import hashlib
import certErrors as cterr

certTracker_version = "00.00.04"

CT_MENU_REGISTER = 100
CT_MENU_ABOUT    = 101

CT_MAX_UNLICENSED_DAYS = 30

EMPLOYEE_NAME_WIDTH = 150
CERT_WIDTH = 210
DATES_WIDTH = 130
NOTES_WIDTH = 350
INITIAL_WIDTH = 100
RENEWAL_WIDTH = 100
GROUPS_WIDTH = 150
APP_WIDTH = 900
APP_HEIGHT = 550

statusList = ["Active","Inactive"]
pagesList = ["EmployeeCerts", "Certifications", "Employees", "Groups", "Group Certs"]

# set up logging stuff, note that the file logger and console loggers can have different levels

logger = logging.getLogger('certTracker')
#logger.setLevel(logging.CRITICAL)
#logger.setLevel(logging.ERROR)
#logger.setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)

fh = logging.FileHandler('certTracker.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
ch.setFormatter(formatter)
logger.addHandler(ch)


#---------------------------------------------------------------------------------------------------------
#
#     EmployeeCertsPanel
#
#---------------------------------------------------------------------------------------------------------

class EmployeeCertsPanel(wx.Panel):
    "Class to manage the layout for employee certifications"
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.name = "EmployeeCerts"

        logger.debug("%s: starting up" % self.name)
        
        # create some sizers 
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        ourFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_BOLD)
        
        # create a horizontal sizer, that will contain multiple vertical sizers
        
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        empSizer = wx.BoxSizer(wx.VERTICAL)
        certSizer = wx.BoxSizer(wx.VERTICAL)
        certDateSizer = wx.BoxSizer(wx.VERTICAL)
        renewDateSizer = wx.BoxSizer(wx.VERTICAL)
        reportsSizer = wx.BoxSizer(wx.VERTICAL)

        # create the static labels

        empText = wx.StaticText(self, -1, "Employee", size=(EMPLOYEE_NAME_WIDTH,-1));
        empText.SetFont(ourFont)
        
        certsText = wx.StaticText(self, -1, "Certifications", size=(CERT_WIDTH,-1));
        certsText.SetFont(ourFont)

        certDateText = wx.StaticText(self, -1, "Certification Date");
        certDateText.SetFont(ourFont)

        renewDateText = wx.StaticText(self, -1, "Renewal Date");
        renewDateText.SetFont(ourFont)

        reportsText = wx.StaticText(self, -1, "Reports");
        reportsText.SetFont(ourFont)

        # create editable fields
        
        self.notesText = wx.TextCtrl(self, -1, size=(CERT_WIDTH,-1));

        # create the employees list box
        
        self.employeeList = wx.ListBox(self, size=(EMPLOYEE_NAME_WIDTH,-1), style=wx.LC_REPORT)
        self.employeeList.Bind(wx.EVT_LISTBOX, self.OnEmployeeListSelected)

        # get from map, and add empId as the key

        self.LoadEmployeesList()

        # set the first entry as selected
        
        self.employeeList.SetSelection(0)

        initialEmpId = self.employeeList.GetClientData(0)
        
        # add the employees textbox and list to the employees sizer

        empSizer.Add(empText)

        empSizer.Add(self.employeeList)

        # create the certifications list box
        
        self.certsList = wx.ListBox(self, size=(CERT_WIDTH,-1), style=wx.LC_REPORT)
        self.certsList.Bind(wx.EVT_LISTBOX, self.OnCertsListSelected)

        numCerts = self.LoadCertsList()
        
        # get the cert object for the notes if there were any for the first employee in the employee listbox

        if numCerts > 0:
            initialCertId = self.certsList.GetClientData(0).getId()

            logger.debug("%s: initialCertId: %s" % (self.name, initialCertId))
                          
            certObj = dbUtils.findCertificationById(initialCertId)

            self.notesText.SetValue(certObj.getNotes())
        
            self.certsList.SetSelection(0)

        # create the certDates list box

        self.certDatesList = wx.ListBox(self, size=(DATES_WIDTH,-1), style=wx.LC_REPORT)

        # create the renewDates list box

        self.renewDatesList = wx.ListBox(self, size=(DATES_WIDTH,-1), style=wx.LC_REPORT)

        # fill in cert dates and renew dates

        self.LoadCertDatesList(initialEmpId)
        self.LoadRenewDatesList(initialEmpId)
        
        # add the certifications textbox, list, and notes to the certs sizer

        certSizer.Add(certsText)
        certSizer.Add(self.certsList)
        certSizer.Add(self.notesText)

        ourFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_BOLD)
        
        # Create the larger report buttons
        self.certReportButton = wx.Button(self, label="Certs\nReport", size=(100,50))
        self.Bind(wx.EVT_BUTTON, self.OnCertReportClick,self.certReportButton)
        self.certReportButton.SetFont(ourFont)

        self.allEmplButton = wx.Button(self, label="All Employee\nCert Report", size=(100,50))
        self.Bind(wx.EVT_BUTTON, self.OnAllEmplClick,self.allEmplButton)
        self.allEmplButton.SetFont(ourFont)

        self.certAlertsButton = wx.Button(self, label="Certification\nAlerts", size=(100,50))
        self.Bind(wx.EVT_BUTTON, self.OnCertAlertsClick,self.certAlertsButton)
        self.certAlertsButton.SetFont(ourFont)

        self.lookAheadButton = wx.Button(self, label="Look Ahead\nReport", size=(100,50))
        self.Bind(wx.EVT_BUTTON, self.OnLookAheadClick,self.lookAheadButton)
        self.lookAheadButton.SetFont(ourFont)

        # two smaller buttons
        
        self.deleteCertButton = wx.Button(self, label="Delete Cert Date")
        self.Bind(wx.EVT_BUTTON, self.OnDeleteCertClick,self.deleteCertButton)
        self.deleteCertButton.SetFont(ourFont)

        self.addCertButton = wx.Button(self, label="Add Cert Date")
        self.Bind(wx.EVT_BUTTON, self.OnAddCertClick,self.addCertButton)
        self.addCertButton.SetFont(ourFont)

        # create a small horizontal sizer for the delete cert date and plus and minus buttons

        self.addDelCertDateSizer = wx.BoxSizer(wx.HORIZONTAL)

        #  add the cert date textbox and buttons to the certDateSizer

        self.newCertDatePicker = wx.DatePickerCtrl(self, size=(120,-1),
                                style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY)
        self.addDelCertDateSizer.Add(self.newCertDatePicker)

        # set up the renewDateSizer

        renewDateSizer.Add(renewDateText)
        renewDateSizer.Add(self.renewDatesList)
        
        # set up the certDatesSizer

        certDateSizer.Add(certDateText)
        certDateSizer.Add(self.certDatesList)
        certDateSizer.Add(self.deleteCertButton)
        certDateSizer.Add(self.addDelCertDateSizer)
        certDateSizer.Add(self.addCertButton)
        
        # add the buttons to the reports sizer
        
        reportsSizer.Add(reportsText, 0, wx.ALL, 5)
        reportsSizer.Add(self.certReportButton, 0, wx.ALL, 5)
        reportsSizer.Add(self.allEmplButton, 0, wx.ALL, 5)
        reportsSizer.Add(self.certAlertsButton, 0, wx.ALL, 5)
        reportsSizer.Add(self.lookAheadButton, 0, wx.ALL, 5)

        hSizer.Add(empSizer, 0, wx.ALL, 10)
        hSizer.Add(certSizer, 0, wx.ALL, 10)
        hSizer.Add(certDateSizer, 0, wx.ALL, 10)
        hSizer.Add(renewDateSizer, 0, wx.ALL, 10)
        hSizer.Add(reportsSizer, 0, wx.ALL, 10)

        mainSizer.Add(hSizer, 0, wx.ALL, 20)
        
        self.SetSizer(mainSizer)
        self.Show()


    def LoadCertsList(self):

        locus = "LoadCertsList"
                          
        self.certsList.Clear()
        
        cMap = dbUtils.getCertificationMap()

        logger.debug("%s: cMap length: %s" % (locus, len(cMap)))
        
        for (key,value) in cMap.items():
            logger.debug(">>>>> ##### key: %s, value: %s, certId: %s" % (key, value,value.getId()))

            # Save the certification object as the user data for the certsList listctrl
            
            self.certsList.Append(dbUtils.getCertNameById(value.getId()), value)

        return len(cMap)


    def LoadEmployeesList(self):

        self.employeeList.Clear()
        
        eMap = dbUtils.getEmployeeMap()
        gMap = dbUtils.getGroupMap()

        for (key,value) in eMap.items():
            logger.debug( ">>>>> key: %s, value: %s" % (key, value))
            group = gMap[value.getGroupId()]
            
            self.employeeList.Append("%s (%s)" % (value.getFullName(), group.getName()), key)

        return

    def LoadCertDatesList(self, empId = None):
        locus =  "LoadCertDatesList"

        self.certDatesList.Clear()

        certIndex = self.certsList.GetSelection()

        if certIndex == -1:
            certIndex = 0
            
        logger.debug( "%s: certIndex: %s" % (locus, certIndex))
        certObj = self.certsList.GetClientData(certIndex)
        logger.debug( "%s: certIndex: %s, certId: %s" % (locus, certIndex, certObj.getId()))

        if empId == None:
            empIndex = self.employeeList.GetSelection()
            empId = self.employeeList.GetClientData(empIndex)
            logger.debug( "%s: Selected emp index: %s, empId: %s" % (locus, empIndex, empId))
        
        ecMap = dbUtils.getCertTrackingMapByEmp(con, empId)

        logger.debug( "%s: >>>>> @@@@@ len(ecMap): %s" %  (locus,len(ecMap)))
        
        for (key,value) in ecMap.items():
            logger.debug( "%s: >>>>> @@@@@ key: %s, value: %s" % (locus, key, value.getId()))

            if value.getCertId() == certObj.getId():
                self.certDatesList.Append(str(value.getCertDate()), value)


    def LoadRenewDatesList(self, empId = None):
        locus =  "LoadRenewDatesList"

        certIndex = self.certsList.GetSelection()

        if certIndex == -1:
            certIndex = 0

        certObj = self.certsList.GetClientData(certIndex)
        logger.debug( "%s: certIndex: %s, certId: %s" % (locus, certIndex, certObj.getId()))

        if empId == None:
            empIndex = self.employeeList.GetSelection()
            empId = self.employeeList.GetClientData(empIndex)
            logger.debug( "%s: Selected emp index: %s, empId: %s" % (locus, empIndex, empId))

        self.renewDatesList.Clear()
        
        ecMap = dbUtils.getCertTrackingMapByEmp(con, empId)

        logger.debug( "%s: >>>>> @@@@@ len(ecMap): %s" % (locus, len(ecMap)))
        
        for (key,value) in ecMap.items():
            logger.debug( "%s: >>>>> @@@@@ key: %s, value: %s, renewalDate: %s" % (locus, key, value.getId(), value.getRenewalDate()))
                
            if value.getCertId() == certObj.getId():
                self.renewDatesList.Append(str(value.getRenewalDate()), value)

        
    def EvtComboBox(self, event):
        #self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())
        logger.debug( "%s: ComboBox event" % self.name)
        
    def OnCertReportClick(self,event):
        #self.logger.AppendText('EvtComboBox: New button clicked %s\n' % event.GetString())
        logger.debug( "%s: OnCertReportClick button event" % self.name)
        
    def OnAllEmplClick(self,event):
        #self.logger.AppendText('EvtComboBox: Save button clicked %s\n' % event.GetString())
        logger.debug( "%s: OnAllEmplClick button event" % self.name)
        
    def OnCertAlertsClick(self,event):
        #self.logger.AppendText('EvtComboBox: Save button clicked %s\n' % event.GetString())
        logger.debug( "%s: OnCertAlertsClick button event" % self.name)
        
    def OnLookAheadClick(self,event):
        #self.logger.AppendText('EvtComboBox: Save button clicked %s\n' % event.GetString())
        logger.debug( "%s: OnLookAheadClick button event" % self.name)
        
    def OnDeleteCertClick(self,event):
        #self.logger.AppendText('EvtComboBox: Save button clicked %s\n' % event.GetString())
        logger.debug( "%s: OnDeleteCertClick button event" % self.name)
        certRow = self.certDatesList.GetSelection()
        logger.debug( "Cert Row: " + str(certRow))

        data = self.certDatesList.GetString(certRow)
        logger.debug( "Delete data: %s"  % data)
        certObj = self.certDatesList.GetClientData(certRow)
        logger.debug( "Cert Obj: %s, id: %s" % (certObj, certObj.getId()))

        # put up dialog box to make sure they really want to delete

        msg = "Do you really want to delete certification date %s?"  % data
        
        dial = wx.MessageDialog(None, msg, 'WARNING', wx.OK | wx.ICON_WARNING)
        if dial.ShowModal() == wx.OK:
            dbUtils.deleteFromCertTracking(con, certObj.getId())
        else:
            return
        
        empIndex = self.employeeList.GetSelection()
        logger.debug( "Selected emp index: %s" % empIndex)
        empId = self.employeeList.GetClientData(empIndex)
        logger.debug( "Employee Id: %s" % empId)
        
        # Refresh certDatesList and renewDatesList
        dbUtils.loadCertTracking(con)
        self.LoadCertDatesList(empId)
        self.LoadRenewDatesList(empId)
        
    def OnAddCertClick(self,event):
        #self.logger.AppendText('EvtComboBox: Save button clicked %s\n' % event.GetString())
        logger.debug( "%s: OnAddCertClick button event" % self.name)
        row = event.GetSelection()
        logger.debug( "Row: " + str(row))

        index = event.GetSelection()
        startDate = self.newCertDatePicker.GetValue()
        month = startDate.Month + 1
        day = startDate.Day
        year = startDate.Year
        date_str = "%4d-%02d-%02d" % (year, month, day)
        logger.debug( "Selected date: %s" % date_str)

        # get employeeId and certId to add to certificationtracking table
        empIndex = self.employeeList.GetSelection()
        logger.debug( "Selected emp index: %s" % empIndex)
        empId = self.employeeList.GetClientData(empIndex)
        logger.debug( "Employee Id: %s" % empId)

        # get the employee id, as we may need the start date
        
        eMap = dbUtils.getEmployeeMap()

        empObj = eMap[empId]
        
        certIndex = self.certsList.GetSelection()
        logger.debug( "Selected cert index: %s" % certIndex)
        certObj = self.certsList.GetClientData(certIndex)
        logger.debug( "Cert Id: %s, initial: %s, renewal: %s" % (certObj.getId(), certObj.getInitial(), certObj.getRenewal()))

        # calculate the renew date

        initial = certObj.getInitial()
        renewal = certObj.getRenewal()
            
        startdateobj = datetime.date(datetime.strptime(str(empObj.getStartDate()),'%Y%m%d'))

        
        if initial != None:
            renew_date = startdateobj + timedelta(days=initial)
            logger.debug( "calculated renew_date: %s" % renew_date)
        
        # create the EmployeeCertification object

        tmpId = 0
        
        empCert = ec.EmployeeCertification(tmpId, empId, certObj.getId(), date_str, renew_date)

        dbUtils.addCertTracking(con, empCert)
        
        # Refresh certDatesList and renewDatesList
        dbUtils.loadCertTracking(con)
        self.LoadCertDatesList(empId)
        self.LoadRenewDatesList(empId)

        logger.debug( ">>>>>>>>>>>>>>>>>>>  done <<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n")
        
    def OnEmployeeListSelected(self, event):
        logger.debug( "%s: OnEmployeeListSelected button event" % self.name)

        # go ahead and clear the list ctrls
        
        #self.certsList.Clear()
        self.certDatesList.Clear()
        self.renewDatesList.Clear()
        
        #logger.debug( "Event data %s" % event.GetText() 
        row = event.GetSelection()
        
        logger.debug( "Row: " + str(row))

        index = event.GetSelection()
        data = self.employeeList.GetString(index)
        
        logger.debug( "Selected index: %s, Group: %s" % (index, data))
            
        empId = self.employeeList.GetClientData(index)
        
        logger.debug( "Employee Id: %s" % empId)

        # Get the currently selected cert from the cert list 
        certIndex = self.certsList.GetSelection()

        if certIndex == -1:
            certIndex = 0
            
        certObj = self.certsList.GetClientData(certIndex)
        logger.debug( "certIndex: %s, certId: %s" % (certIndex, certObj.getId()))

        # Refresh certDatesList and renewDatesList
        self.LoadCertDatesList(empId)
        self.LoadRenewDatesList(empId)

    def OnCertsListSelected(self, event):
        logger.debug( "%s: OnCertsListSelected button event" % self.name)
        #logger.debug( "Event data %s" % event.GetText())
        row = event.GetSelection()
        logger.debug( "Row: " + str(row))

        # go ahead and clear the dates list ctrls

        logger.debug( ".... clearing certDatesList and renewDatesList")
            
        self.certDatesList.Clear()
        self.renewDatesList.Clear()
        
        certObj = self.certsList.GetClientData(row)

        # get the notes for the selected certification
        
        initialCertId = certObj.getId()

        logger.debug( "initialCertId: %s" % initialCertId)
        
        logger.debug( "Cert Obj, initial %s, renewal %s" % (certObj.getInitial(), certObj.getRenewal()))
        
        if certObj.getNotes != None:
            self.notesText.SetValue(certObj.getNotes())

        # Get the currently selected cert from the cert list 
        certIndex = self.certsList.GetSelection()
        certObj = self.certsList.GetClientData(certIndex)
        logger.debug( "certIndex: %s, certId: %s" % (certIndex, certObj.getId()))

        # Get the currently selected employee from the employees list 
        empIndex = self.employeeList.GetSelection()
        empId = self.employeeList.GetClientData(empIndex)

        logger.debug( "empIndex: %s, empId: %s" % (empIndex, empId))

        # fill in cert dates and renew dates

        self.LoadCertDatesList(empId)
        self.LoadRenewDatesList(empId)



#---------------------------------------------------------------------------------------------------------
#
#     CertificationsPanel
#
#---------------------------------------------------------------------------------------------------------

class CertificationsPanel(wx.Panel):
    "Class to manage the layout for certifications"

    global debug
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.name = "Certifications"

        self.lastClickedId = None
        self.showInactive = False
        
        # create some sizers 
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.list = wx.ListCtrl(self, size=(100,110), style=wx.LC_REPORT)
        
        self.list.InsertColumn(0, 'Id')
        self.list.InsertColumn(1, 'Certification')
        self.list.InsertColumn(2, 'Initial')
        self.list.InsertColumn(3, 'Renewal')
        self.list.InsertColumn(4, 'Notes')

        # Note: hide the Id column
        self.list.SetColumnWidth(0,0)
        
        self.list.SetColumnWidth(1,CERT_WIDTH)
        self.list.SetColumnWidth(2,INITIAL_WIDTH)
        self.list.SetColumnWidth(3,RENEWAL_WIDTH)
        self.list.SetColumnWidth(4,NOTES_WIDTH)

        self.updateCertsList(False)

        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListSelected)

        # create the horizontal sizer for data entry fields
        
        self.newDataSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create the 4 text fields for the data entry

        self.newCertText = wx.TextCtrl(self, -1, size=(CERT_WIDTH,-1))
        self.newInitialText = wx.TextCtrl(self, -1)
        self.newRenewalText = wx.TextCtrl(self, -1)
        self.newNotesText = wx.TextCtrl(self, -1, size=(NOTES_WIDTH,-1))

        self.newDataSizer.Add(self.newCertText)
        self.newDataSizer.Add(self.newInitialText)
        self.newDataSizer.Add(self.newRenewalText)
        self.newDataSizer.Add(self.newNotesText)
        
        # create the horizontal sizer for the checkbox and buttons
        
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        # checkbox

        self.showInactCkB = wx.CheckBox(self, label='Show Inactive Certifications')
        self.Bind(wx.EVT_CHECKBOX, self.ShowInactCkB)
        
        # A button
        self.inactButton = wx.Button(self, label="Inactivate")
        self.Bind(wx.EVT_BUTTON, self.OnInactClick,self.inactButton)

        self.newButton = wx.Button(self, label="New")
        self.Bind(wx.EVT_BUTTON, self.OnNewClick,self.newButton)

        self.saveButton = wx.Button(self, label="Save")
        self.Bind(wx.EVT_BUTTON, self.OnSaveClick,self.saveButton)

        # add the buttons to the button sizer
        
        self.buttonSizer.Add(self.showInactCkB, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        self.buttonSizer.Add(self.inactButton, 0, wx.ALL, 5)
        self.buttonSizer.Add(self.newButton, 0, wx.ALL, 5)
        self.buttonSizer.Add(self.saveButton, 0, wx.ALL, 5)

        mainSizer.Add(self.list, 0, wx.EXPAND|wx.ALL, 5)

        mainSizer.Add(self.newDataSizer, flag=wx.ALIGN_LEFT|wx.LEFT, border=10)

        mainSizer.Add(self.buttonSizer, flag=wx.ALIGN_LEFT|wx.LEFT, border=10)

        self.SetSizer(mainSizer)
        self.Show()

    def updateCertsList(self, showInactive):
        dbUtils.loadCertifications(con)
        self.list.DeleteAllItems()

        for cert in dbUtils.getCertificationList():

            if (showInactive == False) and (cert.isActive() == False):
                pass
            else:
                index = self.list.InsertStringItem(sys.maxint, str(cert.getId()))
                self.list.SetStringItem(index, 1, str(cert.getCertification()))
                self.list.SetStringItem(index, 2, str(cert.getInitial()))
                self.list.SetStringItem(index, 3, str(cert.getRenewal()))
                self.list.SetStringItem(index, 4, str(cert.getNotes()))

    def EvtComboBox(self, event):
        self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())
        
    def OnInactClick(self,event):
        logger.debug( "%s: OnInactClick button event" % self.name)
            
        newCert = dbUtils.findCertificationById(self.lastClickedId)

        if newCert == None:
            logger.debug( "ERROR: certification not found!")
            dbUtils.dumpCertificationMap()
        else:
            newCert.setActive(False)

            logger.debug( "Updating certification id %s, name %s, init: %s, renew: %s, status %s" % \
                  (self.lastClickedId, newCert.getCertification(), newCert.getInitial(),newCert.getRenewal(),newCert.isActive()))
                
            dbUtils.updateCertification(con, newCert)
            self.updateCertsList(self.showInactive)
        
    def OnNewClick(self,event):

        logger.debug( "%s: OnNewClick button event" % self.name)
            
        self.lastClickedId = None
        
        self.newCertText.SetValue('')
        self.newInitialText.SetValue('')
        self.newRenewalText.SetValue('')
        self.newNotesText.SetValue('')

        self.newCertText.SetFocus()
        
    def OnSaveClick(self,event):
        global certsUpdate

        logger.debug( "%s: OnSaveClick button event" % self.name)
        logger.debug( "%s: cert name: %s" % (self.name, self.newCertText.GetValue()))
        logger.debug( "%s: initial: %s, renewal: %s" % (self.name, self.newInitialText.GetValue(), self.newRenewalText.GetValue()))
        logger.debug( "%s: notes: %s" % (self.name,self.newNotesText.GetValue()))
        
        # if this cert already exists, do an update, else do an insert

        if self.lastClickedId == None:

            logger.debug( "%s: certification not found... creating new" % self.name)
            
            newCert = c.Certification(0, self.newCertText.GetValue(), self.newInitialText.GetValue(), self.newRenewalText.GetValue(), \
                                      1, self.newNotesText.GetValue())
            dbUtils.addCertification(con, newCert)
            certsUpdate = True
            
            # set as if the user selected this guy
            self.lastClickedId = newCert.getId()
            self.updateCertsList(self.showInactive)
        else:
            logger.debug( "Updating certification id %s" % self.lastClickedId)
                
            newCert = dbUtils.findCertificationById(self.lastClickedId)

            if newCert == None:
                logger.debug( "ERROR: certification not found for id: %s" % self.lastClickedId)
                dbUtils.dumpCertificationMap()
            else:
                logger.debug( "Updating certification id %s, name %s, init: %s, renew: %s, status %s" % \
                      (self.lastClickedId, newCert.getCertification(), newCert.getInitial(),newCert.getRenewal(),newCert.isActive()))
                    
                newCert.setActive(newCert.isActive())
                newCert.setInitial(self.newInitialText.GetValue())
                newCert.setRenewal(self.newRenewalText.GetValue())
                newCert.setNotes(self.newNotesText.GetValue())
                dbUtils.updateCertification(con, newCert)
                self.updateCertsList(self.showInactive)

        logger.debug( "TODO: update the renewal date for every employee that has this cert in the certificationTracking table!")
        

    def OnListSelected(self, event):

        logger.debug( "%s: OnListSelected button event" % self.name)
        logger.debug( "Event data %s" % event.GetText())
            
        row = event.GetIndex()
        row = event.GetIndex()
        self.lastClickedId = self.list.GetItem(row, 0).GetText()

        logger.debug( "Row: %s, lastClicked: %s" %  (str(row), self.lastClickedId))
            
        self.newCertText.SetValue(self.list.GetItem(row, 1).GetText())
        self.newInitialText.SetValue(self.list.GetItem(row, 2).GetText())
        self.newRenewalText.SetValue(self.list.GetItem(row, 3).GetText())
        self.newNotesText.SetValue(self.list.GetItem(row, 4).GetText())
        
    def ShowInactCkB(self, event):
        if self.showInactive == True:
            self.showInactive = False
        else:
            self.showInactive = True

        logger.debug( "%s: ShowInactCkB button event, current state %s" % (self.name,str(self.showInactive)))
            
        self.updateCertsList(self.showInactive)
        
#---------------------------------------------------------------------------------------------------------
#
#     EmployeesPanel
#
#---------------------------------------------------------------------------------------------------------

class EmployeesPanel(wx.Panel):
    "Class to manage the layout for employees"
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.name = "Employees"
        self.lastClickedId = None
        
        # create some sizers 
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.list = wx.ListCtrl(self, size=(450,110), style=wx.LC_REPORT)

        self.list.InsertColumn(0, 'Id')
        self.list.InsertColumn(1, 'Employee')
        self.list.InsertColumn(2, 'Group')
        self.list.InsertColumn(3, 'Start Date')
        self.list.InsertColumn(4, 'Status')

        # set up event handler
        
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListSelected)

        # Try and hide the Id column, and set other column widths

        self.list.SetColumnWidth(0, 0)
        self.list.SetColumnWidth(1,EMPLOYEE_NAME_WIDTH)
        
        for emp in dbUtils.getEmployeeList():
            index = self.list.InsertStringItem(sys.maxint, str(emp.getId()))
            self.list.SetStringItem(index, 1, ''.join([emp.getLastName(), ',', emp.getFirstName()]))
            empGroup = dbUtils.findGroupById(emp.getGroupId())
            
            self.list.SetStringItem(index, 2, empGroup.getName())
            self.list.SetStringItem(index, 3, str(emp.getStartDate()))
            self.list.SetStringItem(index, 4, "Active" if emp.isActive() == True else "Inactive")

        # create the horizontal sizer for data entry fields
        
        self.newDataSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create the horizontal sizer for the buttons
        
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create the 4 text fields for the data entry

        self.newEmplText = wx.TextCtrl(self, -1, size=(EMPLOYEE_NAME_WIDTH,-1))

        groupList = [g.getName() for g in dbUtils.getGroupList()]

        self.newGroupCombo = wx.ComboBox(self, -1, style=wx.CB_READONLY, choices=groupList)
        self.newGroupCombo.SetStringSelection(groupList[0])

        
        self.newStartDatePicker = wx.DatePickerCtrl(self, size=(120,-1),
                                style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY)

        self.newStatusCombo = wx.ComboBox(self, -1, style=wx.CB_READONLY, choices=statusList)
        self.newStatusCombo.SetStringSelection("Active")

        self.newDataSizer.Add(self.newEmplText)
        self.newDataSizer.Add(self.newGroupCombo)
        self.newDataSizer.Add(self.newStartDatePicker)

        self.newDataSizer.Add(self.newStatusCombo)
        
        # Create new and save buttons
        self.newButton = wx.Button(self, label="New")
        self.Bind(wx.EVT_BUTTON, self.OnNewClick,self.newButton)

        self.saveButton = wx.Button(self, label="Save")
        self.Bind(wx.EVT_BUTTON, self.OnSaveClick,self.saveButton)

        # add the buttons to the button sizer
        
        self.buttonSizer.Add(self.newButton, 0, wx.ALL, 5)
        self.buttonSizer.Add(self.saveButton, 0, wx.ALL, 5)


        mainSizer.Add(self.list, 0, wx.ALL, 5)
        mainSizer.Add(self.newDataSizer, 0, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(self.buttonSizer, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.Show()

    def updateEmployeesList(self):
        dbUtils.loadEmployees(con)
        self.list.DeleteAllItems()
        
        for emp in dbUtils.getEmployeeList():
            index = self.list.InsertStringItem(sys.maxint, str(emp.getId()))
            self.list.SetStringItem(index, 1, ''.join([emp.getLastName(), ',', emp.getFirstName()]))
            empGroup = dbUtils.findGroupById(emp.getGroupId())
            
            self.list.SetStringItem(index, 2, empGroup.getName())
            self.list.SetStringItem(index, 3, str(emp.getStartDate()))
            self.list.SetStringItem(index, 4, "Active" if emp.isActive() == True else "Inactive")

    def EvtComboBox(self, event):
        self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())

    def OnNewClick(self,event):
        self.lastClickedId = None

        logger.debug( "%s: OnNewClick button event" % self.name)
        logger.debug( "%s: status: %s" % (self.name, self.newGroupCombo.GetValue()))
        self.newEmplText.SetValue('')
        self.newEmplText.SetFocus()
        
    def OnSaveClick(self,event):

        global employeeUpdate
        
        logger.debug( "%s: employee name: %s" % (self.name, self.newEmplText.GetValue()))
        logger.debug( "%s: group: %s" % (self.name, self.newGroupCombo.GetValue()))
        logger.debug( "%s: lastClickedId: %s" % (self.name,self.lastClickedId))


        startDate = self.newStartDatePicker.GetValue()
        month = startDate.Month + 1
        day = startDate.Day
        year = startDate.Year
        date_str = "%4d%02d%02d" % (year, month, day)
        logger.debug( "Selected date: %s" % date_str)

        # check for date reasonability

        tmp = datetime.now()
        today = tmp.strftime("%Y%m%d")
        logger.debug( "today = %s" % today)

        if date_str > today:
            msg = "Start date must be prior to today: " + today
            dial = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            return
        
        # NOTE: because we populate the Group combobox, we should always be able to find it!
        
        group = dbUtils.findGroupByName(con, self.newGroupCombo.GetValue())

        if self.newStatusCombo.GetValue() == 'Active':
            status = True
        else:
            status = False

        # if this employee already exists, do an update, else do an insert

        if self.lastClickedId == None:
            logger.debug( "%s: TODO: employee not found... creating new" % self.name)
            names = self.newEmplText.GetValue().split(',')
            
            newEmployee = e.Employee(0,names[1], names[0], status, date_str, group.getId())
            dbUtils.addEmployee(con, newEmployee)
            employeeUpdate = True
            dbUtils.loadEmployees(con)
            
            # set as if the user selected this guy
            self.lastClickedId = newEmployee.getId()
            self.updateEmployeesList()
        else:
            logger.debug( "Updating employee id %s" % self.lastClickedId)
            newEmployee = dbUtils.findEmployeeById(self.lastClickedId)

            if newEmployee == None:
                logger.debug( "ERROR: employee not found!")
                dbUtils.dumpEmployeeMap()
            else:
                logger.debug( "Updating employee id %s, name %s, status %s" % (self.lastClickedId, newEmployee.getFullName(),status))
                newEmployee.setActive(status)
                newEmployee.setStartDate(date_str)
                newEmployee.setGroupId(group.getId())
                dbUtils.updateEmployee(con, newEmployee)
                self.updateEmployeesList()

    def OnListSelected(self, event):
        logger.debug( "%s: OnListSelected button event" % self.name)
        row = event.GetIndex()
        self.lastClickedId = self.list.GetItem(row, 0).GetText()

        logger.debug( "%s: >>>> employeeId: %s" % (self.name, self.lastClickedId))
        logger.debug( "Selected employee: %s" % self.list.GetItem(row, 1).GetText())
            
        self.newEmplText.SetValue(self.list.GetItem(row, 1).GetText())
        logger.debug( "Row: " + str(row))

#---------------------------------------------------------------------------------------------------------
#
#     GroupsPanel
#
#---------------------------------------------------------------------------------------------------------

class GroupsPanel(wx.Panel):
    "Class to manage the layout for groups"
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.name = "Groups"

        # create some sizers 
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.list = wx.ListCtrl(self, size=(300,100), style=wx.LC_REPORT)

        self.list.InsertColumn(0, 'Id')
        self.list.InsertColumn(1, 'Group')
        self.list.InsertColumn(2, 'Status')

        for g in dbUtils.getGroupList():
            index = self.list.InsertStringItem(sys.maxint, str(g.getId()))
            self.list.SetStringItem(index, 1, g.getName())
            self.list.SetStringItem(index, 2, "Active" if g.isActive() == True else "Inactive")

        # Try and hide the Id column

        self.list.SetColumnWidth(0, 0)
        
        # set up event handler for listctrl
        
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListSelected)

        # create the horizontal sizer for data entry fields
        
        self.newDataSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create the horizontal sizer for the buttons
        
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        # TODO: get the list of groups and use as the 'choices' list
        
        self.newGroupText = wx.TextCtrl(self, -1)
        self.newGroupCombo = wx.ComboBox(self, -1, style=wx.CB_READONLY, choices=statusList)
        self.newGroupCombo.SetStringSelection("Active")
        
        self.newDataSizer.Add(self.newGroupText)
        self.newDataSizer.Add(self.newGroupCombo)
        
        # Create new and save buttons
        self.newButton = wx.Button(self, label="New")
        self.Bind(wx.EVT_BUTTON, self.OnNewClick,self.newButton)

        self.saveButton = wx.Button(self, label="Save")
        self.Bind(wx.EVT_BUTTON, self.OnSaveClick,self.saveButton)

        # add the buttons to the button sizer
        
        self.buttonSizer.Add(self.newButton, 0, wx.ALL, 5)
        self.buttonSizer.Add(self.saveButton, 0, wx.ALL, 5)

        #mainSizer.Add(self.list, 0, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(self.list, 0, wx.ALL, 5)
        mainSizer.Add(self.newDataSizer, 0, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(self.buttonSizer, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.Show()

    def updateGroupsList(self):
        dbUtils.loadGroups(con)
        self.list.DeleteAllItems()

        logger.debug( "%s: updating groups list" % self.name)
        
        for g in dbUtils.getGroupList():
            index = self.list.InsertStringItem(sys.maxint, str(g.getId()))
            self.list.SetStringItem(index, 1, g.getName())
            self.list.SetStringItem(index, 2, "Active" if g.isActive() == True else "Inactive")

    def EvtComboBox(self, event):
        self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())

    def OnNewClick(self,event):
        logger.debug( "%s: status: %s" % (self.name, self.newGroupCombo.GetValue()))
        logger.debug( "%s: OnNewClick button event" % self.name)
        self.newGroupText.SetValue('')
        self.newGroupText.SetFocus()
        
    def OnSaveClick(self,event):
        logger.debug( "%s: OnSaveClick button event" % self.name)
        logger.debug( "%s: newGroup name: %s" % (self.name, self.newGroupText.GetValue()))
        logger.debug( "%s: status: %s" % (self.name, self.newGroupCombo.GetValue()))

        # TODO: if this already exists, do an update, else do an insert

        if self.newGroupCombo.GetValue() == 'Active':
            status = True
        else:
            status = False

        newGroup = dbUtils.findGroupByName(con, self.newGroupText.GetValue())
        
        if newGroup == None:
            newGroup = g.Group(0,self.newGroupText.GetValue(), status)
            dbUtils.addGroup(con, newGroup)
            self.updateGroupsList()
        else:
            logger.debug( "TODO: Updating group %s, status %s" % (newGroup.getName(),status))
            newGroup.setActive(status)
            dbUtils.updateGroup(con, newGroup)
            self.updateGroupsList()

    def OnListSelected(self, event):
        logger.debug( "%s: OnListSelected button event" % self.name)
        row = event.GetIndex()
        self.lastClickedId = self.list.GetItem(row, 0).GetText()

        logger.debug( "%s: >>>> groupId: %s" % (self.name, self.lastClickedId))
        logger.debug( "Selected group: %s" % self.list.GetItem(row, 1).GetText())
            
        self.newGroupText.SetValue(self.list.GetItem(row, 1).GetText())
        logger.debug( "Row: " + str(row))

#---------------------------------------------------------------------------------------------------------
#
#     GroupCertsPanel
#
#---------------------------------------------------------------------------------------------------------

class GroupCertsPanel(wx.Panel):
    "Class to manage the layout for group certifications"
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.name = "GroupCertsPanel"
        
        ourFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_BOLD)

        # create the static labels

        groupsText = wx.StaticText(self, -1, "Groups");
        groupsText.SetFont(ourFont)
        
        certsText = wx.StaticText(self, -1, "Certifications");
        certsText.SetFont(ourFont)

        groupCertsText = wx.StaticText(self, -1, "Group Certifications");
        groupCertsText.SetFont(ourFont)

        # create some sizers 
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # create the 3 main listBoxes
        
        self.groupsList = wx.ListBox(self, size=(GROUPS_WIDTH,100), style=wx.LC_REPORT)
        self.groupsList.Bind(wx.EVT_LISTBOX, self.OnGroupsListSelected)

        self.certsList = wx.ListBox(self, size=(CERT_WIDTH,100), style=wx.LC_REPORT)
        self.certsList.Bind(wx.EVT_LISTBOX, self.OnCertsListSelected)

        self.groupCertsList = wx.ListBox(self, size=(CERT_WIDTH,100), style=wx.LC_REPORT)
        self.groupCertsList.Bind(wx.EVT_LISTBOX, self.OnGroupCertsListSelected)

        # use a map so we can store the group's key

        gMap = dbUtils.getGroupMap()

        for (key,value) in gMap.items():
            logger.debug(">>>>> key: %s, value: %s" % (key, value))
            self.groupsList.Append(value.getName(), key)

        self.groupsList.SetSelection(0)

        self.loadCertsList()
        
        # now, get the certfications for the selected group

        self.loadGroupCertsList(index=0)
        
        # create a horizontal sizer for the 4 vertical ones
        
        hSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create the vertical sizers
        
        groupsSizer = wx.BoxSizer(wx.VERTICAL)
        certsSizer = wx.BoxSizer(wx.VERTICAL)
        arrowsSizer = wx.BoxSizer(wx.VERTICAL)
        groupCertsSizer = wx.BoxSizer(wx.VERTICAL)

        # add the text labels and listboxes to their respective sizers

        groupsSizer.Add(groupsText, border=20)
        groupsSizer.Add(self.groupsList, border=20)

        certsSizer.Add(certsText, border=20)
        certsSizer.Add(self.certsList, border=20)

        groupCertsSizer.Add(groupCertsText, border=20)
        groupCertsSizer.Add(self.groupCertsList, border=20)
        
        # create 4 arrow buttons
        
        rightButton = wx.Button(self, label=">", size=(30,30))
        self.Bind(wx.EVT_BUTTON, self.OnRightClick,rightButton)
        rightButton.SetFont(ourFont)

        allRightButton = wx.Button(self, label=">>", size=(30,30))
        self.Bind(wx.EVT_BUTTON, self.OnAllRightClick,allRightButton)
        allRightButton.SetFont(ourFont)

        leftButton = wx.Button(self, label="<", size=(30,30))
        self.Bind(wx.EVT_BUTTON, self.OnLeftClick,leftButton)
        leftButton.SetFont(ourFont)

        allLeftButton = wx.Button(self, label="<<", size=(30,30))
        self.Bind(wx.EVT_BUTTON, self.OnAllLeftClick,allLeftButton)
        allLeftButton.SetFont(ourFont)

        # add the arrow buttons to the arrowSizer

        arrowsSizer.Add(rightButton, border=20)
        arrowsSizer.Add(allRightButton, border=20)
        arrowsSizer.Add(leftButton, border=20)
        arrowsSizer.Add(allLeftButton, border=20)
        
        # add the vertical sizers to the horizontal one

        #reportsSizer.Add(reportsText, 0, wx.ALL, 5)

        hSizer.Add(groupsSizer, 0, wx.ALL, 20)
        hSizer.Add(certsSizer, 0, wx.ALL, 20)
        hSizer.Add(arrowsSizer, 0, wx.ALL, 20)
        hSizer.Add(groupCertsSizer, 0, wx.ALL, 20)

        mainSizer.Add(hSizer, 0, wx.EXPAND|wx.ALL, 20)

        self.SetSizer(mainSizer)
        self.Show()

    def updateGroupCertsMap(self, certId):

        # Remember that the client data for this listbox is the group

        logger.debug( "updateGroupCertsMap: certId: %s" % certId)

        # now look through the local gcMap, and if this one is not there, add it
        
        for (key,value) in self.gcMap.items():
            logger.debug( ">>>>> key: %s, value: %s" % (key, value))

            if key == certId:
                return
            else:
                cert = dbUtils.findCertificationById(certId)
                logger.debug( "adding key: %s, value: %s to gcMap" % (key, value))
                self.gcMap[certId] = cert

        # clear the listbox
        self.groupCertsList.Clear()

        # fill in with our updated list
        
        for (key,value) in gcMap.items():
            logger.debug( ">>>>> key: %s, value: %s" % (key, value))
            self.groupCertsList.Append(value.getCertification(), key)

    def loadCertsList(self):
        cMap = dbUtils.getCertificationMap()
        
        for (key,value) in cMap.items():
            logger.debug( ">>>>> key: %s, value: %s" % (key, value))
            self.certsList.Append(value.getCertification(), key)

        self.certsList.SetSelection(0)

        
    def loadGroupCertsList(self, index):

        self.groupCertsList.Clear()

        # Remember that the client data for this listbox is the group

        logger.debug( ">>>> index: %s, client data: %s" % (index, self.groupsList.GetClientData(index)))
        
        gcMap = dbUtils.getCertificationMapByGroup(con, self.groupsList.GetClientData(index))

        for (key,value) in gcMap.items():
            logger.debug( ">>>>> key: %s, value: %s" % (key, value))
            self.groupCertsList.Append(value.getCertification(), key)

    def EvtComboBox(self, event):
        self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())

    def OnGroupsListSelected(self, event):
        logger.debug( "%s: OnGroupsListSelected button event" % self.name)
        self.groupCertsList.Clear()
        
        row = event.GetSelection()
        logger.debug( "Row: " + str(row))
        # TODO: fill in certsListBox with this group's certs
        index = event.GetSelection()
        data = self.groupsList.GetString(index)
        logger.debug( "Selected index: %s, Group: %s" % (index, data))
        obj = self.groupsList.GetClientData(index)
        logger.debug( "Group Id: %s" % obj)
        self.loadGroupCertsList(index)

    def OnCertsListSelected(self, event):
        logger.debug( "%s: OnCertsListSelected button event" % self.name)
        row = event.GetSelection()
        logger.debug( "Row: " + str(row))
        # TODO: fill in groupCertsListBox with the entries for the currently selected
        # group and cert
        index = event.GetSelection()
        data = self.certsList.GetString(index)
        logger.debug( "Selected Cert: %s, index: %s" % (data, self.certsList.GetSelection()))

    def OnGroupCertsListSelected(self, event):
        logger.debug( "%s: OnGroupCertsListSelected button event" % self.name)
        row = event.GetSelection()
        logger.debug( "Row: " + str(row))
        # TODO: mark selected cert for moving based on arrows 
        index = event.GetSelection()
        data = self.groupCertsList.GetString(index)
        logger.debug( "Selected index: %s, Group: %s" % (index, data))
        obj = self.groupCertsList.GetClientData(index)
        logger.debug( "Cert Id: %s" % obj)

    def OnRightClick(self,event):
        global certsUpdate

        logger.debug( "%s: OnRightClick button event" % self.name)
        groupIndex = self.groupsList.GetSelection()
        certIndex = self.certsList.GetSelection()
        groupId = self.groupsList.GetClientData(groupIndex)
        certId = self.certsList.GetClientData(certIndex)
        logger.debug( "Group index: %s, Cert index: %s" % (groupIndex, certIndex))
        logger.debug( "Group Id: %s, Cert Id: %s" %(groupId, certId))
        dbUtils.updateGroupCerts(con, groupId, certId)
        self.loadGroupCertsList(groupIndex)
        certsUpdate = True
        
    def OnAllRightClick(self,event):
        global certsUpdate
        logger.debug( "%s: OnAllRightClick button event" % self.name)
        groupIndex = self.groupsList.GetSelection()
        certIndex = self.certsList.GetSelection()
        groupId = self.groupsList.GetClientData(groupIndex)
        certId = self.certsList.GetClientData(certIndex)
        logger.debug( "Group index: %s, Cert index: %s" % (groupIndex, certIndex))
        logger.debug( "Group Id: %s, Cert Id: %s" %(groupId, certId))
        dbUtils.deleteAllGroupCerts(con, groupId)
        dbUtils.addAllGroupCerts(con, groupId)
        self.loadGroupCertsList(groupIndex)
        certsUpdate = True

    def OnLeftClick(self,event):
        global certsUpdate
        logger.debug( "%s: OnLeftClick button event" % self.name)
        certIndex = self.groupCertsList.GetSelection()
        certId = self.groupCertsList.GetClientData(certIndex)
        groupIndex = self.groupsList.GetSelection()
        groupId = self.groupsList.GetClientData(groupIndex)
        logger.debug( "Group index: %s, Cert index: %s" % (groupIndex, certIndex))
        logger.debug( "Group Id: %s, Cert Id: %s" %(groupId, certId))
        dbUtils.deleteFromGroupCerts(con, groupId, certId)
        self.loadGroupCertsList(groupIndex)
        certsUpdate = True

    def OnAllLeftClick(self,event):
        global certsUpdate
        logger.debug( "%s: OnAllLeftClick button event" % self.name)
        groupIndex = self.groupsList.GetSelection()
        certIndex = self.certsList.GetSelection()
        groupId = self.groupsList.GetClientData(groupIndex)
        certId = self.certsList.GetClientData(certIndex)
        logger.debug( "Group index: %s, Cert index: %s" % (groupIndex, certIndex))
        logger.debug( "Group Id: %s, Cert Id: %s" %(groupId, certId))
        dbUtils.deleteAllGroupCerts(con, groupId)
        self.loadGroupCertsList(groupIndex)
        certsUpdate = True


#---------------------------------------------------------------------------------------------------------
#
#     OnQuit
#
#---------------------------------------------------------------------------------------------------------

def OnQuit(self):
    logging.info( "Got QUIT menu event")
    con.commit()
    con.close()
    sys.exit(cterr.CT_SUCCESS)
    
#---------------------------------------------------------------------------------------------------------
#
#     OnAboutBox
#
#---------------------------------------------------------------------------------------------------------

def OnAboutBox(self):
        
        description = """certTracker is an advanced application for 
hospitals and nursing homes to manage certifications and training for
their employees.
"""

        licence = """certTracker is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

certTracker is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""


        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon('narrow_river.png', wx.BITMAP_TYPE_PNG))
        info.SetName('certTracker')
        info.SetVersion(getVersion())
        info.SetDescription(description)
        info.SetCopyright('(C) 2012 Mitchell McConnell')
        info.SetWebSite('http://www.mitchellmcconnell.net')
        info.SetLicence(licence)
        info.AddDeveloper('Mitchell McConnell')

        wx.AboutBox(info)

#---------------------------------------------------------------------------------------------------------
#
#     OnRegisterBox
#
#---------------------------------------------------------------------------------------------------------

def OnRegisterBox(self):

    dlg = RegisterDialog(frame, -1, "Register Dialog", size=(350, 200),
                         style=wx.DEFAULT_DIALOG_STYLE, 
                         useMetal=False,
                         )
    dlg.CenterOnScreen()

    # this does not return until the dialog is closed.
    val = dlg.ShowModal()
    
    if val == wx.ID_OK:
        key = dlg.getLicenseKey()
        
        print "You pressed OK, key value: %s" % key

        # get host name

        host = socket.gethostname()

        print "got host name: %s, licenseKey: %s" % (host, key)

        # testing

        try:
            parts = key.decode("hex").split(',')
        except TypeError, msg:
            msg = "Invalid key: %s" % key
            dial = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
            logger.error(msg)
            dial.ShowModal()
            dial.Destroy()
            return            

        print "parts: %s" % parts

        if parts[0] != host:
            msg = "Host name mismatch, key: %s, host: %s" % (parts[0], host)
            dial = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
            logger.error(msg)
            dial.ShowModal()
            dial.Destroy()
            return
        else:
            # check to see if we are already registered

            key = dbUtils.getKey(con)

            if key == None:
                dbUtils.insertKey(con, key)
            else:
                msg = "CertTracker is already registered with key: %s, contact support@narrowriver.com" % key
                dial = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
                logger.error(msg)
                dial.ShowModal()
                dial.Destroy()
                return
            
        # end testing
        
        SMTPHOST = "smtp.gmail.com"
        PORT = 587
        ACCOUNT = gmailuser
        PASSWORD = gmailPass
        
        SUBJECT = "Test email from Python"
        TO = "mitch@mitchellmcconnell.net"
        FROM = "mitchmcconnell1@gmail.com"
        text = "New registration from host: %s, key: %s" % (host, key)
        BODY = string.join((
            "From: %s" % FROM,
            "To: %s" % TO,
            "Subject: %s" % SUBJECT ,
            "",
            text
            ), "\r\n")

        server = smtplib.SMTP(SMTPHOST, PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(ACCOUNT, PASSWORD)
        server.sendmail(FROM, [TO], BODY)
        server.quit()
        
    else:
        print "You pressed Cancel"

    dlg.Destroy()
       
#----------------------------------------------------------------------------------
#
#                           g e t V e r s i o n
#
#----------------------------------------------------------------------------------
def getVersion():
    return certTracker_version

#----------------------------------------------------------------------------------
#
#                           O n P a g e C h a n g e d
#
#----------------------------------------------------------------------------------
def OnPageChanged(event):

    locus = "OnPageChanged"
    
    global certsUpdate
    global employeeUpdate
    global nb
    global debug
    global pagesList
    
    old = event.GetOldSelection()
    new = event.GetSelection()
    #sel = self.GetSelection()

    logger.debug( '%s: old:%d, new:%d, name: %s\n' % (locus, old, new, pagesList[new]))

    page = nb.GetPage(new)
    
    if certsUpdate == True:
        # update the certs list
        logger.debug( "%s: updating lists for page %s" % (locus, new))
            
        page.LoadCertsList() 
        page.LoadCertDatesList()
        page.LoadRenewDatesList()
        certsUpdate = False
    else:
        logger.debug( "WARNING: certsUpdate not set")

    if employeeUpdate == True:
        # update the employees list
        logger.debug( "%s: updating employee list for page %s" % (locus, new))
        page.LoadEmployeesList() 
        employeeUpdate = False
    else:
        logger.debug( "WARNING: employeeUpdate not set")

##    if new == 0:
##        # EmployeeCerts page... may need to update certs list if it was changed on the Certs page
##        
##        if certsUpdate == True:
##            # update the certs list in the groupcerts tab
##            logger.debug( "%s: updating certs list for page %s" % (locus, new)
##            page.loadCertsList() 
##            certsUpdate = False
##        else:
##            logger.debug( "WARNING: certsUpdate not set"
##            
##    elif new == 1:
##        pass
##    elif new == 2:
##        pass
##    elif new == 3:
##        pass
##    elif new == 4:
##        pass
##    else:
##        logger.debug( "ERROR: unexpected tab index %s" % new
##        sys.exit(3)
        
    event.Skip()


#----------------------------------------------------------------------------------
#
#                            m  a  i  n
#
#----------------------------------------------------------------------------------

#debug = 1

#dbUtils.setDebug(debug)

employeeUpdate = False
certsUpdate = False
groupsUpdate = False

dbPath = os.environ['CERTTRACKER_HOME']
dbName = os.environ['CERTTRACKER_DB']
dbFile = dbPath + '/' + dbName

# create the app
app = wx.App(False)
frame = wx.Frame(None, title="CertTracker", size=(APP_WIDTH, APP_HEIGHT))
nb = wx.Notebook(frame)

# do some sanity checking before trying to open the database

if not os.path.isfile(dbFile):
    msg = "Error opening database file: \n%s\n\nPlease check file name and path" % dbFile
    dial = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
    logger.warn(msg)
    dial.ShowModal()
    sys.exit(cterr.CT_DATABASE_NOT_FOUND)

logger.info("certTracker starting up, HOME: %s" % dbPath)
logger.info("certTracker starting up, dbFile: %s" % dbFile)

# logger testing

print "logging level: %s (%s)" % (logging.getLevelName(logger.getEffectiveLevel()), logger.getEffectiveLevel())

logger.debug("logger debug test")
logger.warn("logger warning test")
logger.error("logger error test")
logger.critical("logger critical test")

#dbUtils.initLogging()

# end testing

try:
    con = sqlite3.connect(dbFile)
    con.row_factory = sqlite3.Row
except sqlite3.Error, e:
    msg = "Error opening database: %s" % e
    dial = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
    logger.error(msg)
    dial.ShowModal()
    sys.exit(cterr.CT_DATABASE_CONNECT_ERROR)

# Do some license housekeeping 

key = dbUtils.getKey(con)
print "================ key: %s" % key

installDate = dbUtils.getInstallDate(con)
print "================ installDate: %s" % installDate

currDate = datetime.now()
print "currDate = %s" % currDate

if installDate == None:
    print "No installation date found"
    logger.warn("No installation date found")
else:
    print "Found installDate: %s" % installDate
    
    startdateobj = datetime.date(datetime.strptime(str(installDate),'%Y%m%d'))

    logger.debug("Found installation date: %s" % (startdateobj))

    # calculate the max date we will allow if there is no license key

    if key == None:
        max_date = startdateobj + timedelta(days=CT_MAX_UNLICENSED_DAYS)
        print "max_date: %s" % max_date
        if currDate.date() > max_date:
            msg = "Your trial period has expired, please contact support@narrowriver.com"
            logger.error(msg)
            dial = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            sys.exit(cterr.CT_LICENSE_EXPIRED)
        else:
            print "Trial period still valid"
    else:
        print "Found key: %s" % key

# get email info

emailAccount = dbUtils.getEmailAccount(con)
gmailUser = emailAccount[0]
gmailPass = emailAccount[1]

#print "got emailAccount info, user: %s, pass: %s" % (emailAccount[0], emailAccount[1])

# end housekeeping

dbUtils.loadEmployees(con)
dbUtils.loadGroups(con)
dbUtils.loadCertifications(con)

dbUtils.loadCertTracking(con)

# debugging stuff

# end debugging

nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, OnPageChanged)
 
# set up menus

menubar = wx.MenuBar()
fileMenu = wx.Menu()
fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
menubar.Append(fileMenu, '&File')
frame.Bind(wx.EVT_MENU, OnQuit, fitem)
frame.Bind(wx.EVT_CLOSE, OnQuit, fitem)

help = wx.Menu()
help.Append(CT_MENU_REGISTER, '&Register')
frame.Bind(wx.EVT_MENU, OnRegisterBox, id=CT_MENU_REGISTER)

help.Append(CT_MENU_ABOUT, '&About')
frame.Bind(wx.EVT_MENU, OnAboutBox, id=CT_MENU_ABOUT)
menubar.Append(help, '&Help')

frame.SetMenuBar(menubar)

nb.AddPage(EmployeeCertsPanel(nb), "Employee Certification Tracking")
nb.AddPage(CertificationsPanel(nb), "Certifications")
nb.AddPage(EmployeesPanel(nb), "Employees")
nb.AddPage(GroupsPanel(nb), "Groups")
nb.AddPage(GroupCertsPanel(nb), "Group Certs")
frame.Show()
app.MainLoop()
