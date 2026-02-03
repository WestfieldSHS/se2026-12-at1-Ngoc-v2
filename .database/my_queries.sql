PRAGMA foreign_keys = ON; -- Turns on link safety for the database
--add a group by and order by--
BEGIN TRANSACTION;  --as long as everything is good it will sent the update-- 
    CREATE TABLE IF NOT EXISTS courses ( -- Starts creating the courses table
    course_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the course
    course_name TEXT NOT NULL -- The name of the subject
    ); -- Ends the courses table
    CREATE TABLE IF NOT EXISTS traits ( -- Starts creating the traits table
    trait_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the trait
    trait_name TEXT NOT NULL -- The name of the personality trait
    ); -- Ends the traits table
    CREATE TABLE IF NOT EXISTS tutors ( -- Starts creating the tutors table
    tutor_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the tutor
    full_name TEXT NOT NULL, -- The tutor's name
    photo_url TEXT, -- The name of the image file
    bio TEXT -- The biography of the tutor
    ); -- Ends the tutors table
    CREATE TABLE IF NOT EXISTS tutor_traits ( -- Starts the tutor-trait link table
    tutor_id INTEGER, -- Stores the tutor ID
    trait_id INTEGER, -- Stores the trait ID
    PRIMARY KEY (tutor_id, trait_id), -- Sets a combined unique ID
    FOREIGN KEY (tutor_id) REFERENCES tutors(tutor_id), -- Links to tutors table
    FOREIGN KEY (trait_id) REFERENCES traits(trait_id) -- Links to traits table (NO COMMA HERE)
    ); -- Ends the link table
    CREATE TABLE IF NOT EXISTS students ( -- Starts the student registration table
    student_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the student
    name TEXT NOT NULL, -- The name of the student
    email TEXT NOT NULL UNIQUE, -- Unique email address
    username TEXT NOT NULL UNIQUE, -- Unique login name
    password_hash TEXT NOT NULL, -- The secured password hash
    course_id INTEGER, -- Link to the course ID
    time_slot TEXT, -- Preferred study time
    selected_tutor_id INTEGER, -- Link to the tutor ID
    FOREIGN KEY (course_id) REFERENCES courses(course_id), -- Links to courses table
    FOREIGN KEY (selected_tutor_id) REFERENCES tutors(tutor_id) -- Links to tutors table (NO COMMA HERE)
    ); -- Ends the students table
    INSERT OR IGNORE INTO courses (course_id, course_name) VALUES (1, 'Maths'), (2, 'English'), (3, 'Science'), (4, 'History'); -- Adds subject data
    INSERT OR IGNORE INTO traits (trait_id, trait_name) VALUES (1, 'Gentle'), (2, 'Strict'), (3, 'Patient'), (4, 'Fun'), (5, 'Expert'); -- Adds trait data
    INSERT OR IGNORE INTO tutors (tutor_id, full_name, photo_url, bio) VALUES (1, 'John Doe', 'john.jpg', 'Maths specialist for visual learners.'); -- Adds John Doe
    INSERT OR IGNORE INTO tutors (tutor_id, full_name, photo_url, bio) VALUES (2, 'Jane Smith', 'jane.jpg', 'English specialist with strict focus.'); -- Adds Jane Smith
    INSERT OR IGNORE INTO tutors (tutor_id, full_name, photo_url, bio) VALUES (3, 'Mike Ross', 'mike.jpg', 'Science is fun and very interactive!'); -- Adds Mike Ross
    INSERT OR IGNORE INTO tutors (tutor_id, full_name, photo_url, bio) VALUES (4, 'Sarah Lee', 'sarah.jpg', 'History buff and exam prep expert.'); -- Adds Sarah Lee
    INSERT OR IGNORE INTO tutor_traits (tutor_id, trait_id) VALUES (1, 1), (1, 3), (2, 2), (2, 5), (3, 4), (3, 1), (4, 5), (4, 2); -- Links tutors to traits
COMMIT;

--test queries:-- 
SELECT * FROM courses; -- Shows every column and every row from the subject list
SELECT full_name, bio FROM tutors; -- Shows only names and bios of teachers (Specific selection)
SELECT * FROM traits WHERE trait_name = 'Strict'; -- Shows only traits where the name matches 'Strict' (Filtering)

--relational queries--
SELECT tutors.full_name, traits.trait_name FROM tutors JOIN tutor_traits ON tutors.tutor_id = tutor_traits.tutor_id JOIN traits ON tutor_traits.trait_id = traits.trait_id; -- Links 3 tables to show teacher traits
SELECT students.name, courses.course_name FROM students JOIN courses ON students.course_id = courses.course_id; -- Links students to their chosen subjects