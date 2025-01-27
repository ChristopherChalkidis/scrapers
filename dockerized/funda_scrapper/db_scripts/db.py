import sqlite3
# import os

def get_db(database_file: str):
    """
    Returns a connection to the (newly created) database.
        Parameters:
            database_file (str): the path to the database file to be opened 
        Returns: 
            db: a connection to the database
    """
    db = sqlite3.connect(database_file) 
    return db

def init_db(db, schema_file: str):
    """
    Reads and executes all SQL statements from an .sql file.
        Parameters:
            db: a database connection
            schema_file(str): path to an .sql file 
        Returns:
            None
    """
    with open(schema_file, mode='r') as f:
        c = db.cursor()
        c.executescript(f.read())

if __name__ == "__main__":
    # # For portability, we obtain the absolute path to the script
    # dirname = os.path.dirname(os.path.abspath(__file__))
    database_file = "/app/database/properties.db"
    schema_file = "/app/db_scripts/schema.sql"

    db= get_db(database_file)
    init_db(db, schema_file)
    db.commit()
    db.close()
