PRAGMA foreign_keys = ON; -- Turns on link safety for the database

BEGIN TRANSACTION; 
    -- 1. Create Courses Table
    CREATE TABLE IF NOT EXISTS courses ( 
    course_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    course_name TEXT NOT NULL 
    ); 

    -- 2. Create Traits Table
    CREATE TABLE IF NOT EXISTS traits ( 
    trait_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    trait_name TEXT NOT NULL 
    ); 

    -- 3. Create Tutors Table (UPDATED with email and atar)
    CREATE TABLE IF NOT EXISTS tutors ( 
    tutor_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    full_name TEXT NOT NULL, 
    photo_url TEXT, 
    bio TEXT,
    email TEXT, -- Added for contact info
    atar REAL    -- Added for stats
    ); 

    -- 4. Create Link Table
    CREATE TABLE IF NOT EXISTS tutor_traits ( 
    tutor_id INTEGER, 
    trait_id INTEGER, 
    PRIMARY KEY (tutor_id, trait_id), 
    FOREIGN KEY (tutor_id) REFERENCES tutors(tutor_id), 
    FOREIGN KEY (trait_id) REFERENCES traits(trait_id) 
    ); 

    -- 5. Create Students Table
    CREATE TABLE IF NOT EXISTS students ( 
    student_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL, 
    email TEXT NOT NULL UNIQUE, 
    username TEXT NOT NULL UNIQUE, 
    password_hash TEXT NOT NULL, 
    course_id INTEGER, 
    time_slot TEXT, 
    selected_tutor_id INTEGER, 
    FOREIGN KEY (course_id) REFERENCES courses(course_id), 
    FOREIGN KEY (selected_tutor_id) REFERENCES tutors(tutor_id) 
    ); 

    -- DATA INSERTION
    INSERT OR IGNORE INTO courses (course_id, course_name) VALUES (1, 'Maths'), (2, 'English'), (3, 'Science'), (4, 'History'); 
    INSERT OR IGNORE INTO traits (trait_id, trait_name) VALUES (1, 'Gentle'), (2, 'Strict'), (3, 'Patient'), (4, 'Fun'), (5, 'Expert'); 

    -- TUTOR DATA (Now including email and ATAR)
    INSERT OR IGNORE INTO tutors (tutor_id, full_name, photo_url, bio, email, atar) VALUES 
    (1, 'John Doe', 'john.jpg', 'Maths specialist for visual learners.', 'john.d@tutors.com', 99.10),
    (2, 'Jane Smith', 'jane.jpg', 'English specialist with strict focus.', 'jane.s@tutors.com', 98.50),
    (3, 'Mike Ross', 'mike.jpg', 'Science is fun and very interactive!', 'mike.r@tutors.com', 97.40),
    (4, 'Sarah Lee', 'sarah.jpg', 'History buff and exam prep expert.', 'sarah.l@tutors.com', 99.20),
    (5, 'Emily Chen', 'emily.jpg', 'Chemistry expert helping you understand formulas.', 'emily.c@tutors.com', 98.80),
    (6, 'David Wilson', 'david.jpg', 'Physics specialist with a focus on motion.', 'david.w@tutors.com', 99.00),
    (7, 'Jessica Taylor', 'jessica.jpg', 'Biology tutor who makes anatomy easy.', 'jessica.t@tutors.com', 97.90),
    (8, 'Robert Brown', 'robert.jpg', 'Economics guide for HSC success.', 'robert.b@tutors.com', 98.40),
    (9, 'Chris Evans', 'chris.jpg', 'HSC Advanced and Extension Maths expert.', 'c.evans@tutors.com', 99.95); -- NEW MATHS TUTOR

    -- LINKING TRAITS
    INSERT OR IGNORE INTO tutor_traits (tutor_id, trait_id) VALUES 
    (1, 1), (1, 3), (2, 2), (2, 5), (3, 4), (3, 1), (4, 5), (4, 2), 
    (5, 5), (5, 3), (6, 2), (6, 5), (7, 1), (7, 4), (8, 3), (9, 5);
COMMIT;

--test queries:-- 
SELECT * FROM courses; -- Shows every column and every row from the subject list
SELECT full_name, bio FROM tutors; -- Shows only names and bios of teachers (Specific selection)
SELECT * FROM traits WHERE trait_name = 'Strict'; -- Shows only traits where the name matches 'Strict' (Filtering)

--relational queries--
SELECT tutors.full_name, traits.trait_name FROM tutors JOIN tutor_traits ON tutors.tutor_id = tutor_traits.tutor_id JOIN traits ON tutor_traits.trait_id = traits.trait_id; -- Links 3 tables to show teacher traits
SELECT students.name, courses.course_name FROM students JOIN courses ON students.course_id = courses.course_id; -- Links students to their chosen subjects