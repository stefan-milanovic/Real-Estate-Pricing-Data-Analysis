import mysql.connector
from mysql.connector import Error
        
if __name__ == "__main__":

    try:
        db_connection = mysql.connector.connect(host='localhost', database='real_estate', user='root', password='root')
        if (db_connection.is_connected()):
            print("==> Connected to MySQL.")
            cursor = db_connection.cursor()
            

    except Error as e:
        print("==> Error while connecting to MySQL: ", e)
    
    finally:
        if (db_connection.is_connected()):
            cursor.close()
            db_connection.close()
            print("==> Disconnected from MySQL.")