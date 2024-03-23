import mysql.connector
from mysql.connector import MySQLConnection


def get_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='SQL-rooter',  # Enter your own password here
    )
    conn.set_character_set_name('utf8mb4')
    return conn


def get_response_object(conn: MySQLConnection, query: str, params: tuple = (), dictionary: bool = True) -> list:
    cursor = conn.cursor(dictionary=dictionary)
    cursor.execute(query, params)
    response = cursor.fetchall()
    return response


def insert(conn: MySQLConnection, insert_statement: str, params=()) -> None:
    cursor = conn.cursor()
    cursor.execute(insert_statement, params)
    conn.commit()
    return


def update(conn: MySQLConnection, update_statement: str, params=()) -> None:
    cursor = conn.cursor()
    cursor.execute(update_statement, params)
    conn.commit()
    return


def delete(conn: MySQLConnection, delete_statement: str, params=()) -> None:
    cursor = conn.cursor()
    cursor.execute(delete_statement, params)
    conn.commit()
    return
