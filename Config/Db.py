import pymysql
from Config.SecretManager import get_secret
import os
from dotenv import load_dotenv

load_dotenv()  

class Database:
    """
    Database configuration connection for read, write and close.
    """
    def __init__(self):
        self.region_name = os.getenv("AWS_REGION") 
        self.write_secret_name = os.getenv("SECRET_WRITE")
        self.read_secret_name = os.getenv("SECRET_READ")
        self.write_connection = None
        self.read_connection = None

    def connect_write(self):
        # Check current connection
        if self.write_connection and self.write_connection.open:
            return self.write_connection

        # Establish connection with 3 tries
        write_credentials = get_secret(self.write_secret_name, self.region_name)
        retries = 3
        while retries > 0:
            try:
                self.write_connection = pymysql.connect(
                    host=write_credentials["DB_HOST"],
                    user=write_credentials["DB_USER"],
                    password=write_credentials["DB_PASSWORD"],
                    database=write_credentials["DB_NAME"],
                    port=int(write_credentials.get("DB_PORT", 3306)),
                    cursorclass=pymysql.cursors.DictCursor
                )
                print("Write database connection established.")
                return self.write_connection
            except Exception as e:
                print(f"Error connecting to the write database: {e}")
                retries -= 1
                if retries == 0:
                    raise e

    def connect_read(self):
        # Check current connection
        if self.read_connection and self.read_connection.open:
            return self.read_connection

        # Establish connection with 3 tries
        read_credentials = get_secret(self.read_secret_name, self.region_name)
        retries = 3
        while retries > 0:
            try:
                self.read_connection = pymysql.connect(
                    host=read_credentials["DB_HOST"],
                    user=read_credentials["DB_USER"],
                    password=read_credentials["DB_PASSWORD"],
                    database=read_credentials["DB_NAME"],
                    port=int(read_credentials.get("DB_PORT", 3306)),
                    cursorclass=pymysql.cursors.DictCursor
                )
                print("Read database connection established.")
                return self.read_connection
            except Exception as e:
                print(f"Error connecting to the read database: {e}")
                retries -= 1
                if retries == 0:
                    raise e

    def close_connections(self):
        # C.s
        if self.write_connection and self.write_connection.open:
            self.write_connection.close()
            print("Write database connection closed.")

        if self.read_connection and self.read_connection.open:
            self.read_connection.close()
            print("Read database connection closed.")
