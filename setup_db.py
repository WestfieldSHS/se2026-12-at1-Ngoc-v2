import sqlite3  # Imports Python's built-in database library
import os  # Imports the operating system module for file paths

# Get the folder where this script is located
base_dir = os.path.abspath(os.path.dirname(__file__))  # Finds the exact folder path of this file

# Build the full path to the database file
db_path = os.path.join(base_dir, '.database', 'data_source.db')  # Combines folder path with database location

# Build the full path to the SQL file
sql_path = os.path.join(base_dir, '.database', 'my_queries.sql')  # Combines folder path with SQL file location
p
# Open and read the SQL file contents
with open(sql_path, 'r') as f:  # Opens the SQL file in read mode
    sql_script = f.read()  # Reads all the SQL commands into a variable

# Connect to the database and run all SQL commands
conn = sqlite3.connect(db_path)  # Opens a connection to the database file
conn.executescript(sql_script)  # Runs every SQL command in the file
conn.commit()  # Saves all changes to the database
conn.close()  # Closes the connection safely

print("Database setup complete!")  # Confirms the script finished successfully