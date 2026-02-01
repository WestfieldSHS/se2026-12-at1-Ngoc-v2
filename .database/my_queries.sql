-- tells SQLite to actually enforce the  Foreign Key rules.
PRAGMA foreign_keys = ON;
-- STEP 1: DATABASE RESET AND CLEANUP
-- These commands ensure that the database starts from a clean state.
-- This prevents "Table Already Exists" errors and ensures old, incorrect schemas don't conflict with our new 2026 structure.

DROP TABLE IF EXISTS Student_Courses; -- Removes old junction tables first to prevent foreign key constraint errors
DROP TABLE IF EXISTS Student_Learning_Styles; -- Clears the relationship table between students and learning styles for a fresh start
DROP TABLE IF EXISTS Tutor_Traits; -- Resetting this junction table allows us to implement the new 'Many Traits per Tutor' logic
DROP TABLE IF EXISTS Students; -- Drops the student table so we can add the 'name' and 'tutor_name' columns correctly
DROP TABLE IF EXISTS Tutors; -- Resets the tutor master list so we can update it from 'first_name/last_name' to 'full_name'
DROP TABLE IF EXISTS Courses; -- Removes the subjects list so we can re-populate it with the official course names
DROP TABLE IF EXISTS Learning_Styles; -- Wipes the learning styles list to ensure no duplicate entries during the update
DROP TABLE IF EXISTS Traits; -- Clears the personality trait list so we can map 'Gentle' and 'Strict' to specific IDs

-- STEP 2: CREATE THE TABLES WITH THE CORRECT ;COLUMNS
CREATE TABLE Courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique number for each subject
    course_name TEXT NOT NULL -- The name of the subject (Maths, English, etc)
); -- Ends Courses table

CREATE TABLE Learning_Styles (
    learning_style_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique number for each style
    style_name TEXT NOT NULL -- Name like Visual, Auditory, or Kinesthetic
); -- Ends Learning_Styles table

CREATE TABLE Traits (
    trait_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique number for each trait
    trait_name TEXT NOT NULL -- Personality name like Gentle, Strict, or Patient
); -- Ends Traits table

CREATE TABLE Tutors (
    tutor_id INTEGER PRIMARY KEY AUTOINCREMENT, -- A unique identifier for each teaching professional
    full_name TEXT NOT NULL, -- The complete name of the tutor displayed on the front-end
    photo_url TEXT, -- THE FIX: Stores the filename of the tutor's image (e.g., 'john.jpg')
    email TEXT, -- Professional contact email for the tutor
    phone TEXT, -- Contact phone number for the tutor
    bio TEXT -- A short biography describing the tutor's expertise
); -- Finalises the Tutor table structure

CREATE TABLE Students (
    -- Unique primary key for every student record
    student_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    -- Stores the full legal name of the student
    name TEXT NOT NULL, 
    -- Stores the email and ensures no two students use the same one (Data Integrity)
    email TEXT NOT NULL UNIQUE, 
    -- Stores the unique login name for the student account
    username TEXT NOT NULL UNIQUE, 
    -- Stores the scrambled Bcrypt hash (never the real password) for security (SE-12-07)
    password_hash TEXT NOT NULL, 
    -- Stores the ID number of the course (Relational Link)
    course_id INTEGER, 
    -- Stores the preferred time slot for classes
    time_slot TEXT, 
    -- THE FIX: Stores the tutor's ID number instead of their name for better relational design
    selected_tutor_id INTEGER, 
    -- Creates a structural link to the Courses table
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    -- THE FIX: Creates a structural link to the Tutors table
    FOREIGN KEY (selected_tutor_id) REFERENCES Tutors(tutor_id)
); -- Ends

-- STEP 3: CREATE THE LINK TABLE FOR MANY-TO-MANY RELATIONSHIPS (SE-12-03)
CREATE TABLE Tutor_Traits (
    tutor_id INTEGER, -- Connects to a specific tutor
    trait_id INTEGER, -- Connects to a specific trait
    PRIMARY KEY (tutor_id, trait_id), -- Ensures a tutor cannot have the same trait twice
    FOREIGN KEY (tutor_id) REFERENCES Tutors(tutor_id), -- Links back to Tutors table
    FOREIGN KEY (trait_id) REFERENCES Traits(trait_id) -- Links back to Traits table
); -- Ends link table

-- STEP 4: INSERT DATA (ADDING MORE TUTORS AND MULTIPLE TRAITS)
INSERT INTO Courses (course_name) VALUES ('Maths'), ('English'), ('Science'), ('History'); -- Adds subjects
INSERT INTO Learning_Styles (style_name) VALUES ('Visual'), ('Auditory'), ('Kinesthetic'); -- Adds styles
INSERT INTO Traits (trait_name) VALUES ('Gentle'), ('Strict'), ('Patient'), ('Fun'), ('Expert'); -- Adds traits

-- INSERTING 4 TUTORS
INSERT INTO Tutors (full_name, photo_url, email, phone, bio) VALUES ('John Doe', 'john.jpg', 'john@ex.com', '041', 'Maths specialist for visual learners.'); -- Record 1
INSERT INTO Tutors (full_name, photo_url, email, phone, bio) VALUES ('Jane Smith', 'jane.jpg', 'jane@ex.com', '042', 'English specialist with strict focus.'); -- Record 2
INSERT INTO Tutors (full_name, photo_url, email, phone, bio) VALUES ('Mike Ross', 'mike.jpg', 'mike@ex.com', '043', 'Science is fun and very interactive!'); -- Record 3
INSERT INTO Tutors (full_name, photo_url, email, phone, bio) VALUES ('Sarah Lee', 'sarah.jpg', 'sarah@ex.com', '044', 'History buff and exam prep expert.'); -- Record 4

-- LINKING TUTORS TO MULTIPLE TRAITS (ONE TUTOR -> MANY TRAITS)
INSERT INTO Tutor_Traits (tutor_id, trait_id) VALUES (1, 1), (1, 3); -- John is Gentle (1) and Patient (3)
INSERT INTO Tutor_Traits (tutor_id, trait_id) VALUES (2, 2), (2, 5); -- Jane is Strict (2) and Expert (5)
INSERT INTO Tutor_Traits (tutor_id, trait_id) VALUES (3, 4), (3, 1); -- Mike is Fun (4) and Gentle (1)
INSERT INTO Tutor_Traits (tutor_id, trait_id) VALUES (4, 5), (4, 2); -- Sarah is Expert (5) and Strict (2)