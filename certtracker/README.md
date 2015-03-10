certtracker
===========

This is a Python project that uses WxPython and sqlite to create an application to track employee certifications

CertTracker User Guide

Narrow River Software, Inc.


Table of Contents:

Introduction
Installing CertTracker
Running CertTracker
Technical Specifications


Introduction

CertTracker is a Windows application that is designed to help organizations such as, but not limited to, hospitals or nursing homes track employee certifications.

CertTracker’s design centers around employees, who belong to groups.  Each group has a list of certifications that its employees are expected or required to keep up to date.  

Examples include:

A hospital typically manages groups like Registered Nurse (RN), Patient Care Technician (PCT), Emergency Medical Technician (EMT), etc.    For RNs, the certifications might include Advanced Cardiac Life Support, Trauma, Gerontological Care, etc.

Law enforcement groups might include Street Patrol, SWAT, or Drug Enforcement.  Certifications might include Firearms Training, Street Interaction, Laser Training, Pepper Spray (OC) etc.

Nursing Homes are somewhat similar to hospitals, but in addition might have Kitchen workers, Gerontologists, etc.

Certifications, Employees, and Groups are “basic” tables that manage the raw data for the application.   the Employees table manages the group the employee belongs to, the employee’s start (hire) date, and the current status (“active” or “inactive”).  Groups likewise have an “active” or “inactive” status field.

The Certifications table manages three items:
Initial - the number of days after hire that proof of certification is required
Renewal - the number of days that the Certification lasts
A “Notes” field for miscellaneous data

An example might be helpful.  Say that nurse Jane Greer starts at Citywide Hospital on June 10, 2013.   Citywide requires that RNs (Jane’s group) have Advanced Cardiac Life Support (ACLS) within 90 days of start, and ACLS has a renewal of 365 days (in other words, it is good for one year).

If Jane already has a current ACLS certificate, she simply needs to present it and have it be recorded by CertTracker.  It’s date will become the base for the next renewal Jane will need, based on the “Renewal” field defined for ACLS in the Certifications table.

If Jane does not have a current ACLS certificate, she has 90 days (the “Initial” value for that certification) to get it.
CertTracker not only manages this information, but it provides a reporting mechanism to get a current list of all of Jane’s certifications, along with their dates and status.

This report can be run for just one employee (the “Certs Report”), or for all employess (the “All Employee Cert Report”).

Probably the most useful reporting feature of CertTracker is the “Certification Alerts” report.  This report can be generated with a date before which any employees have certifications that will be expiring.   Failure to keep certifications up to date may result in fines or other penalties.

There are two other tables that relate these data items to each other that make CertTracker useful.  The “Group Certs” table relates Groups to the Certifications that group members are required to have.    Certifications from the Certifications table may be added or removed from a group.

The final table is the Employee Certifications table, which tracks the certifications achieved by each employee for all certifications that belong to that employee’s group.    When a new employee starts, all of their existing certifications, along with their date, are entered into CertTracker.  Since CertTracker already “knows”, based on the employee’s group, which certifications the organization requires, there will already be useful data available just by entering the employee.

Obviously, CertTracker requires a regular data entry process to be useful.  New employees and their certifications and certification dates must be entered to be able to be seen on the Certification Alerts report.   Additionally, there needs to be a regular process to update all employees certifications as they are renewed.

Installation
CertTracker is delivered as a compressed (zipped) file with the format CertTracker_010205.zip, where “010205” represents the version number (“01” is the major version number, “02” is the release number, and “05” represents the current patch level).
Installing Python
CertTracker requires Python version 2.7.  Python is an interpreted language that CertTracker is written in.  The instructions on how to install it may be found at:

http://www.python.org/getit/

Here is another helpful link on installing Python:

http://docs.python-guide.org/en/latest/starting/install/win/

We recommend that you use the provided Windows installer package.  Be sure to choose the correct one based on whether or not you have a 32 or 64-bit processor.  You do not need to install a package that includes Python source

After installing Python, you need to add the path to the python.exe program to your system’s PATH environment variable.

Once you install Python and have set the PATH, you should test it to make sure it is installed and working correctly by starting a DOS cmd.exe shell and typing “python”.  You should get a prompt that will show the version of Python as follows:

C:\WINDOWS>echo off
$ python
Python 2.7.2 (default, Jun 12 2011, 15:08:59) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>

At the prompt, type “exit()” to exit Python.

Installing Sqlite3
CertTracker requires the Sqlite database package.  The download instructions may be found at:

http://www.sqlite.org/download.html

Be sure to go to the section entitled: Precompiled Binaries for Windows.  Sqlite3 installs as a single executable file, and may be placed anywhere in your system.  You must also add this path to your system’s PATH environment variable, however.   For convenience, you may wish to simply install it in the same directory you install CertTracker into (see below).

After sqlite3 is installed, you should check its installation by starting a DOS cmd.exe shell and typing “sqlite3”.  You should get a command prompt as follows:

$ sqlite3
SQLite version 3.7.13 2012-06-11 02:05:22
Enter ".help" for instructions
Enter SQL statements terminated with a ";"
sqlite>

To exit, type “.exit”.

Installing CertTracker
To install CertTracker, create a directory where you would like it installed.  We recommend C:\CertTracker.   Copy the zip file to the directory, and unzip it.

The files that are installed include:

Python source code (*.py)
Window batch files (*.bat)
Image file (narrow_river.png)

CertTracker does not ship with an empty database, to avoid any possibility of overwriting your data.  Instead, it ships with a simple utility that will generate an empty database for use in the initial installation only.  To run this, in the CertTracker directory, type

$ create_new_db.bat

This will utilize a Python script which will generate the Sqlite tables for an empty database named ‘certtracker’.  This is really “just” a Windows file that Sqlite manages like a database.

If Python and Sqlite are correctly installed, you should be ready to start using CertTracker.

Log Files
When CertTracker is running, it will create a log file in the installation directory.  This is used for debugging problems that might occur.  It will grow to only the maximum size specified in the runcert.bat script, then will copy the last log file to be certracker.log.bak.  You can control this size to be as big or little as you like, but if there is a problem, you must include this file with your email to support@certtracker.org.  

Reinstalling CertTracker after a version upgrade
Everything CertTracker uses is common, with the exception of your database data.  Therefore, you should be able to unzip a new CertTracker release into your existing CertTracker directory with no problems.  And when CertTracker shuts down normally, it makes a backup of your current database in the file certtracker.bak.

It is highly recommended that you make an off-machine or possibly off-site backup of this file (just as for all computer applications).  A simple way to do this is to send a copy of the database to yourself as an attachment to an email.  Most email providers, such as Google, Yahoo, etc., will effectively be storing your data (via their email) in a secure, off-site and backed-up up cloud environment.

Running CertTracker
To run CertTracker, from the installation directory, run the Windows batch file ‘runcert.bat’.  This will start the application.

CertTracker will install and run with a 45 day trial  license before a real license is required.  You may run and test the features before deciding if you wish to buy a one year license.  A one year license costs $10.

To buy a license, go to www.certtracker.org and click on the “Buy license” link on the home page.   Currently, CertTracker can only be purchased online using Paypal.  You may also send a check along with your email address to [TODO].  After the check has cleared, your license key will be emailed to you.

A CD with the software may also be purchased for $25.  Again, you must provide an email address for receiving the license key.

Once you have the license key, start CertTracker and select the “Help” menu followed by the “Register” command.  This will show a dialog box that will allow you to enter your new license key and your company or organization name.  The company name will be shown on the main window and on CertTracker reports.

Before CertTracker can be used fully, several preliminary steps must be taken to set up the data.  This involves defining lookup tables that are behind the employee certifications that are to be tracked.  These include the Groups, Certifications, Group Certifications, and Employees.  These all represent the data that CertTracker works with.

Groups represent the categories that employees must belong to.  For example, a hospital might have groups like: Registered Nurse, Patient Care Tech, EMT, etc.   A nursing home might also have Food Service Worker, Administrator, etc.   A law enforcement agency might have Patrol Officer, Community Policing Officer, School Resource Officer, SWAT, etc.

Certifications represent the all types of required training that are used by the organization.   Each certification defines two values: a) Initial - the number of days after the date of hire that the certification must be provided or taken; b) Renewal - the number of days from the time of the certification before renewal is required.   The reason that certifications are separated out from the groups is that some certifications might be required by multiple groups, e.g., Basic Life Support might be required for both Nurses and PCTs.

Group Certifications is where the certifications are associated with groups.   Think of it like a spreadsheet where one column is the group and the next column is the certification, but the same certification may be applied to multiple groups.

Employees represent your employees.  All employees are required to belong to one and only one group, and are entered along with their starting date of hire..   Based on their date of hire, their  group, and the group certifications, CertTracker knows which certifications each employee is required to have and can track them.

Once this data is defined, CertTracker is ready to be used to manage your employees certifications. 

To start CertTracker, run the supplied batch file ‘runcert.bat’.  This assumes you have completed the installation steps listed above, the main parts of which are making sure that Python 2.7 is installed, and that the initial database has been created.

Groups
To enter groups, select the “Groups” tab.  Press the “New” button and enter the group name.  Select whether the group is “Active” or “Inactive” via the drop-down list, and press the “Save” button.

The group will show up on the main list box.

To modify a group’s status, select the group in the main list box, and its data will be loaded into the editing fields.  Modify the status via the drop-down list, and press the “Save” button.  NOTE: the group name cannot be modified.  If you try and change it, it will enter a new group.  Also, groups cannot be deleted.
Certifications
To enter certifications, select the “Certifications” tab, and press the “New” button to position the cursor on the data entry fields.

Enter the certification name, initial days, renewal days, and any notes that you may find useful.
For example, the “Notes” field might contain information such as “Certificates on file”, or “Refresher course okay”.

The certification name, initial days, and renewal days are required.  If they are omitted, a dialog box will appear with the appropriate error.

Employees
To add employees, select the “Employees” tab and press the “New” button.  This will position the cursor in the new employees data text fields.

Enter the employee name.  You may enter it as First, Last, or Last, First, but you should be consistent to make it easier to find employees later.  Next, select the Group from the drop-down list for Groups.  Note that only groups which have been entered in the Groups tab will be visible here.  It is highly recommended that you enter all groups before entering employees.

Next, enter the employee’s start date via the calendar date chooser.  Select the drop-down arrow to the right of the date field to get the calendar chooser.   Finally, select the employee’s status, either “Active” or “Inactive”, and press the “Save” button.

To continue adding new employees, press the “New” button each time to reset the employee data fields.

To change employee data, simply select the employee in the main list box, and change the data fields as necessary, then press “Save”.  The changes should become visible in the employee list box.

Group Certifications
After all groups and certifications have been entered, the next step is to associate which certifications belong to which group.   Select the “Group Certs” tab, and you should see all of the groups and certifications you have entered.

Employee Certifications
The final step is to enter each employee’s certifications.  Select the “Employee Certification Tracking” tab, and you will see two listboxes on the left: Employee and Certifications.  As you click on an employee name, the Certifications listbox will change to show the certifications needed for that employee based on his/her group.   Clicking on one of the certifications for an employee will cause the employee’s list of certifications to be displayed in the Certification Date listbox, along with the current renewal date in the Renewal Date listbox.  Also, selecting a certification will show any notes associated with that certification in the textbox directly below the Certifications listbox.

To add a new date entry for the currently selected employee and certification, press the dropdown date chooser above the  “Add Cert Date” button, select the date, then press the “Add Cert Date” button.  The certification date will then be displayed in the Certification Date listbox, and the calculated renewal date will be displayed in the Renewal Date listbox.  The renewal date will be calculated as the certification date plus the number of days the certification is good for (see Certifications tab).

TODO: finish

Support
CertTracker is a “one man” operation.  Because of this, the price is minimal, and so is the support.  The good news is that there is no extra charge for support, all of which is done via email or online in the “Support” section of certtracker.org.  

Once a defect has been found and the corrrection made and tested, the new code will be posted to certtracker.org under the “Downloads” section.  Any licensed user may download and reinstall the new code and start using it with their existing database.

Requests for new features will be considered by sending inquiries to info@certtracker.org.

Security
CertTracker does not access the Internet, and the source code is available for all to see.  It only updates its own database file (‘certtracker’) and the log file in the working directory.

Technical Specifications

CertTracker was developed using Python version 2.7.2.  It uses a special package called wxPython to run in the Windows environment.

Python is a open-source program that is available for free at:

http://www.python.org/getit/

Make sure that version 2.7.x is downloaded.  CertTracker has not been tested with Python version 3.x.

CertTracker also uses SqlLite3 for its database.  SqlLite3 uses a plain Windows file for the database, and hence does not require any special installation or database management expertise.   

CertTracker has been tested on
Windows XP
Windows 7


Limitations
Employees must belong to a group, and cannot have certifications that are not part of their group.  

Employees may only belong to one group.

Employee names must be entered as “Last name, first name”


