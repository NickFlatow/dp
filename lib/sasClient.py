from dbConn import dbConn
from cbsd import CbsdModelExporter
import consts


class sasClient():
    '''
    One stop shop for all your SAS communication needs.\n
    You got cbsds needing specturm?\n
    We got connections :|
    '''
    def __init__(self):
        self.cbsdList = []
        self.heartbeatList = []

    def get_cbsd_database_row(self,SN: str) -> dict:
        '''Given a cbsd Serial Number the fucntion will return a dict with cbsd attributes'''
        conn = dbConn(consts.DB)
        cbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",SN)
        conn.dbClose()

        return cbsd

    def create_cbsd(self,SN):

        sqlCbsd = self.get_cbsd_database_row(SN)
        a = CbsdModelExporter.getCbsd(sqlCbsd[0])
        
        self.cbsdList.append(CbsdModelExporter.getCbsd(sqlCbsd[0]))
    


    # def registration_request(self):
    #     pass

    # def registration_response(self):
    #     pass

    # def specturm_inquiry_request(self):
    #     pass
    
    # def spectrum_inquiry_response(self):
    #     pass

    # def grant_request(self):
    #     pass

    # def grant_response(self):
    #     pass

    # def heartbeat_request():
    #     pass 

    # def heartbeat_reponse():
    #     pass

        

if __name__ == '__main__':
    
    s = sasClient()
    s.create_cbsd('DCE994613163')
    print(s.cbsdList[0].sasStage)

    print("Look at me")


