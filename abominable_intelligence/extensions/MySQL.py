import mysql.connector
from cryptography.fernet import Fernet
from data_manager import config_sql

config_sql = config_sql()
encrypt_key = Fernet(config_sql["encrypt_key"])
config_sql.pop("encrypt_key")


class Sql:
    class gw2:
        def insert(self, username: str, api_key: str):
            with mysql.connector.connect(**config_sql) as connection:
                with connection.cursor() as cursor:
                    query = "INSERT INTO gw2 (username, api_key) VALUES (%s, %s)"
                    encrypted_api_key = encrypt_key.encrypt(bytes(api_key, "utf-8"))
                    cursor.execute(query, (username, encrypted_api_key))
                    connection.commit()

        def update(self, username: str, api_key: str):
            with mysql.connector.connect(**config_sql) as connection:
                with connection.cursor() as cursor:
                    query = "UPDATE gw2 SET api_key = %s WHERE username = %s"
                    encrypted_api_key = encrypt_key.encrypt(bytes(api_key, "utf-8"))
                    cursor.execute(query, (encrypted_api_key, username))
                    connection.commit()

        def select(self, username: str):
            with mysql.connector.connect(**config_sql) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM gw2 WHERE username = %s"
                    cursor.execute(query, [username])
                    rows = cursor.fetchall()
                if rows:
                    return encrypt_key.decrypt(rows[0][-1])
                else:
                    return None
