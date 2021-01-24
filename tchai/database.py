import configparser
import sqlite3

config = configparser.ConfigParser()
config.read('../config.ini')


def get_database():
    """Gets database from config file. """

    return sqlite3.connect('../' + config['PATH']['DATABASE'])


def initialize_database():
    """Initializes database with user and trans tables. """

    connection = get_database()
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE user(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            name TEXT UNIQUE,
            pay INTEGER
        )""")
    cursor.execute("""
        CREATE TABLE trans(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            p1 INTEGER,
            p2 INTEGER,
            amount INTEGER,
            date DATE,
            hash VARCHAR,
            signature VARCHAR,
            FOREIGN KEY(p1) REFERENCES user(id),
            FOREIGN KEY(p2) REFERENCES user(id)
        ) 
    """)
    connection.commit()
