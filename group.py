class Group(object):
    "Class to represent group"
    id = 0
    debug = 0
    
    def __init__(self, id, name, active):

        if (id is None):
            Group.id = Group.id + 1
            self.id = Group.id
        else:
            self.id = id

        self.name = name
        self.active = active

        if self.debug == 1:    
            print "created group " + name

    def getId(self):
        return self.id
    
    def setId(self, id):
        self.id = id

    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name

    def isActive(self):
        return self.active

    def setActive(self, active):
        self.active = active
        

