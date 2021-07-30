import pymysql
# from test import app
import logging
# import lib.consts as consts

class dbConn():
    def __init__(self,db):
        try:
            # self.conn = pymysql.connect(host = app.config['HOST'], 
            #                         user = app.config["USER"], 
            #                         passwd = app.config["PASSWORD"], 
            #                         database=db,
            #                         cursorclass = pymysql.cursors.DictCursor,
            #                         autocommit = True)
            self.conn = pymysql.connect(host = 'localhost', 
                                    user = 'root', 
                                    passwd = 'N3wPr1vateNw', 
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
        logging.debug("SQL COMMAND: " + sql + " params: " +  str(params))
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
            logging.debug("SQL COMMAND: " + sql + " params: " +  str(params))
            print("SQL COMMAND: " + sql + " params: " +  str(params))
            try:
                if params:
                    self.cursor.execute(sql, params)
                else:
                    self.cursor.execute(sql)
                self.conn.commit()
            except Exception as e:
                logging.debug(e)
            finally:
                self.cursor.close()
    def updateSasStage(self,sasStage,cbsds_SN_list):
            self.cursor = self.conn.cursor()
            sql = "UPDATE `dp_device_info` SET `sasStage` = \'" +sasStage+ "\' WHERE SN IN ({})".format(','.join(['%s'] * len(cbsds_SN_list)))
            logging.debug("SQL COMMAND: " + sql + " cbsd list: " +  str(cbsds_SN_list))
            try:
                self.cursor.execute(sql,cbsds_SN_list)
                self.conn.commit()
            except Exception as e:
                logging.debug(e)
            finally:
                self.cursor.close()
    def setSasStage(self, cbsd):  
        pass


