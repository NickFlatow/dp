from lib.dbConn import dbConn

class License:

    def __init__(self):
        license = self.getLicense()
        self.remainingtime = license['remainingTime']
        self.authType = license['funcVal0']
        self.numEnB = license['funcVal2']

    def getLicense(self) -> dict:
        conn = dbConn("epc_database")
        license = conn.select("SELECT * FROM EPCSecureInfo")
        conn.dbClose()
        return license[0]

