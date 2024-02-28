import sqlite3


def run_schema_script(database_file, schema_script):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Read and execute the contents of the schema script
    with open(schema_script, 'r') as f:
        sql_script = f.read()
        cursor.executescript(sql_script)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    database_file = 'database/properties.db'
    schema_script = 'database_scripts/schema.sql'

    run_schema_script(database_file, schema_script)
