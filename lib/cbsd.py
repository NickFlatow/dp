import consts
import requests
import time
from abc import ABC, abstractmethod
from dbConn import dbConn
from datetime import datetime
from requests.auth import HTTPDigestAuth

# class CbsdInfo:
#     '''
#     Contains persistant cbsd information userID, fccID, antennaGain ..... 
#     '''

#     cbsdID: str
#     lowFrequency: int
#     highFrequency: int
#     # attributes = ['userID','fccID','sasStage','TxPower','EARFCN','antennaGain','IPAddress','connreqUname','connreqPass','connreqURL']

#     def __init__(self,sqlCbsd):        
#         self.userID = sqlCbsd['userID']
#         self.fccID = sqlCbsd['fccID']
#         self.sasStage = sqlCbsd['sasStage']
#         self.txPower = sqlCbsd['TxPower']
#         self.earfcn = sqlCbsd['EARFCN']
#         self.antennaGain = sqlCbsd['antennaGain']
#         self.adminState = 0
#         self.ipAddress = sqlCbsd['IPAddress']
#         self.connreqUname = sqlCbsd['connreqUname']
#         self.connreqPass = sqlCbsd['connreqPass']
#         self.connreqURL = sqlCbsd['connreqURL']

#     def set_cbsdID(self,cbsdID):
#         self.cbsdID = cbsdID

#     def compute_maxEirp(self):
#          return self.txPower + self.antennaGain


    #set txPower

    #set lowFreq

    #set highFreq

class CbsdInfo(ABC):
    '''
    Contains information specific to CBSD and cbsdActions such as ipaddress, power, earfcn, connection request URL...etc
    Contains methods whcich preform action on CBSD such as setParamterValues
    CBSD class assumes adminState will start as off. As it is not allowed to be on without SAS permission
    '''

    def __init__(self, sqlCbsd):
        self.userID =            sqlCbsd['userID']
        self.fccID =             sqlCbsd['fccID']
        self.SN =                sqlCbsd['SN']
        self.cbsdCat =           sqlCbsd['cbsdCategory']
        self.sasStage =          sqlCbsd['sasStage']
        self.txPower =           sqlCbsd['TxPower']
        self.earfcn =            sqlCbsd['EARFCN']
        self.antennaGain =       sqlCbsd['antennaGain']
        self.adminState =        0
        self.grantID =           sqlCbsd['grantID']
        self.operationalState =  sqlCbsd['operationalState']
        self.transmitExpireTime =sqlCbsd['transmitExpireTime']
        self.grantExpireTime =   sqlCbsd['grantExpireTime']
        self.cellIdenity =       sqlCbsd['CellIdentity']
        self.ipAddress =         sqlCbsd['IPAddress']
        self.connreqUname =      sqlCbsd['connreqUname']
        self.connreqPass =       sqlCbsd['connreqPass']
        self.connreqURL =        sqlCbsd['connreqURL']
        self.hclass =            sqlCbsd['hclass']
        
        #set maxEirp
        self.compute_maxEirp()
        #set Low and high Frequcy
        self.set_low_and_high_frequncy(self.earfcn)

        
    @abstractmethod
    def set_low_and_high_frequncy(self,earfcn):
        pass

    @abstractmethod
    def select_frequency(self,channels):
        pass

    def update_cbsd_attribute_database(self,column: str ,attribute) -> None:
        '''
        Given a database column and an attribute. We will update the database
        '''
        conn = dbConn(consts.DB)
        # sql = "UPDATE dp_device_info SET %s = %s WHERE SN = %s",(column,attribute,self.SN)
        # print(sql)
        conn.update("UPDATE dp_device_info SET %s = %s WHERE SN = %s",(column,attribute,self.SN))
        # conn.update("UPDATE `dp_device_info` SET ({}) WHERE SN IN %s".format(','.join(['%s'] * len(attribute))),(attribute,self.SN))
        conn.dbClose()

    def updateGrantTime(self,grantTime):
        self.grantExpireTime = grantTime


    def toggleAdminState(self,adminState: int):
        if adminState == 'false':
            # logging.info("Turn RF OFF for %s",cbsd['SN'])
            self.adminState = 0
        else:
            # logging.info("Turn on RF for %s",cbsd['SN'])
            self.adminState = 1

    def adjustPower(self,power):
        # logging.info("adjust to power to %s dBm",power)
        self.txPower = power
        self.compute_maxEirp()

    def compute_maxEirp(self):
        self.maxEirp = self.txPower + self.antennaGain
        # logging.info("adjust to maxEirp to %s dBm",maxEirp)

    def wait_for_execution():
        pass

    def setParamterValue(self,parameterValueList)-> None:
        '''
        Given a list of dicts containing datamodel_path, data_type and data_value
        setParameterValues will use the ACS to set this value on the cell.
        '''
        #connect to database
        conn = dbConn("ACS_V1_1")

        #add perodicInform to parameterValueList(sets new database values immediately after setting)
        parameterValueList.append(consts.PERIODIC_ONE)
        
        print(f"connected to IP: {self.ipAddress}")

        for i in range(len(parameterValueList)):
            
            #toggle Power on or off
            if parameterValueList[i]['data_path'] == consts.ADMIN_STATE:
                self.toggleAdminState(parameterValueList[i]['data_value'])

            #change cell power
            if parameterValueList[i]['data_path'] == consts.TXPOWER_PATH:
                self.adjustPower(parameterValueList[i]['data_value'])

            #change cell frequency
            if parameterValueList[i]['data_path'] == consts.EARFCN_LIST:
                self.set_low_and_high_frequncy(parameterValueList[i]['data_value'])


            #add parameterValues datamodel, type and value to spv database table
            conn.update('INSERT INTO fems_spv(`SN`, `spv_index`,`dbpath`, `setValueType`, `setValue`) VALUES(%s,%s,%s,%s,%s)',(self.SN,i,parameterValueList[i]['data_path'],parameterValueList[i]['data_type'],parameterValueList[i]['data_value']))

            #place action in apt_action_queue
            self.cbsdAction(self.SN,'Set Parameter Value',str(datetime.now()))
            
            #Make connection request
            response = requests.get(self.connreqURL, auth= HTTPDigestAuth(self.connreqUname,self.connreqPass))

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

    def set_cbsdID(self,cbsdID):
        #TODO update new value to database to relect changes on cbrsStatus page

        self.cbsdID = cbsdID


    #deregister method(clear all values associtaed with SAS)


class OneCA(CbsdInfo):

    def __init__(self,sqlCbsd):
        super(OneCA,self).__init__(sqlCbsd)
    
    def set_low_and_high_frequncy(self,earfcn):
        self.lowFrequency = 5
    
    def select_frequency(self,channels):
        pass


class TwoCA(CbsdInfo):

    def __init__(self,sqlCbsd):
        #to extend from 1CA add new varaibles here and use where applicaple in methods
        #ex self.earfcn2 = sqlCbsd['earfcn2']
        #must be before the call to super
        # self.earfcn2 = 2
        super(TwoCA,self).__init__(sqlCbsd)
       
    def set_low_and_high_frequncy(self,earfcn):
        self.lowFrequency = 8
        # print(self.earfcn2)

    def select_frequency(self,channels):
        #select freq with self.earfcn2
        pass

if __name__ == '__main__':
    conn = dbConn("ACS_V1_1")
    sqlCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",'900F0C732A02')

    # sql = "UPDATE `dp_device_info` SET ({}) WHERE SN IN %s".format(','.join(['%s'] * len(parameter)))

    # print(f"sql: {sql}")

    a = OneCA(sqlCbsd[0])
    b = TwoCA(sqlCbsd[0])

    a.update_cbsd_attribute_database('AdminState',1)
    print(f"1CA lowFreq: {a.lowFrequency}")
    print(f"2CA lowFreq: {b.lowFrequency}")


