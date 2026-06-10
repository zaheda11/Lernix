-- LERNIX SQLite Schema

-- Drop tables if they exist to allow clean recreations (only if forced)
DROP TABLE IF EXISTS student_quizzes;
DROP TABLE IF EXISTS student_tasks;
DROP TABLE IF EXISTS student_curricula;
DROP TABLE IF EXISTS feedbacks;
DROP TABLE IF EXISTS download_history;
DROP TABLE IF EXISTS learning_plans;
DROP TABLE IF EXISTS curricula;
DROP TABLE IF EXISTS users;

-- Users Table (with Year, Branch, Roll Number, and Subscriptions)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT CHECK(role IN ('student', 'educator', 'admin')) NOT NULL DEFAULT 'student',
    year TEXT,                   -- '1st Year', '2nd Year', etc. (Student only)
    branch TEXT,                 -- 'Computer Science', etc. (Student only)
    roll_no TEXT,                -- University Roll No (Student only)
    subscription_tier TEXT CHECK(subscription_tier IN ('free', 'monthly', 'annual')) NOT NULL DEFAULT 'free',
    generation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Curricula Table (with manual satisfaction_score)
CREATE TABLE curricula (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    field_of_study TEXT NOT NULL,
    duration_semesters INTEGER NOT NULL,
    raw_json TEXT NOT NULL,
    satisfaction_score INTEGER CHECK(satisfaction_score BETWEEN 1 AND 5) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Student-Curricula Opt-in Linkage
CREATE TABLE student_curricula (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    curriculum_id INTEGER NOT NULL,
    opted_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(curriculum_id) REFERENCES curricula(id) ON DELETE CASCADE,
    UNIQUE(student_id, curriculum_id)
);

-- Student Study Plan Checkboxes Progress
CREATE TABLE student_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    task_index INTEGER NOT NULL,
    completed INTEGER DEFAULT 0, -- 0 for False, 1 for True
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(plan_id) REFERENCES learning_plans(id) ON DELETE CASCADE,
    UNIQUE(student_id, plan_id, week_number, task_index)
);

-- Student Quiz Submissions Scores
CREATE TABLE student_quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    curriculum_id INTEGER NOT NULL,
    course_code TEXT NOT NULL,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    wrong_answers_explanation TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(curriculum_id) REFERENCES curricula(id) ON DELETE CASCADE
);

-- Saved Student Learning/Revision Plans
CREATE TABLE learning_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curriculum_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    plan_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(curriculum_id) REFERENCES curricula(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Export and Download History Logs
CREATE TABLE download_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    curriculum_id INTEGER NOT NULL,
    export_format TEXT NOT NULL, -- 'pdf', 'json', 'csv'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(curriculum_id) REFERENCES curricula(id) ON DELETE CASCADE
);

-- User Feedback Table
CREATE TABLE feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comments TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
