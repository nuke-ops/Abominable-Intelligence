import mysql.connector
import yaml
from cryptography.fernet import Fernet
from global_variables import config_path


def _setup():
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
            return {"connection_config": connection_config, "encrypt_key": encrypt_key}
    except FileNotFoundError:
        print("SQL module: File not found")


class Sql:
    class gw2:
        def insert(self, username: str, api_key: str):
            connection_conf = _setup()["connection_config"]
            encrypt_key = _setup()["encrypt_key"]
            with mysql.connector.connect(**connection_conf) as connection:
                with connection.cursor() as cursor:
                    query = "INSERT INTO gw2 (username, api_key) VALUES (%s, %s)"
                    encrypted_api_key = encrypt_key.encrypt(bytes(api_key, "utf-8"))
                    cursor.execute(query, (username, encrypted_api_key))
                    connection.commit()

        def update(self, username: str, api_key: str):
            connection_conf = _setup()["connection_config"]
            encrypt_key = _setup()["encrypt_key"]
            with mysql.connector.connect(**connection_conf) as connection:
                with connection.cursor() as cursor:
                    query = "UPDATE gw2 SET api_key = %s WHERE username = %s"
                    encrypted_api_key = encrypt_key.encrypt(bytes(api_key, "utf-8"))
                    cursor.execute(query, (encrypted_api_key, username))
                    connection.commit()

        def select(self, username: str):
            connection_conf = _setup()["connection_config"]
            encrypt_key = _setup()["encrypt_key"]
            with mysql.connector.connect(**connection_conf) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM gw2 WHERE username = %s"
                    cursor.execute(query, (username,))
                    rows = cursor.fetchall()
                if rows:
                    return encrypt_key.decrypt(rows[0][-1])
                else:
                    return None
