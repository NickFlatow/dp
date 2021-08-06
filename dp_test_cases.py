from datetime import date, datetime
from lib.sasClient import sasClientClass
from lib.dbConn import dbConn
import unittest
import lib.consts as consts
import json

from lib.cbsd import OneCA as ONECA



# class CbsdTest(unittest.TestCase):
#     '''
#     Test Cases for generic cbsd class
#     '''
    
#     def test_setParameterValues_adminState_off(self):

#         '''
#         Tests if the adminState is being properly shut off
#         '''
#         cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
#         cbsd.setParamterValue([consts.ADMIN_POWER_OFF])
#         self.assertEqual(cbsd.adminState,0)

#         ass = cbsd.select_cbsd_database_value('AdminState')
#         self.assertEqual(ass[0]['AdminState'],0)


#     def test_update_expire_time(self):

#         grantTime    = "2021-05-28T19:18:33Z"
#         transmitTime = "2021-07-30T21:18:33Z"
#         cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
        
#         #set grant time
#         cbsd.updateExpireTime(grantTime,'grant')

#         #check cbsd grantTime matches grantTime
#         self.assertEqual(grantTime,cbsd.grantExpireTime)

#         #set transmitTime
#         cbsd.updateExpireTime(transmitTime,'transmit')
        
#         #check cbsd transmitTime matches transmitTime
#         self.assertEqual(transmitTime,cbsd.transmitExpireTime)

#         #get grant and transmit from database
#         dbGrantTime = cbsd.select_cbsd_database_value('grantExpireTime')
#         dbTransmitTime = cbsd.select_cbsd_database_value('transmitExpireTime')
        
#         #ensure they match
#         self.assertEqual(dbGrantTime[0]['grantExpireTime'],grantTime)
#         self.assertEqual(dbTransmitTime[0]['transmitExpireTime'],transmitTime) 
    
#     def test_EARFCNtoMHZ(self):
#         cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
#         self.assertEqual(cbsd.EARFCNtoMHZ(55240),3550)
#         self.assertEqual(cbsd.EARFCNtoMHZ(55990),3625)
#         self.assertEqual(cbsd.EARFCNtoMHZ(56739),3700)

#     def test_MHztoEARFCN(self):
#         cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
#         self.assertEqual(cbsd.MHZtoEARFCN(3550),55240)
#         self.assertEqual(cbsd.MHZtoEARFCN(3625),55990)
#         # self.assertEqual(cbsd.MHZtoEARFCN(3700),56739)

#     def test_expired(self):
#         pass
#         # cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
#         # time = str(datetime.utcnow())
#         # cbsd.expired(time,False)

#     def test_set_low_and_high_frequency(self):
#         cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
#         #low range
#         cbsd.set_low_and_high_frequncy(55340)
#         self.assertEqual(cbsd.lowFrequency,3550)
#         self.assertEqual(cbsd.highFrequency,3570)
#         #middle range
#         cbsd.set_low_and_high_frequncy(55990) 
#         self.assertEqual(cbsd.lowFrequency,3615)
#         self.assertEqual(cbsd.highFrequency,3635)


#     def test_get_earfcnList(self):
#         cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
#         # self.assertEqual(cbsd.earfcnList,['55590','55190','55490'])
#         # self.assertEqual(cbsd.earfcnList,['55590'])


#     #test for channel search
#     def test_select_frequency(self):
#         cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)

#         channels1 = consts.SPEC_EIRP
#         avaiableChannels1 = channels1['spectrumInquiryResponse'][0]['availableChannel']
#         #one where no frequcy is avalbile
#         self.assertEqual(cbsd.select_frequency(avaiableChannels1),False)


#         channels2 = consts.FS
#         avaiableChannels2 = channels2['spectrumInquiryResponse'][0]['availableChannel']

#         #one where earfcnInUse is used
#         self.assertEqual(cbsd.select_frequency(avaiableChannels2),True)
#         self.assertEqual(cbsd.earfcn,'55340')

#         # check database earfcn is equal to 55590
#         self.assertEqual(cbsd.select_cbsd_database_value('EARFCN'),'55340')



#         channels3 = consts.FS_MISING_55590
#         avaiableChannels3 = channels3['spectrumInquiryResponse'][0]['availableChannel']

#         #one where one of the backup earfcns are used from apt_subscription
#         self.assertEqual(cbsd.select_frequency(avaiableChannels3),True)
#         self.assertEqual(cbsd.earfcn,'55790')

#         #check database earfcn is equal to 55190
#         self.assertEqual(cbsd.select_cbsd_database_value('EARFCN'),'55190')


#         #TODO test for set Frequency


#         #TODO test for set power
#             #TODO test for calc MaxEirp


class sasClientTest(unittest.TestCase):
    
    def test_subHeart_function(self):
        conn = dbConn("ACS_V1_1")
        sqlCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",'900F0C732A02')
        cbsd1 = ONECA(sqlCbsd[0])

        conn = dbConn("ACS_V1_1")
        sqlCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",'DCE99461317E')
        cbsd2 = ONECA(sqlCbsd[0])

        sasClient = sasClientClass()

        sasClient.addOneCA(cbsd1)
        sasClient.addOneCA(cbsd2)

        cbsd1.subHeart = True
        cbsd1.setSasStage(consts.HEART)

        subheatList = sasClient.filter_subsequent_heartbeat()

        self.assertEqual([cbsd1],subheatList)
        # print(subheatList)


    def test_getCbsds_function(self):
        conn = dbConn("ACS_V1_1")
        sqlCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",'900F0C732A02')
        cbsd1 = ONECA(sqlCbsd[0])

        sasClient = sasClientClass()
        myDict = {'snDict':['900F0C732A02','DCE99461317E']}
    
        sasClient.addOneCA(cbsd1)

        cbsds = sasClient.getCbsds(myDict)

        self.assertEqual([cbsd1],cbsds)


    def test_reqlinquish_function(self):
        
        #create two cbsds
        conn = dbConn("ACS_V1_1")
        sqlCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",'900F0C732A02')
        cbsd1 = ONECA(sqlCbsd[0])

        conn = dbConn("ACS_V1_1")
        sqlCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",'DCE99461317E')
        cbsd2 = ONECA(sqlCbsd[0])

        #get sas client
        sasClient = sasClientClass()
        #create dereg dic
        deregDict = {'snDict':['900F0C732A02','DCE99461317E']}

        #make cbsds 1CA
        sasClient.addOneCA(cbsd1)
        sasClient.addOneCA(cbsd2)


        #turn power on
        cbsd1.adminState = 1
        cbsd2.adminState = 1

        #set grantID
        cbsd1.grantID = 1
        cbsd2.grantID = 2

        #set cbsdID
        cbsd1.cbsdID = 1
        cbsd2.cbsdID = 2

        #make cbsds heartbeating
        cbsd1.setSasStage(consts.HEART)
        cbsd2.setSasStage(consts.HEART)
        cbsd1.subHeart = True
        cbsd2.subHeart = True

        sasClient.userDeregisterCbsd(deregDict)







    

    def get_oneCA_test_CBSD(self,test_cbsd_sn) -> ONECA:
        conn = dbConn("ACS_V1_1")
        sqlCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",test_cbsd_sn)
        cbsd = ONECA(sqlCbsd[0])
        return cbsd


class TwoCAdifference(unittest.TestCase):
    '''
    Test cases for the definition of the Two abstract methods
    '''
    pass



if __name__ == '__main__':
    
    unittest.main()