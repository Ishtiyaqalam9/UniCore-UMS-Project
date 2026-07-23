UniCore University Management System

UniCore is a role-based University Management System developed with Django. It provides separate portals for administrators, students, and teachers to manage academic activities, attendance, results, course registration, library services, fees, routines, notices, and bus card applications.

A key feature of this project is its multi-database architecture. UniCore uses four different database systems—SQLite, MySQL, PostgreSQL, and MongoDB—within one Django application.

Key Features

Administrator

Manage student and teacher profiles

Create Student and Teacher user accounts

Manage departments, courses, academic sessions, and notices

Assign courses to teachers

Enroll students in courses

Manage attendance and academic results

Manage class routines and student fees

Review and process bus card applications

Manage library books and borrowing records

Reset user passwords and control account access

Student

Sign in through the Student login option

View personal profile and dashboard

Register for available courses

Withdraw from registered courses when allowed

View attendance and academic results

View class routine, fees, and notices

Browse and borrow available library books

Return borrowed books and view borrowing history

Apply for a bus card and track application status

Change account password

Teacher

Sign in through the Teacher login option

View personal profile and dashboard

View courses assigned by the administrator

View students enrolled in assigned courses

Record and update date-wise attendance

Enter and update student assessment results

View teaching routine and notices

Browse, borrow, and return library books

Change account password

Role-Based Login

The login page includes three role options:

Student

Teacher

Admin

A user must select the correct role before signing in. The system verifies the selected role and redirects the user to the appropriate portal. A user cannot access another role's portal without the required permission.

Four-Database Architecture

UniCore uses four databases for different parts of the system.

Database

Default Database Name

Main Responsibility

SQLite

db.sqlite3

Django authentication, accounts, academic records, course assignments, attendance, results, fees, routines, notices, bus card applications, and Django core tables

MySQL

student

Student profile information and student-specific records

PostgreSQL

teacher

Teacher profile information and teacher-specific records

MongoDB

library_db

Library books, book issue records, return records, and borrowing history

Database Routing

Django's custom database router sends Student app operations to MySQL and Teacher app operations to PostgreSQL. Other relational Django apps use SQLite as the default database.

MongoDB is connected separately through PyMongo for the Library module.

The application avoids unsafe foreign-key relationships across different databases. Stable Student and Teacher reference IDs are used to connect related information between modules.

Technology Stack

Python

Django 5.2

HTML5

CSS3

JavaScript

SQLite

MySQL

PostgreSQL

MongoDB

PyMongo

Django ORM

Session Authentication

Project Structure

UniCore_UMS/
├── accounts/          # Login accounts and role-based authorization
├── academic/          # Courses, assignments, attendance, results and other academic modules
├── home/              # Role-specific dashboards and portal pages
├── student/           # Student profiles stored in MySQL
├── teacher/           # Teacher profiles stored in PostgreSQL
├── library/           # Library services stored in MongoDB
├── database/          # MySQL and PostgreSQL database setup files
├── sms_project/       # Django settings, URLs, WSGI and database router
├── static/            # CSS and JavaScript files
├── templates/         # Shared HTML templates
├── db.sqlite3         # Default SQLite database
├── manage.py
└── requirements.txt

System Requirements

Install the following software before running the project:

Python 3.11 or later

MySQL Server

PostgreSQL

MongoDB Community Server

Git

Visual Studio Code or another code editor

Installation

1. Clone the Repository

git clone https://github.com/ishtiyaqalam9/UniCore-UMS-Project.git
cd UniCore-UMS/UniCore_UMS

Replace YOUR_USERNAME with your GitHub username.

2. Create a Virtual Environment

macOS or Linux

python3 -m venv venv
source venv/bin/activate

Windows

python -m venv venv
venv\Scripts\activate

3. Install Dependencies

python -m pip install --upgrade pip
pip install -r requirements.txt

Database Setup

Make sure the MySQL, PostgreSQL, and MongoDB services are running.

MySQL

Create the Student database:

CREATE DATABASE student CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

PostgreSQL

Create the Teacher database:

CREATE DATABASE teacher;

MongoDB

MongoDB automatically creates the library_db database and its collections when the first Library record is saved.

The application uses these MongoDB collections:

books

book_issues

SQLite

No manual database creation is required. Django uses the included db.sqlite3 file or creates it automatically when migrations are run.

Environment Variables

For security, database passwords and secret keys should be configured using environment variables.

Example:

DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_TIME_ZONE=Asia/Dhaka

MYSQL_DATABASE=student
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306

POSTGRES_DATABASE=teacher
POSTGRES_USER=your_postgresql_username
POSTGRES_PASSWORD=your_postgresql_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=library_db

Do not upload real passwords, secret keys, or .env files to a public GitHub repository.

Run Database Migrations

Run migrations separately for the three relational database connections:

python manage.py migrate
python manage.py migrate --database=mysql
python manage.py migrate --database=postgres

MongoDB does not use Django migrations.

Create an Administrator Account

python manage.py createsuperuser

Enter the requested username, email address, and password.

Run the Project

python manage.py runserver --insecure

Open the following address in a browser:

http://127.0.0.1:8000/

Initial Administration Workflow

After signing in as an administrator:

Create departments and courses.

Add Student and Teacher profiles.

Create login accounts for Students and Teachers.

Assign courses to Teachers.

Enroll Students in courses or allow Student self-registration.

Add routines, notices, fee records, and academic information.

Add books to the Library module.

Teacher Course Assignment

An administrator can assign a course to a teacher from either:

Teacher Management → Assign Course

Academic → Assignments

After the assignment is saved, the course appears in the Teacher portal. The teacher can then view enrolled students and record attendance or results for that assigned course.

Security Features

Django password hashing

CSRF protection

Session-based authentication

Role-based authorization

Restricted Student, Teacher, and Admin portals

Server-side form validation

Duplicate course registration prevention

Attendance and result access restricted to assigned teachers

Student access limited to the student's own records

Main Data Integrity Rules

Unique Student and Teacher reference IDs

Unique department and course codes

Duplicate course registration prevention

One attendance entry per enrollment per date

One result per assessment type

Mark range validation

Automatic grade calculation

Available-book validation before issuing

Duplicate active library-loan prevention

Maximum active-loan validation

Protected administrative operations

Deployment

GitHub stores the source code, but GitHub Pages cannot run a Django backend. Deploy the application through a Django-compatible hosting platform such as Railway, Render, or another Python hosting provider.

For production deployment:

Set DJANGO_DEBUG=0

Configure a secure DJANGO_SECRET_KEY

Configure the public domain in DJANGO_ALLOWED_HOSTS

Use environment variables for all credentials

Configure persistent database services

Collect and serve static files properly

Use a production WSGI server such as Gunicorn

Future Improvements

Online payment integration

Email and SMS notifications

Downloadable transcripts and certificates

Guardian portal

Hostel management

Payroll management

Transport route tracking

REST API and mobile application

Advanced reports and analytics

Project Purpose

This project was developed as an academic University Management System demonstration. It shows how Django can integrate multiple database technologies in a single role-based web application.

License

This project is intended for educational and academic use.
