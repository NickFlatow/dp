from dbConn import dbConn
from cbsd import CbsdModelExporter
from abc import ABC, abstractmethod
import consts
import requests


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

    def buildJsonRequest(self,typeOfCalling: str) -> dict:
        '''
        Builds and logs all json requests to SAS
        '''
        
        requestMessageType = str(typeOfCalling + "Request")
        
        req = {requestMessageType:[]}

        for cbsd in self.cbsdList:

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
    
    def SAS_response(self, cbsds: list, typeOfCalling: str) -> None:
        #check for errors
        #call individuial reponse methods

        for cbsd in self.cbsdList:
            
            cbsd.sasStage = self.getNextCalling(typeOfCalling)
            #update cbsd to next sasStage

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

    def reg(self):
       reg = SASRegistrationMethod(self.cbsdList)
       reg.buildJsonRequest()
       reg.contactSAS()
       reg.handleReply()

class SASMethod(ABC):
    
    @abstractmethod
    def buildJsonRequest():
        pass
    
    @abstractmethod
    def handleReply():
        pass

    def handleError():
        pass


    def contactSAS(self,method):
        ''''
        send json dict to sas
        '''
        try:
            self.sasResponse = requests.post("https://192.168.4.222:5001/v1.2/"+method, 
            # cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
            # verify=('googleCerts/ca.cert'),
            # json=request)
            # timeout=5
            cert=('certs/client.cert','certs/client.key'),
            verify=('certs/ca.cert'),
            json=self.req,
            timeout=5)
        
        except Exception as e:
            print(f"your connection has failed: {e}")
            return False


class SASRegistrationMethod(SASMethod):


    def __init__(self,cbsds: list):
            self.method = str(consts.REG + "Request")
            self.resposneMethod = str(consts.REG + "Response")
            self.cbsds = cbsds

    def buildJsonRequest(self):
        """
        produces json dict to send to SAS
        """
        self.req = {self.method:[]}
        
        for cbsd in self.cbsds:
            self.req[self.method].append(
                    {
                        "cbsdSerialNumber": cbsd.SN,
                        "fccId": cbsd.fccID,
                        "cbsdCategory": cbsd.cbsdCat,
                        "userId": cbsd.userID
                    }
                )
        print(json.dumps(self.req, indent = 4))


    def contactSAS(self):
        return super().contactSAS("registration")


    def handleReply(self):
        #TODO dump the log to the log file
        print(json.dumps(self.sasResponse.json(),indent=4))
        
        response = self.sasResponse.json()

        #iterate through the reposne for errors
        for i in range(len(self.cbsds)):
            if response['registrationResponse'][i]['response']['responseCode'] != 0:
                pass
                #add to errorList
            else:
                self.cbsds[i].setCbsdID(response['registrationResponse'][i]['cbsdId'])
                self.cbsds[i].setSasStage(consts.SPECTRUM)
        
        #if errorList
            #send to error class

    

if __name__ == '__main__':
    
    s = sasClient()
    #takes cbsd add it to list of cbsds to be registered
    s.create_cbsd('900F0C732A02')
    s.create_cbsd('DCE99461317E')

    # s.cbsdList[1].sasStage = consts.SPECTRUM
    registration_list = s.filter_sas_stage(consts.REG)
    s.reg()
    spectrum_list = s.filter_sas_stage(consts.SPECTRUM)
    # s.spec()



    for cbsd in s.cbsdList:
        print(cbsd.sasStage)

    # for f in registration_list:
    #     print(f.SN)

    #while True:
        #keep heartbeating all cbsds in hb stage
    # s.buildJsonRequest(s.cbsdList,consts.REG)




