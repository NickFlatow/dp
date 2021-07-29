

class CbsdInfo:
    cbsdID: str
    lowFrequency: int
    highFrequency: int

    def __init__(self,userID,fccID,sasStage,txPower,earfcn,antennaGain,ipAddress,connreqUname,connreqURL):
        self.userID = userID
        self.fccID = fccID
        self.sasStage = sasStage
        self.txPower = txPower
        self.earfcn = earfcn
        self.antennaGain = antennaGain
        self.ipAddress = ipAddress
        self.connreqUname = connreqUname
        self.connreqURL = connreqURL

    def set_cbsdID(self,cbsdID):
        self.cbsdID = cbsdID

    def compute_maxEirp(self):
        return self.txPower + self.antennaGain


    #set txPower

    #

class Cbsd:

    def __init__(self, SN, info):
        self.SN = SN
        self.info = info

    def setParamterValue(self,parameterValueList):
        '''
        sets new paramter value on cell
        updates cbsd class
        '''

        print()


        #add perodicInform to parameterValueList

        #add parameterValues datamodel, type and value to spv database table

        #Make connection request

        #Wait for conenction request to complete
