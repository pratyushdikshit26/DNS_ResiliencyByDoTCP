from ripe_wrapper.database.request_pseudosection_table import RequestPseudosectionTable
from ripe_wrapper.database.database_table import DatabaseTable
import ipaddress
import json 
import time
import sqlite3

class RequestTable(DatabaseTable):
    COLUMNS = {
        "id" : "integer PRIMARY KEY NOT NULL",
        "question_name": 'text',
        "timestamp": 'integer',
        "response_size": "integer", 
        'backend_resolver': 'text',
        "proto": "text",
        "raw_data": "text",
        'flags': "text",
        'header': "text",
        'query_count': "integer",
        'ans_count': "integer",
        'auth_count': "integer",
        'addit_count': "integer",
        'question': "text",
        'udp_size': "integer"
    }
    TABLE_NAME = 'requests'
    
    def __init__(self):
        self.con = sqlite3.connect(self.DATABASE_PATH)
        self.cur = self.con.cursor()

    def add_request(self, question_name, timestamp, data, response_size):
        parts = data.split(" ")
        data, pseudosetion_data = self.parse_txt_data(parts)
        data["timestamp"] = timestamp
        data["question_name"] = question_name
        data["response_size"] = response_size
        id = self.add_item_get_id(data)
        pseudosection_table = RequestPseudosectionTable()
        for item in pseudosetion_data:
            item["request_id"] = id
           # pseudosection_table.save_pseudosection_item(item)
    

    def add_item_get_id(self, item):
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
        self.cur.execute(query)
        id = self.cur.lastrowid
        return id

    def commit(self):
        self.con.commit()

    def close(self):
        self.con.close()
            
    def parse_txt_data(self, data):
        before = time.perf_counter() 
        result = {}
        pseudosection_results = []
        for item in data: 
            if item.startswith("FROM"):
                parts = item.split('_')
                result["backend_resolver"] = parts[1]
            if item.startswith("Protocol"):
                parts = item.split('_')
                result["proto"] = parts[1]
            if item.startswith("opcode"):
                result["header"] = item.replace("&", " ").replace("$", "")
            if item.startswith("flags:"):
                parts = item.split('%')
                result["flags"] = parts[0].replace('flags:', '').replace('&', "")
                for part in parts[1:]:
                    inner_parts = part.split(",")
                    for inner_part in inner_parts:
                        single_items = inner_part.split("&")
                        if single_items[1] == "QUERY:":
                            result["query_count"] = single_items[2]
                        elif single_items[1] == "ANSWER:": 
                            result["ans_count"] = single_items[2]
                        elif single_items[1] == "AUTHORITY:": 
                            result["auth_count"] = single_items[2]
                        elif single_items[1] == "ADDITIONAL:": 
                            result["addit_count"] = single_items[2].replace("$", "")
            if item.startswith("OPT&PSEUDOSECTION"):
                parts = item.split('$%&') #"\n; "
                for part in parts[1:]:
                    inner_parts = part.split(":", 1)
                    res = {
                        "name": inner_parts[0],
                        "content": inner_parts[1].replace("&", " ").replace("$", "").replace(" ", "", 1).replace("%", ";")
                    }
                    if inner_parts[0] == "EDNS":
                        single_items = inner_parts[1].split("&")
                        for i in range(len(single_items)):
                            item_i = single_items[i]
                            if item_i.startswith("udp"):
                                result["udp_size"] = single_items[i+1].replace("$", "")
                    pseudosection_results.append(res)
            if item.startswith("QUESTION&SECTION:"):
                parts = item.split("$%") # "\n;"
                result["question"] = parts[1].replace("?", " ").replace("&", "").replace("$", "") 
        after = time.perf_counter() 
        return result, pseudosection_results
