from dbConn import dbConn
import unittest

import consts

from cbsd import OneCA as ONECA


class CbsdTest(unittest.TestCase):
    '''
    Test Cases for generic cbsd class
    '''

    def test_setParameterValues_adminState_off(self):

        '''
        Tests if the adminState is being properly shut off
        '''
        cbsd = self.get_oneCA_test_CBSD(consts.TEST_CBSD_SN)
        cbsd.setParamterValue([consts.ADMIN_POWER_OFF])
        self.assertEqual(cbsd.adminState,0)


    #test for set Frequency


    #test for set power


    #test for calc MaxEirp


    #test for convert Earfcn to MHz


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