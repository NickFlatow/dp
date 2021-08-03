from dbConn import dbConn
from cbsd import CbsdModelExporter
from sasMethods import SASRegistrationMethod
import consts
import requests

import threading


import json


class sasClient():
    '''
    One stop shop for all your SAS communication needs.\n
    You got cbsds needing specturm?\n
    We got connections :|
    '''
    def __init__(self):
        #list of cbsd objects
        self.cbsdList = []
        #list of cbsd objects currently heartbeating
        self.heartbeatList = []


    def contactSAS(self,request:dict,method:str):
        '''
        request: json request to pass to SAS server
        method:  method to pass json request to: registration,spectrum,grant,heartbeat
        '''
        try:
            return requests.post("https://192.168.4.222:5001/v1.2/"+method, 
            # cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
            # verify=('googleCerts/ca.cert'),
            # json=request)
            # timeout=5

            cert=('certs/client.cert','certs/client.key'),
            verify=('certs/ca.cert'),
            json=request,
            timeout=5)
        
        except Exception as e:
            print(f"your connection has failed: {e}")
            return False

    def get_cbsd_database_row(self,SN: str) -> dict:
        '''Given a cbsd Serial Number the fucntion will return a dict with cbsd attributes'''
        conn = dbConn(consts.DB)
        cbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",SN)
        conn.dbClose()

        return cbsd

    def create_cbsd(self,SN):

        sqlCbsd = self.get_cbsd_database_row(SN)
        a = CbsdModelExporter.getCbsd(sqlCbsd[0])
        
        # a.userID
        self.cbsdList.append(CbsdModelExporter.getCbsd(sqlCbsd[0]))

    def buildJsonRequest(self,cbsds: list,typeOfCalling: str) -> dict:
        '''
        Builds and logs all json requests to SAS
        '''
        
        requestMessageType = str(typeOfCalling + "Request")
        
        req = {requestMessageType:[]}

        for cbsd in cbsds:

            if typeOfCalling == consts.REG:
                req[requestMessageType].append(
                    {
                        "cbsdSerialNumber": cbsd.SN,
                        "fccId": cbsd.fccID,
                        "cbsdCategory": cbsd.cbsdCat,
                        "userId": cbsd.userID
                    }
                )

            elif typeOfCalling == consts.SPECTRUM:
                req[requestMessageType].append(
                    { 
                        "cbsdId":cbsd.cbsdID,
                        "inquiredSpectrum":[
                            {
                                "highFrequency":consts.HIGH_FREQUENCY,
                                "lowFrequency":consts.LOW_FREQUENCY
                            }
                        ]
                    }
                )

            elif typeOfCalling == consts.GRANT:
                req[requestMessageType].append(
                        { 
                            "cbsdId":cbsd.cbsdID,
                            "operationParam":{
                                "maxEirp":cbsd.maxEirp,
                                "operationFrequencyRange":{
                                    "lowFrequency":cbsd.lowFrequency * 1000000,
                                    "highFrequency":cbsd.highFrequency * 1000000
                                }
                            }
                        }
                    )

            elif typeOfCalling == consts.HEART:
                req[requestMessageType].append(
                    {
                        "cbsdId":cbsd.cbsdID,
                        "grantId":cbsd.grantID,
                        "operationState":'GRANTED',
                        "grantRenew":False
                    }
                )
        print(json.dumps(req, indent=4))
        return req

    def getNextCalling(typeOfCalling):
        if typeOfCalling == consts.REG:
            return consts.SPECTRUM
        if typeOfCalling == consts.SPECTRUM:
            return consts.GRANT
        if typeOfCalling == consts.GRANT:
            return consts.HEART
        else:
            return False



    def SAS_request(self,typeOfCalling: str) -> dict:
        '''
        passses json to SAS with typeOfCalling method 
        returns the resposne from SAS
        '''
        #filter cbsdList where cbsd.sasStage
         
        #build json
        sasRequest = self.buildJsonRequest(typeOfCalling)
        #contactSAS
        response = self.contactSAS(sasRequest,typeOfCalling)

        if response.status_code == 200:
            return 
        print(response)
        
        # return sasResponse

    def registrationResposne(self,cbsd,sasResponse):
        
        cbsd.setCbsdID(sasResponse['cbsdId'])
        cbsd.setSasStage(consts.SPECTRUM)

    def spectrumResposne(self,cbsd,channels):
        pass

    
    def processSasResposne(self, sasResponse: dict, cbsds: list, typeOfCalling: str) -> None:

        responseMessageType = typeOfCalling + "Response"
        err = []

        print(json.dumps(sasResponse,indent=4))

        #iterate through the reposne for errors
        for i in range(len(cbsds)):
            if sasResponse[responseMessageType][i]['response']['responseCode'] != 0:
                #TODO what to do about sasStage for cbsd
                err.append(cbsds[i])
                continue
            
            elif typeOfCalling == consts.REG:
                self.registrationResposne(cbsds[i],sasResponse[responseMessageType][i])
            
            elif typeOfCalling == consts.SPECTRUM:
                self.spectrumResposne(cbsds[i],sasResponse[responseMessageType][i]['availableChannel'])

                
        if err:
            print("errror")

    def registration_response(self):
        pass
        #update all cbsds to have sasStage = conts.SPECTRUM

    def deregistration_request(self):
        pass
        #cbsd.deregister()
        #filter list where cbsd.sasStage = consts.DEREG
        #buildJsonrequest()
    

    def registration(self) -> None:
        '''Runs a list of cbsds through the SAS registratrion process, stops at grant; then adds list of cbsds to hearbeat list'''

        #if cbsd is not in cbsdList or heartbeatList:
            #create cbsd
        #else:
            #print to log/FeMS already registered or heartbeating

        typeOfCallings = [consts.REG,consts.SPECTRUM,consts.GRANT,consts.HEART]
        
        for typeOfCalling in typeOfCallings:
            sasResponse = self.SAS_request(typeOfCalling)
            
            # if sasResponse.status_code == 200:
            #     self.SAS_response(sasResponse)

    def filter_sas_stage(self,sasStage):
        
        filtered = []

        for cbsd in self.cbsdList:
            if cbsd.sasStage == sasStage:
                filtered.append(cbsd)
        
        return filtered

    def makeSASRequest(self,cbsds:list,typeOfCalling:str):
        req = self.buildJsonRequest(cbsds,typeOfCalling)
        sasReponse = self.contactSAS(req,typeOfCalling)
        self.processSasResposne(sasReponse.json(),cbsds,typeOfCalling)
    #    reg = SASRegistrationMethod(self.cbsdList)
    #    reg.buildJsonRequest()
    #    reg.contactSAS()
    #    reg.handleReply()


if __name__ == '__main__':
    
    s = sasClient()
    #takes cbsd add it to list of cbsds to be registered
    s.create_cbsd('900F0C732A02')
    s.create_cbsd('DCE99461317E')

    # s.cbsdList[1].sasStage = consts.SPECTRUM
    registration_list = s.filter_sas_stage(consts.REG)
    s.makeSASRequest(registration_list,consts.REG)
    spectrum_list = s.filter_sas_stage(consts.SPECTRUM)
    s.makeSASRequest(spectrum_list,consts.SPECTRUM)



    for cbsd in s.cbsdList:
        print(cbsd.sasStage)


    # while True:
        heartbeat_list = s.filter_sas_stage(consts.HEART)
    # for f in registration_list:
    #     print(f.SN)

    #while True:
        #keep heartbeating all cbsds in hb stage
    # s.buildJsonRequest(s.cbsdList,consts.REG)




