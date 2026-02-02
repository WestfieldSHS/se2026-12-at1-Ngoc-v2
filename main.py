import sqlite3  # Imports SQLite so we can create tables and run queries
import os  # Imports OS so we can build correct file paths
from flask import (
    Flask,
    render_template,
    request,
)  # Imports Flask tools for routing and forms
from flask_bcrypt import Bcrypt  # Imports Bcrypt so we can hash passwords securely

app = Flask(__name__)  # Creates the Flask app object
bcrypt = Bcrypt(app)  # Attaches Bcrypt to the app for hashing and checking passwords


def get_paths():  # Defines a helper function to build file paths in one place
    base_dir = os.path.abspath(
        os.path.dirname(__file__)
    )  # Gets the folder where main.py is
    db_path = os.path.join(
        base_dir, ".database", "data_source.db"
    )  # Builds the path to the database file
    sql_path = os.path.join(
        base_dir, ".database", "my_queries.sql"
    )  # Builds the path to the SQL setup file
    return (
        base_dir,
        db_path,
        sql_path,
    )  # Returns the paths so other functions can use them


def get_db():  # Defines a function that returns a database connection
    _, db_path, _ = get_paths()  # Gets the database path from the helper
    conn = sqlite3.connect(db_path)  # Opens a connection to the database file
    conn.row_factory = (
        sqlite3.Row
    )  # Makes rows accessible by column name (better than indexes)
    conn.execute(
        "PRAGMA foreign_keys = ON;"
    )  # Enforces relational integrity for this connection
    return conn  # Returns the open connection


def ensure_students_columns(
    conn,
):  # Defines a function to add missing columns safely (no DROP)
    conn.row_factory = sqlite3.Row  # Ensures PRAGMA results can be read by column name
    rows = conn.execute(
        "PRAGMA table_info(Students);"
    ).fetchall()  # Reads the real Students columns from the database
    existing = {row["name"] for row in rows}  # Creates a set of existing column names
    if "course_id" not in existing:  # Checks if course_id is missing
        conn.execute(
            "ALTER TABLE Students ADD COLUMN course_id INTEGER;"
        )  # Adds course_id column safely
    if "time_slot" not in existing:  # Checks if time_slot is missing
        conn.execute(
            "ALTER TABLE Students ADD COLUMN time_slot TEXT;"
        )  # Adds time_slot column safely
    if "selected_tutor_id" not in existing:  # Checks if selected_tutor_id is missing
        conn.execute(
            "ALTER TABLE Students ADD COLUMN selected_tutor_id INTEGER;"
        )  # Adds selected_tutor_id column safely
    if (
        "selected_tutor" in existing
    ):  # Checks if the old selected_tutor text column exists
        conn.execute(
            """
            UPDATE Students
            SET selected_tutor_id = (
                SELECT tutor_id
                FROM Tutors
                WHERE Tutors.full_name = Students.selected_tutor
            )
            WHERE selected_tutor_id IS NULL
              AND selected_tutor IS NOT NULL;
            """
        )  # Backfills selected_tutor_id from the old selected_tutor name values
    conn.commit()  # Saves schema and data updates so Flask can insert without crashing


def ensure_database_ready():  # Defines a function that runs setup + migration at Flask start
    _, db_path, sql_path = get_paths()  # Gets the database path and SQL file path
    os.makedirs(
        os.path.dirname(db_path), exist_ok=True
    )  # Ensures the .database folder exists
    conn = sqlite3.connect(
        db_path
    )  # Opens a connection even if the DB file does not exist yet
    conn.execute(
        "PRAGMA foreign_keys = ON;"
    )  # Turns on foreign key enforcement for setup
    with open(sql_path, "r", encoding="utf-8") as f:  # Opens the SQL file safely
        sql_script = f.read()  # Reads all SQL text into a string
    conn.executescript(
        sql_script
    )  # Runs the SQL file (CREATE TABLE IF NOT EXISTS + INSERT OR IGNORE)
    conn.commit()  # Saves table creation and seed data
    try:  # Starts a protection block in case Students does not exist yet
        ensure_students_columns(conn)  # Adds missing columns without deleting the table
    except sqlite3.Error:  # Runs if Students does not exist for any reason
        conn.commit()  # Saves any changes that did succeed
    conn.close()  # Closes the database connection cleanly


def get_db():  # Defines a function to open a database connection
    base_dir = os.path.abspath(
        os.path.dirname(__file__)
    )  # Finds the current folder path
    db_path = os.path.join(
        base_dir, ".database", "data_source.db"
    )  # Locates the database file
    conn = sqlite3.connect(db_path)  # Physically opens the connection to the SQL file
    conn.row_factory = sqlite3.Row  # Configures results to be accessible by column name
    return conn  # Returns the active connection for the routes to use


@app.route("/")  # Sets the URL path for the homepage
def home():  # Function to handle the home screen logic
    conn = get_db()  # Connects to the database
    tutors = conn.execute(
        "SELECT * FROM Tutors"
    ).fetchall()  # Fetches all tutors for display
    conn.close()  # Closes the connection to prevent memory leaks
    return render_template(
        "web1/index.html", tutors=tutors
    )  # Loads the homepage with data


@app.route("/about")  # Sets the URL path for the tutor bio page
def about():  # Function to handle the tutor information logic
    conn = get_db()  # Connects to the database
    tutors = conn.execute(
        "SELECT * FROM Tutors"
    ).fetchall()  # Fetches every tutor record
    conn.close()  # Closes the database connection
    return render_template(
        "web1/about.html", tutors=tutors
    )  # Loads the about page with data


@app.route("/account")  # Sets the URL path for account creation
def account():  # Function to show the signup form
    return render_template("web1/account.html")  # Displays the registration form


@app.route(
    "/class", methods=["GET", "POST"]
)  # Added "GET" to the list of allowed methods
def select_class():  # Function to process Step 1 and show Step 2
    # If the user is just visiting the page (like Lighthouse does)
    if request.method == "GET":
        conn = get_db()  # Connect to database
        courses = conn.execute(
            "SELECT * FROM Courses"
        ).fetchall()  # Get courses for display
        conn.close()  # Close connection
        # Show the page with empty values so Lighthouse can audit it
        return render_template(
            "web1/class.html",
            courses=courses,
            fullname="",
            email="",
            username="",
            password="",
        )

    # This part handles the actual form submission from the account page
    fullname = request.form.get("fullname")  # Gets student name
    email = request.form.get("email")  # Gets email
    username = request.form.get("username")  # Gets username
    password = request.form.get("password")  # Gets password (plain text before hashing)

    conn = get_db()  # Connect to database
    # Check for duplicate username
    existing_user = conn.execute(
        "SELECT student_id FROM Students WHERE username = ?", (username,)
    ).fetchone()
    if existing_user:
        conn.close()
        return render_template("web1/account.html", error="Username already exists.")

    pw_hash = bcrypt.generate_password_hash(password).decode(
        "utf-8"
    )  # Security requirement SE-12-07
    courses = conn.execute("SELECT * FROM Courses").fetchall()  # Get course list
    conn.close()  # Close connection

    return render_template(
        "web1/class.html",
        courses=courses,
        fullname=fullname,
        email=email,
        username=username,
        password=pw_hash,
    )


@app.route("/quiz", methods=["POST"])  # Sets the path for Step 3: Tutor Selection
def quiz():  # Function to process Step 2 and show Step 3
    data = request.form  # Collects all data sent from the course form
    conn = get_db()  # Connects to the database
    query = """SELECT
    Tutors.tutor_id AS tutor_id,
    Tutors.full_name AS full_name,
    GROUP_CONCAT(Traits.trait_name, ", ") AS traits
    FROM Tutors
    JOIN Tutor_Traits ON Tutors.tutor_id = Tutor_Traits.tutor_id
    JOIN Traits ON Tutor_Traits.trait_id = Traits.trait_id
    GROUP BY Tutors.tutor_id;
    """  # Builds a many-to-many view of tutors and their traits
    tutors = conn.execute(query).fetchall()  # Runs the query and collects the rows
    traits = conn.execute(
        "SELECT * FROM Traits"
    ).fetchall()  # Gets the list of filter traits
    conn.close()  # Closes the database connection
    return render_template(
        "web1/quiz.html", tutors=tutors, traits=traits, **data
    )  # Moves to Step 3


@app.route("/final", methods=["POST"])  # Sets the path for the registration completion
def final():  # Function to save data and show success
    name = request.form.get("fullname")  # Gets student name
    email = request.form.get("email")  # Gets student email
    user = request.form.get("username")  # Gets student username
    pw = request.form.get("password")  # Gets hashed password
    c_id = request.form.get("course_id")  # Gets course ID (Integer)
    time = request.form.get("time")  # Gets selected time slot
    t_id = request.form.get(
        "selected_tutor_id"
    )  # THE FIX: Gets tutor ID directly from form
    conn = get_db()  # Connects to the database

    # Check if username already exists BEFORE inserting
    existing = conn.execute(
        "SELECT student_id FROM Students WHERE username = ?", (user,)
    ).fetchone()  # Checks for duplicate
    if existing:  # If username is taken
        conn.close()  # Close connection
        return (
            "Error: Username already exists. Please go back and choose a different username.",
            400,
        )  # Returns error message

    sql = "INSERT INTO Students (name, email, username, password_hash, course_id, time_slot, selected_tutor_id) VALUES (?, ?, ?, ?, ?, ?, ?)"  # SQL structure
    conn.execute(
        sql, (name, email, user, pw, c_id, time, t_id)
    )  # Saves the student record
    conn.commit()  # Confirms the changes in the .db file

    # Get course name for display
    c_row = conn.execute(
        "SELECT course_name FROM Courses WHERE course_id = ?", (c_id,)
    ).fetchone()  # Gets course name
    # Get tutor name for display
    t_row = conn.execute(
        "SELECT full_name FROM Tutors WHERE tutor_id = ?", (t_id,)
    ).fetchone()  # Gets tutor name
    t_name = t_row["full_name"] if t_row else "Unknown"  # Safely gets name or default
    conn.close()  # Closes the database

    return render_template(
        "web1/final.html",
        fullname=name,
        email=email,
        username=user,
        course=c_row["course_name"] if c_row else "Unknown",
        time=time,
        selected_tutor=t_name,
    )  # Shows final success


@app.route("/login")  # Sets the URL path to /login
def login():  # Function to handle the login screen logic
    return render_template("web1/login.html")  # Loads the login page file


@app.route("/view_profile", methods=["POST"])  # Handles the login form submission
def view_profile():  # Function to verify user and show their data
    username = request.form.get("username")  # Gets username from the login form
    password = request.form.get("password")  # Gets plain password from the login form

    conn = get_db()  # Connects to the database
    # Finds the student record that matches the username
    user_row = conn.execute(
        "SELECT * FROM Students WHERE username = ?", (username,)
    ).fetchone()

    if user_row:  # If a user with that name exists
        # Checks if the typed password matches the hashed password in the DB (SE-12-07)
        if bcrypt.check_password_hash(user_row["password_hash"], password):
            # Gets the Course name and Tutor name using JOIN (SE-12-02)
            query = """
                SELECT Students.*, Courses.course_name, Tutors.full_name AS tutor_name
                FROM Students
                LEFT JOIN Courses ON Students.course_id = Courses.course_id
                LEFT JOIN Tutors ON Students.selected_tutor_id = Tutors.tutor_id
                WHERE Students.username = ?
            """
            profile_data = conn.execute(query, (username,)).fetchone()
            conn.close()  # Closes connection safely
            # Sends user data to a new profile page
            return render_template("web1/profile.html", user=profile_data)

    conn.close()  # Closes connection if login fails
    # Returns an error message if the username or password is wrong
    return "Invalid username or password. Please go back and try again.", 401


if __name__ == "__main__":  # Checks if main.py is being run directly
    ensure_database_ready()  # Runs database setup + migration automatically for Flask
    app.run(debug=True)  # Starts the Flask development server
