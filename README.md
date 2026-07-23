নিচে আপনার project-এর updated feature অনুযায়ী একই style-এ README দিলাম।

# 🎓 University Management System (UMS)

A Django-based University Management System designed to manage students, teachers, courses, attendance, results, library activities, and other academic operations through separate role-based portals.

This project demonstrates how multiple databases can be integrated and used within a single Django application.

## 📌 Project Objective

The main objective of this project is to learn and demonstrate Django's **Multi-Database Architecture** along with a complete role-based university management system.

Although Django uses **SQLite3** as its default database, this project also integrates:

* MySQL
* PostgreSQL
* MongoDB (NoSQL)

All four databases are used for different modules of the same Django project.

---

## 🗄 Databases Used

| Module                                 | Database        |
| -------------------------------------- | --------------- |
| Student Management                     | MySQL           |
| Teacher Management                     | PostgreSQL      |
| Library Management                     | MongoDB (NoSQL) |
| Authentication and Academic Management | SQLite3         |

---

## 👥 User Roles

The system provides three different user roles:

* Admin
* Student
* Teacher

Users must select their correct role before signing in. After successful authentication, each user is redirected to a separate role-based dashboard.

---

## 🚀 Features

### 🛡️ Admin Portal

* Admin Login
* Dashboard Overview
* Add, Update, Delete, and View Students
* Add, Update, Delete, and View Teachers
* Create Student and Teacher Accounts
* Manage Departments
* Manage Courses
* Assign Courses to Teachers
* Enroll Students in Courses
* Manage Attendance
* Manage Student Results
* Manage Academic Sessions
* Manage Class Routines
* Manage Student Fees
* Manage Notices
* Manage Bus Card Applications
* Manage Library Books and Borrowing Records
* Reset User Passwords

### 👨‍🎓 Student Management — MySQL

* Student Login
* View Student Dashboard
* View and Update Personal Profile
* Register for Available Courses
* Withdraw from Registered Courses
* View Attendance Records
* View Academic Results
* View Class Routine
* View Fee Information
* View University Notices
* Browse Library Books
* Borrow and Return Books
* View Borrowing History
* Apply for a Bus Card
* Track Bus Card Application Status
* Change Password
* Search Students by Student ID
* Filter Students by Department

### 👨‍🏫 Teacher Management — PostgreSQL

* Teacher Login
* View Teacher Dashboard
* View and Update Personal Profile
* View Courses Assigned by Admin
* View Students Enrolled in Assigned Courses
* Take Student Attendance
* Update Attendance Records
* Enter Student Assessment Results
* Update Student Results
* View Teaching Routine
* View University Notices
* Browse Library Books
* Borrow and Return Books
* Change Password
* Search Teachers by Teacher ID

### 📚 Library Management — MongoDB

* Add Books
* Update Book Information
* Delete Books
* View Book List
* Search Available Books
* Issue Books to Students and Teachers
* Return Borrowed Books
* Maintain Borrowing History
* Track Book Availability
* Prevent Duplicate Active Book Loans

### 📖 Academic Management — SQLite3

* Department Management
* Course Management
* Teacher Course Assignment
* Student Course Enrollment
* Attendance Management
* Result Management
* Academic Session Management
* Routine Management
* Fee Management
* Notice Management
* Bus Card Application Management
* User Authentication
* Role-Based Access Control

---

## 🔐 Role-Based Login System

The login page contains three role options:

* Student
* Teacher
* Admin

Users must select the correct role before submitting their login credentials.

The system verifies the selected role and redirects the user to the appropriate dashboard.

A Student cannot access the Teacher or Admin portal, and a Teacher cannot access the Admin or Student portal without proper permission.

---

## 🔀 Multi-Database Architecture

This project uses multiple databases for different applications.

* Student application → MySQL
* Teacher application → PostgreSQL
* Library application → MongoDB
* Default Django and Academic applications → SQLite3

Django's custom **Database Router** routes Student application queries to MySQL and Teacher application queries to PostgreSQL.

MongoDB is integrated separately using **PyMongo** for Library Management.

SQLite3 is used for Django authentication, academic records, attendance, results, course assignments, fees, routines, notices, and other default Django tables.

---

## ⚙️ Technologies Used

* Python
* Django 5
* Django ORM
* SQLite3
* MySQL
* PostgreSQL
* MongoDB
* PyMongo
* HTML5
* CSS3
* JavaScript
* Bootstrap 5
* Session Authentication
* Git and GitHub

---

## 📂 Project Structure

```text
UMS
│
├── accounts/
├── academic/
├── student/
├── teacher/
├── library/
├── home/
├── database/
├── templates/
├── static/
├── sms_project/
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

## ▶️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Ishtiyaqalam9/UniCore-UMS-Project.git
```

### 2. Go to the Project Directory

```bash
cd UMS-project-Using-MySQL-PostgreSQL-NoSQL
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🛠️ Database Setup

Before running the project, make sure MySQL, PostgreSQL, and MongoDB services are running.

### MySQL Database

Create the Student database:

```sql
CREATE DATABASE student;
```

### PostgreSQL Database

Create the Teacher database:

```sql
CREATE DATABASE teacher;
```

### MongoDB Database

MongoDB automatically creates the following database when Library data is first inserted:

```text
library_db
```

### SQLite3 Database

SQLite3 is used as the default Django database.

The database file is:

```text
db.sqlite3
```

---

## 🔄 Run Database Migrations

Run the default SQLite3 migrations:

```bash
python manage.py migrate
```

Run MySQL migrations:

```bash
python manage.py migrate --database=mysql
```

Run PostgreSQL migrations:

```bash
python manage.py migrate --database=postgres
```

MongoDB does not require Django migrations because it is managed through PyMongo.

---

## 👤 Create Admin Account

Create a Django superuser:

```bash
python manage.py createsuperuser
```

Enter the required username, email address, and password.

---

## ▶️ Run the Project

```bash
python manage.py runserver
```

Open the following link in your browser:

```text
http://127.0.0.1:8000/
```

Select the appropriate role and sign in.

---

## 👨‍🏫 Assigning Courses to Teachers

An Admin can assign courses to Teachers from:

```text
Teacher Management → Assign Course
```

or:

```text
Academic → Assignments
```

The Admin must select:

* Teacher
* Course
* Academic Year

After the assignment is saved, the course appears in the Teacher portal.

The Teacher can then view enrolled Students, take attendance, and manage results for the assigned course.

---

## 🔒 Security Features

* Secure Password Hashing
* Role-Based Authentication
* Role-Based Authorization
* CSRF Protection
* Session Authentication
* Restricted Admin, Student, and Teacher Portals
* Server-Side Form Validation
* Duplicate Course Registration Prevention
* Teacher Access Limited to Assigned Courses
* Student Access Limited to Personal Records
* Protected Administrative Operations

---

## 📚 What I Learned

* Django Multi-Database Configuration
* Custom Database Router
* SQLite3 Integration
* MySQL Integration
* PostgreSQL Integration
* MongoDB Integration Using PyMongo
* Role-Based Login System
* Role-Based Access Control
* CRUD Operations
* Course Assignment System
* Student Course Enrollment
* Attendance Management
* Result Management
* Django Template Engine
* Bootstrap 5
* Session Authentication
* Django Project Structure
* Git and GitHub

---

## 🔮 Future Improvements

* REST API
* Mobile Application
* Online Payment Integration
* Email and SMS Notifications
* Guardian Portal
* Hostel Management
* Payroll Management
* Advanced Dashboard Analytics
* Downloadable Transcripts
* PDF Report Generation
* Docker Support
* Cloud Deployment

---

## 👨‍💻 Author

**Ishtiyaq Alam**

Department of Computer Science and Engineering (CSE)

Bangladesh Army International University of Science and Technology (BAIUST)

GitHub: [https://github.com/Ishtiyaqalam9](https://github.com/Ishtiyaqalam9)

---

⭐ If you found this project helpful, feel free to star the repository.
