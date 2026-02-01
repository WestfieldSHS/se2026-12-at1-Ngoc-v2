import sqlite3 # Imports the standard library for interacting with SQL database files
import os # Imports the operating system module to manage file and folder paths
from flask import Flask, render_template, request # Imports the core Flask framework tools for routing and forms
from flask_bcrypt import Bcrypt # Imports the security library for professional password hashing

app = Flask(__name__) # Initialises the main Flask web application instance
bcrypt = Bcrypt(app) # Links the Bcrypt security scrambler to the application for encryption

def get_db(): # Defines a reusable function to establish a secure database connection
    base_dir = os.path.abspath(os.path.dirname(__file__)) # Finds the exact absolute path of the current folder
    db_path = os.path.join(base_dir, '.database', 'data_source.db') # Builds the correct path to the hidden database file
    try: # Attempts to open the database to check for system errors (SE-12-08)
        conn = sqlite3.connect(db_path) # Physically opens the connection to the .db file
        conn.row_factory = sqlite3.Row # Configures the database to return results as easy-to-read dictionaries
        return conn # Returns the active connection for the routes to use
    except sqlite3.Error: # Runs if the database file is missing or corrupted
        return None # Returns nothing so the routes can handle the error gracefully

@app.route('/') # Sets the main landing page URL path
def home(): # Starts the function to display the home screen
    conn = get_db() # Connects to the database securely
    tutors = conn.execute('SELECT * FROM Tutors').fetchall() # Fetches the full list of tutors for display
    conn.close() # Closes the connection to keep the database healthy
    return render_template('web1/index.html', tutors=tutors) # Loads the index page with the tutor data

@app.route('/about') # Sets the path for the tutor biography page
def about(): # Starts the function to fetch and show tutor bios
    conn = get_db() # Establishes a connection to the data source
    tutors = conn.execute('SELECT * FROM Tutors').fetchall() # Retrieves every tutor's bio and photo URL
    conn.close() # Disconnects from the database to save memory
    return render_template('web1/about.html', tutors=tutors) # Renders the about us page for the user

@app.route('/account') # Sets the path for the initial account creation form
def account(): # Starts the registration entry function
    return render_template('web1/account.html') # Displays the account.html file to the user

@app.route('/class', methods=['GET', 'POST']) # Defines the step 2 path and allows form data submission
def select_class(): # Starts the validation and class selection function
    if request.method == 'POST': # Checks if the user actually submitted a form
        fullname = request.form.get('fullname', '') # Gets the student's name from the input field
        email = request.form.get('email', '') # Gets the student's email from the input field
        username = request.form.get('username', '') # Gets the chosen username from the input field
        raw_password = request.form.get('password', '') # Temporarily holds the plain-text password for hashing
        
        # VALIDATION FIX: Ensures no required fields are empty (Usability + Security)
        if not fullname or not email or not username or not raw_password: # Checks for empty inputs
            return "<h1>Error: All fields are required!</h1><a href='/account'>Go back</a>" # Rejects empty data
            
        conn = get_db() # Connects to the database to check for duplicates
        query_check = 'SELECT * FROM Students WHERE username = ? OR email = ?' # Prepares the unique check query
        existing_user = conn.execute(query_check, (username, email)).fetchone() # Executes the duplicate search
        conn.close() # Closes the database immediately after the search
        
        if existing_user: # Evaluates if the username or email is already taken
            return "<h1>Error: Account already exists!</h1><a href='/account'>Try again</a>" # Stops the user here
        
        password_to_pass = bcrypt.generate_password_hash(raw_password).decode('utf-8') # Scrambles password into a hash
    else: # Runs if the page is visited directly without a form submission
        fullname = email = username = password_to_pass = '' # Initialises empty variables to prevent errors
        
    conn = get_db() # Re-opens database to fetch the subject list
    courses = conn.execute('SELECT * FROM Courses').fetchall() # Gets all subjects for the dropdown menu
    conn.close() # Closes the database connection safely
    return render_template('web1/class.html', courses=courses, fullname=fullname, email=email, username=username, password=password_to_pass) # Loads class selection

@app.route('/quiz', methods=['GET', 'POST']) # Defines the step 3 path for tutor selection
def quiz(): # Starts the quiz and trait filtering function
    if request.method == 'POST': # Checks for form data from the previous step
        fullname = request.form.get('fullname', '') # Retrieves the student name from hidden storage
        email = request.form.get('email', '') # Retrieves the email from hidden storage
        username = request.form.get('username', '') # Retrieves the username from hidden storage
        password = request.form.get('password', '') # Retrieves the hashed password from hidden storage
        course_id = request.form.get('course_id', '') # Retrieves the selected course ID number
        time = request.form.get('time', '') # Retrieves the selected study time slot
    else: # Handles GET requests for direct access
        fullname = email = username = password = course_id = time = '' # Sets blank values
    conn = get_db() # Connects to the relational database source
    # Advanced SQL JOIN to link Tutors and Traits tables together for display (SE-12-02)
    query = 'SELECT Tutors.full_name, GROUP_CONCAT(Traits.trait_name, ", ") FROM Tutors JOIN Tutor_Traits ON Tutors.tutor_id = Tutor_Traits.tutor_id JOIN Traits ON Tutor_Traits.trait_id = Traits.trait_id GROUP BY Tutors.tutor_id'
    tutors = conn.execute(query).fetchall() # Executes the multi-table JOIN query
    all_traits = conn.execute('SELECT * FROM Traits').fetchall() # Fetches all possible traits for the filter
    conn.close() # Closes the database connection
    return render_template('web1/quiz.html', tutors=tutors, traits=all_traits, fullname=fullname, email=email, username=username, password=password, course=course_id, time=time) # Loads the quiz

@app.route('/final', methods=['GET', 'POST']) # Defines the final path to complete the registration
def final(): # Starts the final processing and saving function
    if request.method == 'POST': # Processes the final tutor selection data
        fullname = request.form.get('fullname', '') # Final retrieval of name
        email = request.form.get('email', '') # Final retrieval of email
        username = request.form.get('username', '') # Final retrieval of username
        password_hashed = request.form.get('password', '') # Final retrieval of the secure hash
        course_id = request.form.get('course_id', '') # Final retrieval of course ID
        time_slot = request.form.get('time_slot', '') # Final retrieval of time
        selected_tutor_id = request.form.get('selected_tutor', '') # Final retrieval of tutor ID (Relational link)
    else: # Defaults for unexpected page access
        fullname = email = username = password_hashed = course_id = time_slot = selected_tutor_id = '' 
    
    conn = get_db() # Connects to the database to save the record
    course_query = 'SELECT course_name FROM Courses WHERE course_id = ?' # Query to find name from ID
    course_row = conn.execute(course_query, (course_id,)).fetchone() # Fetches the course name string
    course_name = course_row['course_name'] if course_row else "N/A" # Sets name or N/A
    
    # Prepares the final secure INSERT statement for the Students table
    insert_sql = 'INSERT INTO Students (name, email, username, password_hash, course_id, time_slot, selected_tutor_id) VALUES (?, ?, ?, ?, ?, ?, ?)'
    data_tuple = (fullname, email, username, password_hashed, course_id, time_slot, selected_tutor_id) # Bundles the final data
    
    try: # Starts an error-handling block to catch database issues (SE-12-08)
        conn.execute(insert_sql, data_tuple) # Executes the save command
        conn.commit() # Confirms the transaction to the database file
    except sqlite3.Error: # Runs if a database conflict or crash occurs
        conn.close() # Closes connection to prevent file locking
        return "<h1>Error: Database could not save your data!</h1><a href='/account'>Try again</a>" # Error UI
    
    conn.close() # Final closure of the database connection
    # Renders the success page and displays the user's registered details
    return render_template('web1/final.html', fullname=fullname, email=email, username=username, course=course_name, time=time_slot, selected_tutor=selected_tutor_id)

@app.route('/login') # Path for the existing user login screen
def login(): # Login UI function
    return render_template('web1/login.html') # Displays the login portal

@app.route('/view_profile', methods=['POST']) # Path for processing user login requests
def view_profile(): # Authentication and profile retrieval function
    username = request.form.get('username') # Collects username from form
    password = request.form.get('password') # Collects plain-text password for checking
    conn = get_db() # Connects to the relational database
    # Complex JOIN to retrieve student info and their course name simultaneously (SE-12-02)
    query = 'SELECT Students.*, Courses.course_name FROM Students JOIN Courses ON Students.course_id = Courses.course_id WHERE Students.username = ?'
    user = conn.execute(query, (username,)).fetchone() # Fetches the specific student record
    conn.close() # Closes the connection immediately
    # Uses Bcrypt to verify the typed password against the stored digital fingerprint (hash)
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        # Displays the success page using real data from the database
        return render_template('web1/final.html', fullname=user['name'], email=user['email'], username=user['username'], course=user['course_name'], time=user['time_slot'], selected_tutor=user['selected_tutor_id'])
    else: # Handles unsuccessful login attempts
        return "<h1>Login Failed: Invalid credentials</h1><a href='/login'>Try Again</a>" # Simple error message

@app.route('/service-worker.js') # Route to serve the PWA service worker background script
def service_worker(): # Service worker file delivery function
    return app.send_static_file('js/service-worker.js') # Sends the JS file from the static folder

if __name__ == "__main__": # Checks if the file is the main program being executed
    app.run(debug=True) # Starts the local development server with live error reporting