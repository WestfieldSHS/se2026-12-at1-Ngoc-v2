import sqlite3  # Import database library
import os  # Import file path library
from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,  # Added to serve service worker
)  # Imports Flask tools for routing and forms
from flask_bcrypt import Bcrypt  # Imports Bcrypt for password hashing

app = Flask(__name__)  # Creates the Flask app object
bcrypt = Bcrypt(app)  # Attaches Bcrypt to the app


def get_paths():  # Helper function to build file paths
    base_dir = os.path.abspath(os.path.dirname(__file__))  # Gets script folder
    db_path = os.path.join(base_dir, ".database", "data_source.db")  # Database path
    sql_path = os.path.join(base_dir, ".database", "my_queries.sql")  # SQL file path
    return base_dir, db_path, sql_path  # Returns all paths


def get_db():  # Opens a database connection
    _, db_path, _ = get_paths()  # Gets database path
    conn = sqlite3.connect(db_path)  # Opens connection
    conn.row_factory = sqlite3.Row  # Allows column name access
    conn.execute("PRAGMA foreign_keys = ON;")  # Enforces foreign keys
    return conn  # Returns the connection


def ensure_students_columns(conn):  # Adds missing columns safely
    conn.row_factory = sqlite3.Row  # Ensures column name access
    rows = conn.execute("PRAGMA table_info(students);").fetchall()  # Gets columns
    existing = {row["name"] for row in rows}  # Creates set of column names
    if "course_id" not in existing:  # Checks if course_id missing
        conn.execute("ALTER TABLE students ADD COLUMN course_id INTEGER;")  # Adds it
    if "time_slot" not in existing:  # Checks if time_slot missing
        conn.execute("ALTER TABLE students ADD COLUMN time_slot TEXT;")  # Adds it
    if "selected_tutor_id" not in existing:  # Checks if selected_tutor_id missing
        conn.execute(
            "ALTER TABLE students ADD COLUMN selected_tutor_id INTEGER;"
        )  # Adds it
    if "selected_tutor" in existing:  # Checks for old column
        conn.execute(
            """
            UPDATE students
            SET selected_tutor_id = (
                SELECT tutor_id FROM tutors
                WHERE tutors.full_name = students.selected_tutor
            )
            WHERE selected_tutor_id IS NULL AND selected_tutor IS NOT NULL;
        """
        )  # Backfills data
    conn.commit()  # Saves changes


def ensure_database_ready():  # Runs setup at Flask start
    _, db_path, sql_path = get_paths()  # Gets paths
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Creates folder if needed
    conn = sqlite3.connect(db_path)  # Opens connection
    conn.execute("PRAGMA foreign_keys = ON;")  # Enables foreign keys
    with open(sql_path, "r", encoding="utf-8") as f:  # Opens SQL file
        sql_script = f.read()  # Reads SQL content
    conn.executescript(sql_script)  # Runs SQL commands
    conn.commit()  # Saves changes
    try:  # Protection block
        ensure_students_columns(conn)  # Adds missing columns
    except sqlite3.Error:  # If error occurs
        conn.commit()  # Save what worked
    conn.close()  # Closes connection


# SERVICE WORKER ROUTE - This is the critical fix
@app.route("/service-worker.js")  # Route for service worker at root
def service_worker():  # Function to serve the service worker file
    return send_from_directory(
        "static", "service-worker.js"
    )  # Serves from static folder


@app.route("/")  # Homepage route
def home():  # Homepage function
    conn = get_db()  # Connects to database
    tutors = conn.execute("SELECT * FROM tutors").fetchall()  # Gets tutors
    conn.close()  # Closes connection
    return render_template("web1/index.html", tutors=tutors)  # Renders page


@app.route("/about")  # About page route
def about():  # About page function
    conn = get_db()  # Connects to database
    tutors = conn.execute("SELECT * FROM tutors").fetchall()  # Gets tutors
    conn.close()  # Closes connection
    return render_template("web1/about.html", tutors=tutors)  # Renders page


@app.route("/account")  # Account page route
def account():  # Account page function
    return render_template("web1/account.html")  # Renders form


@app.route("/class", methods=["GET", "POST"])  # Class selection route
def select_class():  # Class selection function
    if request.method == "GET":  # If just visiting
        conn = get_db()  # Connect to database
        courses = conn.execute("SELECT * FROM courses").fetchall()  # Get courses
        conn.close()  # Close connection
        return render_template(
            "web1/class.html",
            courses=courses,
            fullname="",
            email="",
            username="",
            password="",
        )  # Show page with empty values

    fullname = request.form.get("fullname")  # Gets student name
    email = request.form.get("email")  # Gets email
    username = request.form.get("username")  # Gets username
    password = request.form.get("password")  # Gets password

    conn = get_db()  # Connect to database
    existing_user = conn.execute(
        "SELECT student_id FROM students WHERE username = ?", (username,)
    ).fetchone()  # Check for duplicate
    if existing_user:  # If username taken
        conn.close()  # Close connection
        return render_template("web1/account.html", error="Username already exists.")

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")  # Hash password
    courses = conn.execute("SELECT * FROM courses").fetchall()  # Get courses
    conn.close()  # Close connection

    return render_template(
        "web1/class.html",
        courses=courses,
        fullname=fullname,
        email=email,
        username=username,
        password=pw_hash,
    )  # Render class page


@app.route("/quiz", methods=["POST"])  # Quiz route
def quiz():  # Quiz function
    data = request.form  # Gets form data
    conn = get_db()  # Connects to database
    query = """
        SELECT tutors.tutor_id AS tutor_id,
               tutors.full_name AS full_name,
               GROUP_CONCAT(traits.trait_name, ", ") AS traits
        FROM tutors
        JOIN Tutor_traits ON tutors.tutor_id = Tutor_traits.tutor_id
        JOIN traits ON Tutor_traits.trait_id = traits.trait_id
        GROUP BY tutors.tutor_id;
    """  # SQL to get tutors with traits
    tutors = conn.execute(query).fetchall()  # Runs query
    traits = conn.execute("SELECT * FROM traits").fetchall()  # Gets traits
    conn.close()  # Closes connection
    return render_template(
        "web1/quiz.html", tutors=tutors, traits=traits, **data
    )  # Renders page


@app.route("/final", methods=["POST"])  # Final page route
def final():  # Final page function
    name = request.form.get("fullname")  # Gets name
    email = request.form.get("email")  # Gets email
    user = request.form.get("username")  # Gets username
    pw = request.form.get("password")  # Gets hashed password
    c_id = request.form.get("course_id")  # Gets course ID
    time = request.form.get("time")  # Gets time slot
    t_id = request.form.get("selected_tutor_id")  # Gets tutor ID

    conn = get_db()  # Connects to database

    # --- THE FIX IS HERE ---
    existing = conn.execute(
        "SELECT student_id FROM students WHERE username = ?", (user,)
    ).fetchone()  # Checks for duplicate

    if existing:  # If username taken
        conn.close()  # Close connection
        # Renders the account page with the error so it looks nice
        return render_template(
            "web1/account.html",
            error="Error: That username was just taken. Please try a different one.",
        )
    # -----------------------

    sql = """
        INSERT INTO students 
        (name, email, username, password_hash, course_id, time_slot, selected_tutor_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """  # Insert SQL
    conn.execute(sql, (name, email, user, pw, c_id, time, t_id))  # Saves student
    conn.commit()  # Commits changes

    c_row = conn.execute(
        "SELECT course_name FROM courses WHERE course_id = ?", (c_id,)
    ).fetchone()  # Gets course name
    t_row = conn.execute(
        "SELECT full_name FROM tutors WHERE tutor_id = ?", (t_id,)
    ).fetchone()  # Gets tutor name
    t_name = t_row["full_name"] if t_row else "Unknown"  # Gets name or default
    conn.close()  # Closes connection

    return render_template(
        "web1/final.html",
        fullname=name,
        email=email,
        username=user,
        course=c_row["course_name"] if c_row else "Unknown",
        time=time,
        selected_tutor=t_name,
    )  # Renders success page


@app.route("/login")  # Login route
def login():  # Login function
    return render_template("web1/login.html")  # Renders login page


@app.route("/view_profile", methods=["POST"])  # Profile route
def view_profile():  # Profile function
    username = request.form.get("username")  # Gets username
    password = request.form.get("password")  # Gets password

    conn = get_db()  # Connects to database
    user_row = conn.execute(
        "SELECT * FROM students WHERE username = ?", (username,)
    ).fetchone()  # Finds user

    if user_row:  # If user exists
        if bcrypt.check_password_hash(
            user_row["password_hash"], password
        ):  # Checks password
            query = """
                SELECT students.*, courses.course_name, tutors.full_name AS tutor_name
                FROM students
                LEFT JOIN courses ON students.course_id = courses.course_id
                LEFT JOIN tutors ON students.selected_tutor_id = tutors.tutor_id
                WHERE students.username = ?
            """  # Gets full profile data
            profile_data = conn.execute(query, (username,)).fetchone()  # Runs query
            conn.close()  # Closes connection
            return render_template(
                "web1/profile.html", user=profile_data
            )  # Shows profile

    conn.close()  # Closes connection
    return "Invalid username or password.", 401  # Returns error


if __name__ == "__main__":  # If running directly
    ensure_database_ready()  # Setup database
    app.run(debug=True)  # Start server
