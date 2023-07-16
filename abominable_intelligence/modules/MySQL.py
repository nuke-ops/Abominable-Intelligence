import mysql.connector
import yaml
from global_variables import config_path


with open(config_path) as conf:
    f = yaml.load(conf, Loader = yaml.FullLoader)
    connection_config = {
    'host'     : f["host"],
    'user'     : f["user"],
    'password' : f["password"],
    'database' : f["database"]
    }


def insert(table, collumns, values):
    with mysql.connector.connect(**connection_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO {table} ({collumns}) VALUES ({values})")
            connection.commit()

def fetch(table, condition):
    with mysql.connector.connect(**connection_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table} WHERE {condition}")
            rows = cursor.fetchall()
            
        return rows
