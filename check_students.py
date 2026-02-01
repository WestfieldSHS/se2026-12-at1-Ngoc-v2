import sqlite3  # Import database library
import os  # Import file path library

# Get the database file path
base_dir = os.path.abspath(os.path.dirname(__file__))  # Find this script's folder
db_path = os.path.join(base_dir, '.database', 'data_source.db')  # Build full database path

# Connect to database
conn = sqlite3.connect(db_path)  # Open connection
conn.row_factory = sqlite3.Row  # Allow column name access

# Get all students
students = conn.execute('SELECT * FROM Students').fetchall()  # Fetch all records

# Display results
print(f"Total students in database: {len(students)}")  # Show count
for student in students:  # Loop through each student
    print(f"  Name: {student['name']}")  # Show their name
    print(f"  Username: {student['username']}")  # Show their username
    print(f"  Password Hash: {student['password_hash']}")  # Show their secure hash
    print(f"  Email: {student['email']}")  # Show their email
    print("---")  # Separator line

conn.close()  # Close connection