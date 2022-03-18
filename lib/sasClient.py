from concurrent.futures import ThreadPoolExecutor
from re import A
from lib import cbsd
from lib.cbsd import CbsdInfo, CbsdModelExporter
from lib.Registration import Registration
from lib.GrantManger import GrantManger
from lib.types import cbsdAction
import threading


class SasClient():
    def __init__(self):
        self.reg = Registration()
        

    def sasClientRequestStrategy(self, cbsdSerialNumbers: list,strategyClass):
        '''proccess post request to register,relinquish or deregister node'''

        # cbsds = []

        # for sn in cbsdSerialNumbers:
            # cbsds.append(CbsdModelExporter.getCbsd( {"SN":sn,"fccID":"2QCAT299166","cbsdCategory":"B","userID":"Foxconn","hclass":"FAP_FC4064Q1CA"} ) )

        # self.reg.registerCbsds(cbsds)
        # with ThreadPoolExecutor(max_workers=1) as executor:
            # executor.submit(self.reg.registerCbsds,cbsds)

        #change to strategy.run()
        self.reg.Run(cbsdSerialNumbers)
        # strategyClass.Run(cbsdSerialNumbers)
        # action = self.reg.Run(cbsdSerialNumbers)
        print('waiting for new request')

        for thread in threading.enumerate(): 
            print(f"sasClient thread loop -- {thread.name}")


        # self.gm.poll()
        # print("continue")
        # if action == cbsdAction.STARTGRANT:
        #     self.gm.actionQueue = action

    
