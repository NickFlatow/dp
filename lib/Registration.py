import requests
import json
from lib import consts
from lib.cbsd import CbsdInfo
from lib.json import Json


class Registration():
    
    def __init__(self):
        self.json = Json()


    def registerCbsds(self,cbsds: list):

        #build Json request
        jsonRegRequest = self.json.buildJsonRequest(cbsds,consts.REG)

        #send request
        regResponse = self.sendRequest(jsonRegRequest,consts.REG)

        #process curl response
        #regResponse.status_code == 200:
            
            #process SAS resposne
            #self.processResponse(regResponse.json())
        
        self.processResponse(cbsds,regResponse)
    


        



    def processResponse(self,cbsds:list,response:dict):
        
        #bind json response to cbsd
        self.json.parseJsonResponse(cbsds,response,consts.REG)
        
        cbsd:CbsdInfo


        for cbsd in cbsds:

            if cbsd.reponseObj.responseCode == 0:
                #update cbsd state to Registered
                #pass back to sasClient for spectrum
                print("Ready for SIQ")
            elif cbsd.reponseObj.responseCode == 102:
                pass
            elif cbsd.reponseObj.responseCode == 103:
                pass
            elif cbsd.reponseObj.responseCode == 105:
                print("Ready for dereg")
            elif cbsd.reponseObj.responseCode == 106:
                pass



    def sendRequest(self,request:dict,method:str,retry=5):
        '''
        request: json request to pass to SAS server
        method:  method to pass json request to: registration,spectrum,grant,heartbeat
        '''


        return consts.REGPASS
        # timeout = 3
        # retries = 0
        # while retries < retry:
        #     try:
        #         # return requests.post(consts.SAS+method, 
        #         # cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
        #         # verify=('googleCerts/ca.cert'),
        #         # json=request)
        #         return requests.post("https://192.168.4.222:5001/v1.2/"+method, 
        #         cert=('certs/client.cert','certs/client.key'),
        #         verify=('certs/ca.cert'),
        #         json=request,
        #         timeout=5)
        #     except Exception as e:
        #         print({f"there has been some exception: {e}"})

            # except(ConnectTimeout,ConnectionError,SSLError,ReadTimeout,ConnectionRefusedError):
            #     retries = retries + 1
            #     self.checkCbsdsTransmitExpireTime()
            #     self.logger.info('connection to SAS failed')
            #     self.logger.info(f'Retry SAS in {timeout} seconds')
            #     time.sleep(timeout)
