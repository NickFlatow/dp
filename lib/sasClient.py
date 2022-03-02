from lib.cbsd import CbsdInfo, CbsdModelExporter
from lib.Registration import Registration


class SasClient():
    def __init__(self):
        self.reg = Registration()

    def startRegistration(self, cbsdSerialNumbers: list):
        '''proccess post request to register node from user'''

        cbsds = []

        for sn in cbsdSerialNumbers:
            cbsds.append(CbsdModelExporter.getCbsd( {"SN":sn,"fccID":"2QCAT299166","cbsdCategory":"B","userID":"Foxconn","hclass":"FAP_FC4064Q1CA"} ) )

        self.reg.registerCbsds(cbsds)

        #verify cbsds are not alreday in registed or granted state

        #if 5GC does not use database/ dp will use database to store persistant cbsd info
        #will node have cbsdState stored in it's database?... how accessible is this?

        #dbCbds = Select * FROM database where SN = {cbsdSerialNumbers}

        #for cbsd in db:
            #if cbsd.state == NULL:
                #create cbsd per modelType
                #add to cbsdRegList
            #else: 
                #nothing
        
              

