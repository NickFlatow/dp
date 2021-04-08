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



