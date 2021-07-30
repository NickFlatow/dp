from dbConn import dbConn
import unittest

import consts

from cbsd import Cbsd as c


class CbsdTest(unittest.TestCase):

    def test_setParameterValues_adminState_off(self):

        '''
        Tests if the adminState is being properly shut off
        '''
        cbsd = self.get_test_CBSD(consts.TEST_CBSD_SN)
        cbsd.setParamterValue([consts.ADMIN_POWER_OFF])
        self.assertEqual(cbsd.adminState,0)


    #test for set Frequency


    #test for set power


    #test for calc MaxEirp


    #test for convert Earfcn to MHz


    #test for convert Mhz to earfcn

    #test for channel search

    def get_test_CBSD(self,test_cbsd_sn) -> c:
        conn = dbConn("ACS_V1_1")
        sqlCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",test_cbsd_sn)
        cbsd = c(sqlCbsd[0])
        return cbsd


if __name__ == '__main__':
    unittest.main()