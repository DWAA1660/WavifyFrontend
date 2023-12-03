import sqlite3

class Database():
    def __init__(self, database: str) -> None:
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.connection.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT,
            password TEXT,
            username TEXT,
            display_name TEXT
        )""")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY,
            owner_id Integer,
            songs TEXT,
            name TEXT
        )""")
        self.connection.commit()
        
    def execute(self, query:str, paramaters:tuple=None):
        
        """querys and commits"""
        print(query)
        res = self.connection.execute(query, paramaters)
        self.connection.commit()
        if "select" in query.lower():
            return res
        