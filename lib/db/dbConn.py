import pymysql
from test import app

class dbConn():
    def __init__(self,db):
        try:
            self.conn = pymysql.connect(host = app.config['HOST'], 
                                    user = app.config["USER"], 
                                    passwd = app.config["PASSWORD"], 
                                    database=db,
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = True)
            self.cursor = self.conn.cursor()
            self.commit = self.conn.commit()
        except Exception as e:    
            print(e)
    def dbClose(self):
        try:
            self.conn.close()
        except Exception as e:
            print(e)

    def queryall(self, sql, params=None):
        cursor = self._connect.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
        finally:
            cursor.close()
        return result

    def update(self, sql, params=None):
            self.cursor = self.conn.cursor()
            # cursor = self._connect.cursor()
            try:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                self._connect.commit()
            finally:
                cursor.close()
    def getSasStage(self, cbsd):
        self.cursor = self.conn.cursor()
        sql = 'SELECT sasStage from dp_device_info where SN = %s'
        cursor.execute(sql, cbsd)

    def setSasStage(self, cbsd):
        

