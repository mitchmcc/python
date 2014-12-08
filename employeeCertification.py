class EmployeeCertification(object):
    "Class to represent employee"
    employeeId = 0
    certId = 0
    id = 0
    debug = 0
    
    def __init__(self, ecId, employeeId, certId, certDate, renewalDate):

        if (id is None):
            EmployeeCertification.id = EmployeeCertification.id + 1
            self.id = EmployeeCertification.id
        else:
            self.id = ecId

        self.employeeId = employeeId
        self.certId = certId
        self.certDate = certDate
        self.renewalDate = renewalDate

        if self.debug == 1:
            print "created employee cert, id: %s, emplId: %s, certId: %s, certDate: %s, renewalDate: %s" % \
               (self.id, str(self.employeeId),self.certId, self.certDate, self.renewalDate)

    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id
        
    def getEmployeeId(self):
        return self.employeeId
    
    def setEmployeeId(self, id):
        self.employeeId = id
    
    def getCertId(self):
        return self.certId
    
    def setCertId(self, certId):
        self.certId = certId
    
    def getCertDate(self):
        return self.certDate

    def setCertDate(self, certDate):
        self.certDate = certDate
        
    def getRenewalDate(self):
        return self.renewalDate 

    def setRenewalDate(self):
        return self.renewalDate
    
    def setDebug(self, value):
        debug = value

    def getDebug(self):
        return debug
    
