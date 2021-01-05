import sqlite3

import config as cfg


def get_database():
    return sqlite3.connect(cfg.DATABASE)


def initialize_database():
    connection = get_database()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE user(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            name TEXT UNIQUE,
            pay INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE trans(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            p1 INTEGER,
            p2 INTEGER,
            amount INTEGER,
            date DATE,
            hash VARCHAR,
            FOREIGN KEY(p1) REFERENCES user(id),
            FOREIGN KEY(p2) REFERENCES user(id)
        ) 
    """)
    connection.commit()
