import time
import datetime

class ActiveCall(object):

    createdDate = None
    reportNum = ""
    occurredAt = ""
    problem = ""
    address1 = ""
    locality = ""
    unit = ""
    debug = False
    entry = 0

    def __init__(self, rpt=None, occur=None, prob=None, addr1=None, locality=None, unit=None):
        if self.debug:
            print "(Call) enter, rpt: ",rpt

        self.createdDate = datetime.datetime.now()
        self.reportNum = rpt
        self.occurredAt = occur
        self.problem = prob
        self.address1 = addr1
        self.locality = locality
        self.unit = unit


    def __str__(self):
        return str(self.entry) + " - " + self.reportNum + " (" + self.locality + ") " + self.occurredAt + " : " + self.problem
