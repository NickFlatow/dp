from abc import ABC, abstractmethod
import requests
import json
import consts
import err

class SASMethod(ABC):
    
    @abstractmethod
    def buildJsonRequest():
        pass
    
    @abstractmethod
    def handleReply():
        pass

    def error(self):
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
            self.requestMessageType = str(consts.REG + "Request")
            self.resposneMethod = str(consts.REG + "Response")
            self.cbsds = cbsds
            self.err = []

    def buildJsonRequest(self):
        """
        produces json dict to send to SAS
        """
        self.req = {self.requestMessageType:[]}
        
        for cbsd in self.cbsds:
            self.req[self.requestMessageType].append(
                    {
                        "cbsdSerialNumber": cbsd.SN,
                        "fccId": cbsd.fccID,
                        "cbsdCategory": cbsd.cbsdCat,
                        "userId": cbsd.userID
                    }
                )
        
        print(json.dumps(self.req, indent = 4))

    def contactSAS(self):
        return super().contactSAS(consts.REG)

    def handleReply(self):
        #TODO dump the log to the log file
        print(json.dumps(self.sasResponse.json(),indent=4))
        
        response = self.sasResponse.json()

        #iterate through the reposne for errors
        for i in range(len(self.cbsds)):
            if response[self.resposneMethod][i]['response']['responseCode'] != 0:
                self.err.append(self.cbsds[i])
            else:
                self.cbsds[i].setCbsdID(response[self.resposneMethod][i]['cbsdId'])
                self.cbsds[i].setSasStage(consts.SPECTRUM)

        if self.err:
            err.error(self.err)

class SASSpectrumMethod(SASMethod):

    def __init__(self,cbsds: list):
            self.requestMessageType = str(consts.SPECTRUM + "Request")
            self.resposneMethod = str(consts.SPECTRUM + "Response")
            self.cbsds = cbsds
            self.err = []

    def buildJsonRequest(self):
        """
        produces json dict to send to SAS
        """
        self.req = {self.requestMessageType:[]}
        
        for cbsd in self.cbsds:
            self.req[self.requestMessageType].append(
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
        
        print(json.dumps(self.req, indent = 4))

    def contactSAS(self):
        return super().contactSAS(consts.SPECTRUM)

    def handleReply(self):
        #TODO dump the log to the log file
        print(json.dumps(self.sasResponse.json(),indent=4))
        
        response = self.sasResponse.json()

        #iterate through the reposne for errors
        for i in range(len(self.cbsds)):
            if response[self.resposneMethod][i]['response']['responseCode'] != 0:
                self.err.append(self.cbsds[i])
            else:
                self.cbsds[i].setCbsdID(response[self.resposneMethod][i]['cbsdId'])
                self.cbsds[i].setSasStage(consts.SPECTRUM)
                
        if self.err:
            self.error()