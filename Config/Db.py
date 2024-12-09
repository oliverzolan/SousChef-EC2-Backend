import pymysql
from Config.SecretManager import get_secret
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access environment variables
AWS_REGION = os.getenv("AWS_REGION")
SECRET_WRITE = os.getenv("SECRET_WRITE")
SECRET_READ = os.getenv("SECRET_READ")


class Database:
    """
    Database configuration and connection management for read and write operations.
    """

    def __init__(self, write_secret=SECRET_WRITE, read_secret=SECRET_READ, region_name=AWS_REGION):
        self.write_secret_name = write_secret
        self.read_secret_name = read_secret
        self.region_name = region_name
        self.write_connection = None
        self.read_connection = None

    def connect_write(self):
        """
        Establish a connection to the write database using credentials from Secrets Manager.
        Retries 3 times in case of failure.
        """
        if self.write_connection and self.write_connection.open:
            return self.write_connection

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
        """
        Establish a connection to the read database using credentials from Secrets Manager.
        Retries 3 times in case of failure.
        """
        if self.read_connection and self.read_connection.open:
            return self.read_connection

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
        """
        Close both the write and read database connections if they are open.
        """
        if self.write_connection and self.write_connection.open:
            self.write_connection.close()
            print("Write database connection closed.")

        if self.read_connection and self.read_connection.open:
            self.read_connection.close()
            print("Read database connection closed.")
