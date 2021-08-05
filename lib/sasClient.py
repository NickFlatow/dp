# import json
# import consts
# import requests
# from dbConn import dbConn
# from cbsd import CbsdModelExporter
# from datetime import datetime,timedelta


import json 
import requests
import lib.consts as consts
from lib.dbConn import dbConn
from lib.cbsd import CbsdModelExporter, OneCA
from datetime import datetime,timedelta

class sasClientClass():
    '''
    One stop shop for all your SAS communication needs.\n
    You got cbsds needing specturm?\n
    We got connections :/
    '''
    def __init__(self):
        #list of cbsd objects
        self.cbsdList = []
        #list of cbsd objects currently heartbeating
        self.heartbeatList = []
        #keep list of cell that have errors
        self.err = []

        # except Exception as e:
        #     raise e

    def filter_sas_stage(self,sasStage):

        filtered = []

        for cbsd in self.cbsdList:
            if cbsd.sasStage == sasStage:
                filtered.append(cbsd)
        
        return filtered


    def filter_subsequent_heartbeat(self):

        filtered = []

        for cbsd in self.cbsdList:
            if cbsd.sasStage == consts.HEART and cbsd.subHeart == True:
                filtered.append(cbsd)

        return filtered

    def expired(self,SASexpireTime: str, isGrantTime = False) -> bool:
        '''
        Move to SAS client
        expireTime: str representing UTC expire time\n
        Time expired returns true
        else false
        '''
        if SASexpireTime == None:
            return False

        expireTime = datetime.strptime(SASexpireTime,"%Y-%m-%dT%H:%M:%SZ")

        #Renew grant five minues before it expires
        if isGrantTime:
            expireTime = expireTime - timedelta(seconds=300)
    
        if datetime.utcnow() >= expireTime:
            return True
        else: 
            return False


    def get_cbsd_database_row(self,SN: str) -> dict:
        '''Given a cbsd Serial Number the fucntion will return a dict with cbsd attributes'''
        conn = dbConn(consts.DB)
        cbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",SN)
        conn.dbClose()

        return cbsd

    def addOneCA(self, cbsd: OneCA):
        self.cbsdList.append(cbsd)
        
    def addCbsd(self,sqlCbsd: dict) -> None:

        self.cbsdList.append(CbsdModelExporter.getCbsd(sqlCbsd))

    def getCbsds(self,SNs: dict) -> list:

        cbsds = []

        for cbsd in self.cbsdList:
            if cbsd.SN in SNs['snDict']:
                cbsds.append(cbsd)

        return cbsds
            
    
    def contactSAS(self,request:dict,method:str):
        '''
        request: json request to pass to SAS server
        method:  method to pass json request to: registration,spectrum,grant,heartbeat
        '''
        # try:
        return requests.post("https://192.168.4.222:5001/v1.2/"+method, 
        # cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
        # verify=('googleCerts/ca.cert'),
        # json=request)
        # timeout=5
        cert=('certs/client.cert','certs/client.key'),
        verify=('certs/ca.cert'),
        json=request,
        timeout=5)
    
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
                        "operationState":cbsd.operationalState,
                        "grantRenew":False
                    }
                )
            elif typeOfCalling == consts.DEREG:
                req[requestMessageType].append(
                    {
                        "cbsdId":cbsd.cbsdID,
                    }
                )
            elif typeOfCalling == consts.REL:
                req[requestMessageType].append(
                    {
                        "cbsdId":cbsd.cbsdID,
                        "grantId":cbsd.grantID
                    }
                )


        print(json.dumps(req, indent=4))
        return req


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

        # channelSelected = cbsd.select_frequency(channels)
        channelSelected = True

        if channelSelected:
            cbsd.setSasStage(consts.GRANT)
        else: 
            self.err = [cbsd]
            # cbsd.setSasStage("error")

    def grantResposne(self,cbsd,sasResponse):
        #set grant expire time
        cbsd.setGrantExpireTime(sasResponse['grantExpireTime'])

        cbsd.grantID = sasResponse['grantId']
        #operationalState to granted
        cbsd.operationalState = 'GRANTED'

        #set sasStage to heartbeat
        cbsd.setSasStage(consts.HEART)

    def heartbeatResposne(self,cbsd,sasResponse):
        print(f"utcnow: {datetime.utcnow()}")
        cbsd.setTransmitExpireTime(sasResponse['transmitExpireTime'])

        if self.expired(sasResponse['transmitExpireTime']) and cbsd.adminState == 1:
            cbsd.operationalState = 'GRANTED'
            cbsd.powerOff()
        
        elif not self.expired(sasResponse['transmitExpireTime']) and cbsd.adminState == 0:
            cbsd.powerOn()
            cbsd.operationalState = 'AUTHORIZED'
            cbsd.subHeart = True

    def processSasResposne(self, sasResponse: dict, cbsds: list, typeOfCalling: str) -> None:

        responseMessageType = typeOfCalling + "Response"

        print(json.dumps(sasResponse,indent=4))

        #iterate through the response for errors
        for i in range(len(cbsds)):
            if sasResponse[responseMessageType][i]['response']['responseCode'] != 0:
                
                #TODO what to do about sasStage for cbsd
                self.err.append(cbsds[i])
                continue
            
            elif typeOfCalling == consts.REG:
                self.registrationResposne(cbsds[i],sasResponse[responseMessageType][i])
            
            elif typeOfCalling == consts.SPECTRUM:
                self.spectrumResposne(cbsds[i],sasResponse[responseMessageType][i]['availableChannel'])

            elif typeOfCalling == consts.GRANT:
                self.grantResposne(cbsds[i],sasResponse[responseMessageType][i])

            elif typeOfCalling == consts.HEART:
                self.heartbeatResposne(cbsds[i],sasResponse[responseMessageType][i])                

                
        if self.err:
            print("errror")


    def makeSASRequest(self,cbsds:list,typeOfCalling:str):
        
        req = self.buildJsonRequest(cbsds,typeOfCalling)
        
        sasReponse = self.contactSAS(req,typeOfCalling)
        
        if sasReponse.status_code == 200:
            self.processSasResposne(sasReponse.json(),cbsds,typeOfCalling)
        else:
            print(f"conenction error {sasReponse.status_code}")

    def cbsdInList(self,cbsdSN: str) -> bool:
        '''
        return True if cbsd is already in self.cbsdList
        '''
        for cbsd in self.cbsdList:
            if cbsd.SN == cbsdSN:
                return True
    
    def registerCbsds(self, cbsds: dict) -> None:
        
        for cbsd in cbsds:
            if cbsd not in self.cbsdList:
                self.addCbsd(cbsd)

        registration_list = self.filter_sas_stage(consts.REG)
        if registration_list:
            self.makeSASRequest(registration_list,consts.REG)

        spectrum_list = self.filter_sas_stage(consts.SPECTRUM)
        if spectrum_list:
            self.makeSASRequest(spectrum_list,consts.SPECTRUM)

        grant_list = self.filter_sas_stage(consts.GRANT)
        if grant_list:
            self.makeSASRequest(grant_list,consts.GRANT)

        heartbeat_list = self.filter_sas_stage(consts.HEART)
        if heartbeat_list:
            self.makeSASRequest(heartbeat_list,consts.HEART)

    def deregisterCbsd(self,SNs: dict) -> None:
        '''
        
        '''
        cbsds = self.getCbsds(SNs)
        relinquish = []

        for cbsd in cbsds:
            if cbsd.grantID != None:
                cbsd.relinquish()
                relinquish.append(cbsd)
            cbsd.deregister()

        if relinquish:
            self.makeSASRequest(relinquish,consts.REL)
        self.makeSASRequest(cbsds,consts.DEREG)
            
    def heartbeat(self) -> None:

        #filter for authorized heartbeats
        heartbeat_list = self.filter_subsequent_heartbeat()
        if heartbeat_list:
            self.makeSASRequest(heartbeat_list,consts.HEART)


if __name__ == '__main__':

    s = sasClientClass()
    #takes cbsd add it to list of cbsds to be registered

    conn = dbConn(consts.DB)
    cbsd = conn.select("SELECT * FROM dp_device_info WHERE fccID = %s",'2AQ68T99B226')
    conn.dbClose()

    # s.addCbsd(cbsd[0])
    s.registerCbsds(cbsd)
    # s.create_cbsd('DCE99461317E')

    # s.cbsdList[1].sasStage = consts.SPECTRUM


    registration_list = s.filter_sas_stage(consts.REG)
    if registration_list:
        s.makeSASRequest(registration_list,consts.REG)

    spectrum_list = s.filter_sas_stage(consts.SPECTRUM)
    if spectrum_list:
        s.makeSASRequest(spectrum_list,consts.SPECTRUM)

    grant_list = s.filter_sas_stage(consts.GRANT)
    if grant_list:
        s.makeSASRequest(grant_list,consts.GRANT)

    heartbeat_list = s.filter_sas_stage(consts.HEART)
    if heartbeat_list:
        s.makeSASRequest(heartbeat_list,consts.HEART)


        # for f in registration_list:
    #     print(f.SN)

    #while True:
        #keep heartbeating all cbsds in hb stage
    # s.buildJsonRequest(s.cbsdList,consts.REG)




