import pymysql
from test import app
import logging

class dbConn():
    def __init__(self,db):
        try:
            self.conn = pymysql.connect(host = app.config['HOST'], 
                                    user = app.config["USER"], 
                                    passwd = app.config["PASSWORD"], 
                                    database=db,
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = True)
            # self.cursor = self.conn.cursor()
            # self.commit = self.conn.commit()
        except Exception as e:    
            print(e)
    def dbClose(self):
        try:
            self.conn.close()
        except Exception as e:
            print(e)

    def select(self, sql, params=None):
        self.cursor = self.conn.cursor()
        logging.info("SQL COMMAND: " + sql + " params: " +  str(params))
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            result = self.cursor.fetchall()
        finally:
            self.cursor.close()
        return result
    def update(self, sql, params=None):
            self.cursor = self.conn.cursor()
            logging.info("SQL COMMAND: " + sql + " params: " +  str(params))
            try:
                if params:
                    self.cursor.execute(sql, params)
                else:
                    self.cursor.execute(sql)
                self.conn.commit()
            except Exception as e:
                logging.info(e)
            finally:
                self.cursor.close()
    def getSasStage(self, cbsd):
        self.cursor = self.conn.cursor()
        sql = 'SELECT sasStage from dp_device_info where SN = %s'
        cursor.execute(sql, cbsd)

    def setSasStage(self, cbsd):
        pass


