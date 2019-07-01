# -*- coding: utf-8 -*-

import pymysql

class SQL:

    #dbc = ("localhost","root","","sim")

    def __init__(self):
        self.db = pymysql.connect( host='localhost',port=3316,user='root',passwd='',db='simdb')
        self.cursor = self.db.cursor()

    def query(self, sql, arg):
        self.cursor.execute(sql, arg)
        return self.cursor.fetchone()

    def select(self,sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def delete(self,sql):
        self.cursor.execute(sql)

    def querymany(self, sql, arg):
        self.cursor.executemany(sql, arg)
        return self.cursor.fetchone()

    def commit(self):
        self.db.commit()

    def close(self):
        self.cursor.close()


