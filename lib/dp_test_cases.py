from dbConn import dbConn
import unittest

import consts

from cbsd import OneCA as ONECA



class CbsdTest(unittest.TestCase):
    '''
    Test Cases for generic cbsd class
    '''
    

    # def test_setParameterValues_adminState_off(self):

    #     '''
    #     Tests if the adminState is being properly shut off
    #     '''
    #     cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
    #     cbsd.setParamterValue([consts.ADMIN_POWER_OFF])
    #     self.assertEqual(cbsd.adminState,0)

    #     ass = cbsd.select_cbsd_database_value('AdminState')
    #     self.assertEqual(ass[0]['AdminState'],0)

    def test_update_expire_time(self):

        grantTime    = "2021-05-28T19:18:33Z"
        transmitTime = "2021-07-30T21:18:33Z"
        cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
        
        #set grant time
        cbsd.updateExpireTime(grantTime,'grant')

        #check cbsd grantTime matches grantTime
        self.assertEqual(grantTime,cbsd.grantExpireTime)

        #set transmitTime
        cbsd.updateExpireTime(transmitTime,'transmit')
        
        #check cbsd transmitTime matches transmitTime
        self.assertEqual(transmitTime,cbsd.transmitExpireTime)

        #get grant and transmit from database
        dbGrantTime = cbsd.select_cbsd_database_value('grantExpireTime')
        dbTransmitTime = cbsd.select_cbsd_database_value('transmitExpireTime')
        
        #ensure they match
        self.assertEqual(dbGrantTime[0]['grantExpireTime'],grantTime)
        self.assertEqual(dbTransmitTime[0]['transmitExpireTime'],transmitTime) 


    #test for set Frequency


    #test for set power


    #test for calc MaxEirp

    #test for convert Earfcn to MHz
    def EARFCNtoMHZ(self):
        cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
        self.assertEqual(cbsd.EARFCNtoMHZ(58240),3550)
        self.assertEqual(cbsd.EARFCNtoMHZ(55990),3625)
        self.assertEqual(cbsd.EARFCNtoMHZ(56739),3700)


    #test for convert Mhz to earfcn


    #test for channel search

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