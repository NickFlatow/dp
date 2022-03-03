from concurrent.futures import ThreadPoolExecutor
from re import A
from lib import cbsd
from lib.cbsd import CbsdInfo, CbsdModelExporter
from lib.Registration import Registration
from lib.GrantManger import GrantManger
from lib.types import cbsdAction


class SasClient():
    def __init__(self):
        self.reg = Registration()
        self.gm = GrantManger()
        self.gm.start()
        # self.StartGmPollingThread()
        

    def sasClientRequestStrategy(self, cbsdSerialNumbers: list):
        '''proccess post request to register node from user'''

        # cbsds = []

        # for sn in cbsdSerialNumbers:
            # cbsds.append(CbsdModelExporter.getCbsd( {"SN":sn,"fccID":"2QCAT299166","cbsdCategory":"B","userID":"Foxconn","hclass":"FAP_FC4064Q1CA"} ) )

        # self.reg.registerCbsds(cbsds)
        # with ThreadPoolExecutor(max_workers=1) as executor:
            # executor.submit(self.reg.registerCbsds,cbsds)

        #change to strategy.run()
        
        action = self.reg.Run(cbsdSerialNumbers)

        if action == cbsdAction.STARTGRANT:
            self.gm.actionQueue = action


        # self.gm.kill = True
        
        


        #verify cbsds are not alreday in registed or granted state

        #dbCbds = Select * FROM database where SN = {cbsdSerialNumbers}

        #for cbsd in db:
            #if cbsd.state == NULL:
                #create cbsd per modelType
                #add to cbsdRegList
            #else: 
                #nothing
        
        
              

