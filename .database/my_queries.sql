PRAGMA foreign_keys = ON; -- Turns on link safety for the database
CREATE TABLE IF NOT EXISTS Courses ( -- Starts creating the Courses table
course_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the course
course_name TEXT NOT NULL -- The name of the subject
); -- Ends the Courses table
CREATE TABLE IF NOT EXISTS Traits ( -- Starts creating the Traits table
trait_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the trait
trait_name TEXT NOT NULL -- The name of the personality trait
); -- Ends the Traits table
CREATE TABLE IF NOT EXISTS Tutors ( -- Starts creating the Tutors table
tutor_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the tutor
full_name TEXT NOT NULL, -- The tutor's name
photo_url TEXT, -- The name of the image file
bio TEXT -- The biography of the tutor
); -- Ends the Tutors table
CREATE TABLE IF NOT EXISTS Tutor_Traits ( -- Starts the tutor-trait link table
tutor_id INTEGER, -- Stores the tutor ID
trait_id INTEGER, -- Stores the trait ID
PRIMARY KEY (tutor_id, trait_id), -- Sets a combined unique ID
FOREIGN KEY (tutor_id) REFERENCES Tutors(tutor_id), -- Links to Tutors table
FOREIGN KEY (trait_id) REFERENCES Traits(trait_id) -- Links to Traits table (NO COMMA HERE)
); -- Ends the link table
CREATE TABLE IF NOT EXISTS Students ( -- Starts the student registration table
student_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the student
name TEXT NOT NULL, -- The name of the student
email TEXT NOT NULL UNIQUE, -- Unique email address
username TEXT NOT NULL UNIQUE, -- Unique login name
password_hash TEXT NOT NULL, -- The secured password hash
course_id INTEGER, -- Link to the course ID
time_slot TEXT, -- Preferred study time
selected_tutor_id INTEGER, -- Link to the tutor ID
FOREIGN KEY (course_id) REFERENCES Courses(course_id), -- Links to Courses table
FOREIGN KEY (selected_tutor_id) REFERENCES Tutors(tutor_id) -- Links to Tutors table (NO COMMA HERE)
); -- Ends the Students table
INSERT OR IGNORE INTO Courses (course_id, course_name) VALUES (1, 'Maths'), (2, 'English'), (3, 'Science'), (4, 'History'); -- Adds subject data
INSERT OR IGNORE INTO Traits (trait_id, trait_name) VALUES (1, 'Gentle'), (2, 'Strict'), (3, 'Patient'), (4, 'Fun'), (5, 'Expert'); -- Adds trait data
INSERT OR IGNORE INTO Tutors (tutor_id, full_name, photo_url, bio) VALUES (1, 'John Doe', 'john.jpg', 'Maths specialist for visual learners.'); -- Adds John Doe
INSERT OR IGNORE INTO Tutors (tutor_id, full_name, photo_url, bio) VALUES (2, 'Jane Smith', 'jane.jpg', 'English specialist with strict focus.'); -- Adds Jane Smith
INSERT OR IGNORE INTO Tutors (tutor_id, full_name, photo_url, bio) VALUES (3, 'Mike Ross', 'mike.jpg', 'Science is fun and very interactive!'); -- Adds Mike Ross
INSERT OR IGNORE INTO Tutors (tutor_id, full_name, photo_url, bio) VALUES (4, 'Sarah Lee', 'sarah.jpg', 'History buff and exam prep expert.'); -- Adds Sarah Lee
INSERT OR IGNORE INTO Tutor_Traits (tutor_id, trait_id) VALUES (1, 1), (1, 3), (2, 2), (2, 5), (3, 4), (3, 1), (4, 5), (4, 2); -- Links tutors to traits
-- =============================================================
-- BASIC QUERIES (Simple data retrieval for your teacher)
-- =============================================================
SELECT * FROM Courses; -- Shows every column and every row from the subject list
SELECT full_name, bio FROM Tutors; -- Shows only names and bios of teachers (Specific selection)
SELECT * FROM Traits WHERE trait_name = 'Strict'; -- Shows only traits where the name matches 'Strict' (Filtering)
-- =============================================================
-- RELATIONAL QUERIES (Using JOIN to show linked data SE-12-02)
-- =============================================================
SELECT Tutors.full_name, Traits.trait_name FROM Tutors JOIN Tutor_Traits ON Tutors.tutor_id = Tutor_Traits.tutor_id JOIN Traits ON Tutor_Traits.trait_id = Traits.trait_id; -- Links 3 tables to show teacher traits
SELECT Students.name, Courses.course_name FROM Students JOIN Courses ON Students.course_id = Courses.course_id; -- Links students to their chosen subjects