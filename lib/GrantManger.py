import time


class GrantManger():
    
    
    def __init__(self):
        self.test = "test"
        self.data = []

    def setData1(self,data):
        self.data.append(data)

    def setData2(self,data):
        self.data.append(data)

    def getData1(self):
        return not self.data

    def printTest(self):
        while True:
            print("second thread")
            time.sleep(3)


    def StartChannelSelectionProcess():
        pass