


class Resposne():

    def __init__(self):
        self._responseCode: int
        self._responseMessage: str
        self._responseData: list


    @property
    def responseCode(self):
        return self._responseCode
    
    @responseCode.setter
    def responseCode(self, responseCode:int):
        self._responseCode = responseCode

    @property
    def responseMessage(self):
        return self._responseMessage

    @responseMessage.setter
    def responseMessage(self,reponseMessage:str):
        self._responseMessage = reponseMessage

    @property
    def responseData(self):
        return self._responseData

    @responseData.setter
    def responseData(self,responseData:list):
        self._responseData = responseData.copy()

    