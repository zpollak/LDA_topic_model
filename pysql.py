#!/usr/bin/env python

import pyodbc

class SQL:
    def __init__(self, driver, server, user):
        self.driver = driver
        self.server = server
        self.user = user
        self._cxn = pyodbc.connect(Driver=self.driver, Trusted_Connection='yes', Server=self.server, UID=self.user)
        self._cursor = self._cxn.cursor()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cxn.commit()
        self.cxn.close()
    
    @property
    def cxn(self):
        return self._cxn
    
    @property
    def cursor(self):
        return self._cursor
    
    def description(self):
        return self.cursor.description
    
    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
    
    def fetchall(self):
        return self.cursor.fetchall()
    
    # Use when result set too large for fetch_all()
    def fetchall_gen(self, block_size=1000):
        while True:
            results = self.fetchmany(block_size)
            if not results:
                break
            for result in results:
                yield result
    
    def fetchmany(self, n_rows):
        return self.cursor.fetchmany(n_rows)
    
    def fetchone(self):
        return self.cursor.fetchone()