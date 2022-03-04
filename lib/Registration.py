import requests
import time
from lib.dbConn import dbConn
from lib import consts
from lib.log import logger
from lib.cbsd import CbsdInfo,CbsdModelExporter
from lib.json import Json
from lib.GrantManger import GrantManger
from lib.types import cbsdAction,MessageTypes as m
import threading

class Registration():
    
    def __init__(self):
        self.json = Json()
        self.logger = logger()
        self.cbsds = []
        self.gm = GrantManger()


    def __del__(self):
        self.cbsds.clear()
        
    def Run(self,cbsdSerialNumbers: list):

        conn = dbConn('ACS_V1_1')
        sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(cbsdSerialNumbers)))
        sqlCbsds = conn.select(sql,cbsdSerialNumbers)
        conn.dbClose()

        for cbsd in sqlCbsds:
            if cbsd['SN'] not in self.cbsds:
                self.cbsds.append(CbsdModelExporter.getCbsd(cbsd))

        #build Json request
        # jsonRegRequest = self.json.buildJsonRequest(cbsds,consts.REG)
        jsonRegRequest = self.json.buildJsonRequest(self.cbsds,m.REGISTRATION.value)

        #send request
        regResponse = self.sendRequest(jsonRegRequest,consts.REG)

        #process curl response
        # if regResponse.status_code == 200:
            #process SAS resposne
            # self.processResponse(cbsds,regResponse.json())
        # return self.processResponse(regResponse)
        if self.processResponse(regResponse) == cbsdAction.STARTGRANT:
            self.gm.heartbeat()

        for thread in threading.enumerate(): 
            print(f"Registration thread loop -- {thread.name}")


        self.cbsds.clear()
        
    
    #return action
    def processResponse(self,response:dict) -> cbsdAction:
        nextAction:cbsdAction
        
        #bind json response to cbsd
        self.json.parseJsonResponse(self.cbsds,response,consts.REG)
        
        cbsd:CbsdInfo
        for cbsd in self.cbsds:
            if cbsd.reponseObj.responseCode == 0:
                #cbsd.updateRegistration
                    #update cbsdId in cbsd table
                    #update cbsdState to Registred

                    nextAction = cbsdAction.STARTGRANT
            elif cbsd.reponseObj.responseCode == 102:
                pass
            elif cbsd.reponseObj.responseCode == 103:
                pass
            elif cbsd.reponseObj.responseCode == 105:
                print("Ready for dereg")
                time.sleep(1)
                print("Ready for dereg")
            elif cbsd.reponseObj.responseCode == 106:
                pass

        return nextAction



    #change to class
    def sendRequest(self,request:dict,method:str,retry=5):
        '''
        request: json request to pass to SAS server
        method:  method to pass json request to: registration,spectrum,grant,heartbeat
        '''
        # retries = 0
        # while retries < retry:
        return consts.REGPASS
        # while True:
        #     try:
        #         # return requests.post(consts.SAS+method, 
        #         # cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
        #         # verify=('googleCerts/ca.cert'),
        #         # json=request)
        #         return requests.post("https://192.168.4.25:5000/v1.2/"+method, 
        #         cert=('certs/client.cert','certs/client.key'),
        #         verify=('certs/ca.cert'),
        #         json=request,
        #         timeout=5)
        #     except requests.exceptions.RequestException as e:
        #         # retries += 1
        #         self.logger.info({f"there has been some exception: {e}"})
        #         time.sleep(consts.REQ_TIMEOUT)
                


            # except(ConnectTimeout,ConnectionError,SSLError,ReadTimeout,ConnectionRefusedError):
            #     retries = retries + 1
            #     self.checkCbsdsTransmitExpireTime()
            #     self.logger.info('connection to SAS failed')
            #     self.logger.info(f'Retry SAS in {timeout} seconds')
            #     time.sleep(timeout)
