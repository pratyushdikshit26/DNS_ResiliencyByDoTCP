from abc import ABC, abstractmethod
import sqlite3
import pandas as pd
from pytz import AmbiguousTimeError

class DatabaseTable():
    COLUMNS = {}
    FOREIGN_KEYS = ""
    PRIMARY_KEY = ""
    TABLE_NAME = ""
    DATABASE_PATH = "ripe_results.db"
    

    def create_table(self):
        con = sqlite3.connect(self.DATABASE_PATH)
        cur = con.cursor()
        create_string = ""
        for key in self.COLUMNS.keys():
            create_string += f'{key} {self.COLUMNS[key]}, '
        if len(create_string) > 2:
            create_string = create_string[:-2]
        if len(self.PRIMARY_KEY) > 0:
            create_string += f', {self.PRIMARY_KEY}'
        if len(self.FOREIGN_KEYS) > 0:
            create_string += f', {self.FOREIGN_KEYS}'
        query = f'CREATE TABLE {self.TABLE_NAME} ({create_string})'
        cur.execute(query)  
        con.commit()
        con.close()

    def exists(self, filters):
        con = sqlite3.connect(self.DATABASE_PATH)
        cur = con.cursor()
        try:
            params = ()
            condition_string = ""
            for key in filters.keys():
                condition_string += f"{key} = ? AND "
                params += (f'{filters[key]}',)
            if len(condition_string) > 4:
                condition_string = condition_string[:-5]
            query = f"SELECT 1 FROM {self.TABLE_NAME} WHERE {condition_string}"
            cur.execute(query, params)
            return cur.fetchone() is not None
        except (Exception) as error:
            print(error)
            return False

    def execute_query(self, query):
        conn = sqlite3.connect(self.DATABASE_PATH)
        results = pd.read_sql(query, conn)
        return results


    def add_item(self, item):
        value_string = ""
        for key in self.COLUMNS.keys():
            try: 
                value = f"'{item[key]}'"
                if value is None:
                    value = 'NULL'
                value_string += f'{value},'
            except:
                #print(f"Did not find attibute {key}.")
                value = 'NULL'
                value_string += f'{value},'
        
        if len(value_string) > 0: 
            value_string = value_string[:-1]
        query = f"INSERT INTO {self.TABLE_NAME} VALUES ({value_string})" 
        con = sqlite3.connect(self.DATABASE_PATH)
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        con.close()

