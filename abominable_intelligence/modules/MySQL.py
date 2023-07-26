import mysql.connector
import yaml
from global_variables import config_path
from cryptography.fernet import Fernet

try:
    with open(config_path) as conf:
        f = yaml.load(conf, Loader=yaml.FullLoader)
        connection_config = {
            "host": f["host"],
            "user": f["user"],
            "password": f["password"],
            "database": f["database"],
        }
        encrypt_key = Fernet(f["encrypt_key"])
except FileNotFoundError:
    print("File not found")


class Sql:
    class gw2:
        def insert(self, username: str, api_key: str):
            with mysql.connector.connect(**connection_config) as connection:
                with connection.cursor() as cursor:
                    query = "INSERT INTO gw2 (username, api_key) VALUES (%s, %s)"
                    encrypted_api_key = encrypt_key.encrypt(bytes(api_key, "utf-8"))
                    cursor.execute(query, (username, encrypted_api_key))
                    connection.commit()

        def update(self, username: str, api_key: str):
            with mysql.connector.connect(**connection_config) as connection:
                with connection.cursor() as cursor:
                    query = "UPDATE gw2 SET api_key = %s WHERE username = %s"
                    encrypted_api_key = encrypt_key.encrypt(bytes(api_key, "utf-8"))
                    cursor.execute(query, (encrypted_api_key, username))
                    connection.commit()

        def select(self, username: str):
            with mysql.connector.connect(**connection_config) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM gw2 WHERE username = %s"
                    cursor.execute(query, (username,))
                    rows = cursor.fetchall()
                return encrypt_key.decrypt(rows[0][-1])
