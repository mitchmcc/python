class Employee(object):
    "Class to represent employee"
    employeeId = 0
    debug = 0
    
    def __init__(self, id, firstName, lastName, active, startDate, groupId):

        if (id is None):
            Employee.employeeId = Employee.employeeId + 1
            self.employeeId = Employee.employeeId
        else:
            self.employeeId = id
       
        self.firstName = firstName
        self.lastName = lastName
        self.active = active
        self.startDate = startDate
        self.groupId = groupId

        if self.debug == 1:
            print "created employee " + str(self.employeeId) + " " + firstName + ", " + lastName
            print "    startDate: %s, groupId: %s" % (str(self.startDate), self.groupId)

    def getId(self):
        return self.employeeId
    
    def setId(self, id):
        self.employeeId = id
    
    def getGroupId(self):
        return self.groupId
    
    def setGroupId(self, groupId):
        self.groupId = groupId
    
    def getFirstName(self):
        return self.firstName

    def getLastName(self):
        return self.lastName

    def getFullName(self):
        return self.firstName + ' ' + self.lastName

    def getStartDate(self):
        return self.startDate
    
    def setStartDate(self, startDate):
        self.startDate = startDate
    
    def setFirstName(self, firstName):
        self.firstName = firstName

    def setLastName(self, lastName):
        self.lastName = lastName

    def isActive(self):
        return self.active

    def setActive(self, active):
        self.active = active

    def setDebug(self, value):
        debug = value

    def getDebug(self):
        return value
    
