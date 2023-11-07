import mysql.connector
from cryptography.fernet import Fernet
from data_manager import config_sql


class Sql:
    config_sql = config_sql()
    if config_sql["encrypt_key"]:
        encrypt_key = Fernet(config_sql["encrypt_key"])
        config_sql.pop("encrypt_key")

    class gw2:
        @classmethod
        def insert(cls, username: str, api_key: str) -> None:
            with mysql.connector.connect(**Sql.config_sql) as connection:
                with connection.cursor() as cursor:
                    query = "INSERT INTO gw2 (username, api_key) VALUES (%s, %s)"
                    encrypted_api_key = Sql.encrypt_key.encrypt(bytes(api_key, "utf-8"))
                    cursor.execute(query, (username, encrypted_api_key))
                    connection.commit()

        @classmethod
        def update(cls, username: str, api_key: str) -> None:
            with mysql.connector.connect(**Sql.config_sql) as connection:
                with connection.cursor() as cursor:
                    query = "UPDATE gw2 SET api_key = %s WHERE username = %s"
                    encrypted_api_key = Sql.encrypt_key.encrypt(bytes(api_key, "utf-8"))
                    cursor.execute(query, (encrypted_api_key, username))
                    connection.commit()

        @classmethod
        def select(cls, username: str) -> str:
            with mysql.connector.connect(**Sql.config_sql) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM gw2 WHERE username = %s"
                    cursor.execute(query, [username])
                    rows = cursor.fetchall()
                if not rows:
                    return None
                return Sql.encrypt_key.decrypt(rows[0][-1]).decode("utf-8")
