class Certification(object):
    "Class to represent certification"
    id = 0
    debug = 0
    
    def __init__(self, id, certification, initial=None, renewal=None, active=True, notes=None):

        if self.debug == 1:
            print "Certification constructor, id: %s" % id
        
        if (id is None):
            Certification.id = Certification.id + 1
            self.id = Certification.id
        else:
            self.id = id

        self.certification = certification
        self.initial = initial
        self.renewal = renewal
        self.active = active
        self.notes = notes

        if self.debug == 1:
            print "created certification id: %s, cert: %s" % (str(self.id),certification)

    def getId(self):
        return self.id
    
    def setId(self, certId):
        self.id = certId
    
    def getCertification(self):
        return self.certification

    def setCertification(self, cert):
        self.certification = cert

    def getInitial(self):
        return self.initial

    def setInitial(self, initial):
        self.initial = initial

    def getRenewal(self):
        return self.renewal
    
    def setRenewal(self, renewal):
        self.renewal = renewal
    
    def isActive(self):
        return self.active

    def setActive(self, active):
        self.active = active

    def getNotes(self):
        return self.notes
    
    def setNotes(self, notes):
        self.notes = notes
        

