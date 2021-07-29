import consts
import requests
import time
from dbConn import dbConn
from datetime import datetime
from requests.auth import HTTPDigestAuth



class CbsdInfo:
    '''
    Contains persistant cbsd information userID, fccID, antennaGain ..... 
    '''

    cbsdID: str
    lowFrequency: int
    highFrequency: int
    # attributes = ['userID','fccID','sasStage','TxPower','EARFCN','antennaGain','IPAddress','connreqUname','connreqPass','connreqURL']

    def __init__(self,sqlCbsd):        
        self.userID = sqlCbsd['userID']
        self.fccID = sqlCbsd['fccID']
        self.sasStage = sqlCbsd['sasStage']
        self.txPower = sqlCbsd['TxPower']
        self.earfcn = sqlCbsd['EARFCN']
        self.antennaGain = sqlCbsd['antennaGain']
        
        
        self.adminState = 0


        #move this bit to CBSD
        self.ipAddress = sqlCbsd['IPAddress']
        self.connreqUname = sqlCbsd['connreqUname']
        self.connreqPass = sqlCbsd['connreqPass']
        self.connreqURL = sqlCbsd['connreqURL']

    def set_cbsdID(self,cbsdID):
        self.cbsdID = cbsdID

    def compute_maxEirp(self):

        return self.txPower + self.antennaGain


    #set txPower

    #set lowFreq

    #set highFreq

class Cbsd:
    '''
    Contains information specific to cbsd Actions such as ipaddress, power earfcn connection request URL
    As well as the dynamic info that acommanies it such as Power, earfcn etc.
    '''

    def __init__(self, SN, info):
        self.SN = SN
        self.info = info

    def setParamterValue(self,parameterValueList):
        '''
        sets new paramter value on cell
        updates cbsd class
        '''
        #connect to database
        conn = dbConn("ACS_V1_1")

        #add perodicInform to parameterValueList(sets new database values immediately after setting)
        parameterValueList.append(consts.PERIODIC_ONE)
        
        print(f"connected to IP: {self.info.ipAddress}")

        for i in range(len(parameterValueList)):
            
            
            #admin state if off
            if parameterValueList[i]['data_path'] == consts.ADMIN_STATE: 
                if parameterValueList[i]['data_value'] == 'false':
                    # logging.info("Turn RF OFF for %s",cbsd['SN'])
                    conn.update("UPDATE dp_device_info SET AdminState = %s WHERE SN = %s",(0,self.SN))
                    self.info.adminState = 0
                else:
                    # logging.info("Turn on RF for %s",cbsd['SN'])
                    conn.update("UPDATE dp_device_info SET AdminState = %s WHERE SN = %s",(1,self.SN))
                    self.info.adminState = 1

            #add parameterValues datamodel, type and value to spv database table
            conn.update('INSERT INTO fems_spv(`SN`, `spv_index`,`dbpath`, `setValueType`, `setValue`) VALUES(%s,%s,%s,%s,%s)',(self.SN,i,parameterValueList[i]['data_path'],parameterValueList[i]['data_type'],parameterValueList[i]['data_value']))

            #place action in apt_action_queue
            self.cbsdAction(self.SN,'Set Parameter Value',str(datetime.now()))
            
            #Make connection request
            response = requests.get(self.info.connreqURL, auth= HTTPDigestAuth(self.info.connreqUname,self.info.connreqPass))

            #if connection request returns 200
            if response.status_code == 200:
                #Wait for conenction request to complete
                settingParameters = True
                while settingParameters:
                    # logging.info(f"Setting Parameters for {cbsd['SN']}")
                    database = conn.select("SELECT * FROM apt_action_queue WHERE SN = %s",self.SN)
                    
                    if database == (): 
                        # logging.info(f"Paramters set successfully for {cbsd['SN']}")
                        settingParameters = False
                    else:
                        time.sleep(1)
                        # endTime = datetime.now()
                        # logging.info(f"end time in loop: {endTime}")
            else:
                # remove action from action queue
                conn.update("DELETE FROM apt_action_queue WHERE SN = 'DCE994613163'")

                #and then retry


            #if successful update class values

    def cbsdAction(self,cbsdSN,action,time):
        #check note field for EXEC
        # logging.critical("Triggering CBSD action")
        conn = dbConn("ACS_V1_1")
        sql_action = "INSERT INTO apt_action_queue (SN,Action,ScheduleTime) values(\'"+cbsdSN+"\',\'"+action+"\',\'"+time+"\')"
        # logging.critical(cbsdSN + " : SQL cmd " + sql_action)
        conn.update(sql_action)
        conn.dbClose()


if __name__ == '__main__':
    conn = dbConn("ACS_V1_1")
    sqlCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",'900F0C732A02')
    a = CbsdInfo(sqlCbsd[0])
    b = Cbsd('900F0C732A02',a)
    # b.setParamterValue([consts.ADMIN_POWER_ON])
    b.info.sasStage = 'test'


    print('test')
