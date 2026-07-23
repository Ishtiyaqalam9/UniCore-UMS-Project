# University Management System — Project Report

## 1. Project overview

UniCore is a role-based University Management System built with Django. It gives administrators, students, and teachers separate workspaces for managing everyday academic and campus services through a responsive web interface.

## 2. User roles

### Administrator

- Manage student and teacher profiles
- Manage departments, courses, academic sessions, and notices
- Enroll students and assign teachers when administrative action is required
- Review bus card applications
- Manage library books and issue/return records
- Create and manage Student and Teacher login accounts

### Student

- View personal profile and dashboard
- Register for available courses and withdraw when permitted
- View attendance, results, fees, routine, and notices
- Apply for a bus card and track its status
- Browse the library catalog, issue an available book, view current loans, and return books

### Teacher

- View personal profile and assigned courses
- View enrolled students for an assigned course
- Record and update attendance
- Enter and update assessment results
- View routine and notices
- Browse the library catalog, issue an available book, view current loans, and return books

## 3. Interface design

Authenticated users receive a role-specific left sidebar. Every major function opens on a dedicated page so users can understand where they are and return to related tasks quickly. The sidebar collapses into a mobile menu on small screens. Dashboard cards, searchable tables, status badges, confirmation pages, empty states, and feedback messages improve usability.

## 4. Main modules

- Student and teacher profile management
- Login accounts and role-based authorization
- Department and course management
- Course registration and teacher assignment
- Attendance management
- Result and grade management
- Fee records
- Class routine
- Notices
- Bus card applications and administrative review
- Library catalog, self-service issue, return, and borrowing history

## 5. Data architecture

Student records remain in the configured Student data source, Teacher records remain in the configured Teacher data source, Library books and circulation records remain in the configured Library data source, and the core academic and authentication modules use Django's default data source. Stable reference IDs connect records across modules without unsafe cross-database foreign keys.

## 6. Important relationships

- Department one-to-many Course
- Course one-to-many Enrollment
- Course one-to-many Teacher Assignment
- Enrollment one-to-many Attendance
- Enrollment one-to-many Result
- Course one-to-many Class Routine
- Student reference one-to-many Enrollment, Fee, Bus Card Application, and Library Loan
- Teacher reference one-to-many Course Assignment and Library Loan
- Book one-to-many Library Loan

## 7. Validation and integrity controls

- Unique student and employee reference IDs
- Unique department and course codes
- Duplicate course registration prevention
- One attendance record per enrollment and date
- One result per enrollment and assessment type
- Mark range validation and automatic grade calculation
- Automatic fee balance and payment status
- One bus card application per student and academic year
- A maximum of five active library loans per member
- Duplicate active loan prevention for the same member and book
- Available-copy checks before issue
- Protected return and delete operations using POST requests

## 8. Security

- Django password hashing and authentication
- CSRF protection
- Role-based page and action permissions
- Students can view only their own academic and service records
- Teachers can manage attendance and results only for their assigned course instance
- Administrative CRUD screens are restricted to staff users
- Server-side validation for forms and workflow rules

## 9. Testing

Automated tests cover authentication, role protection, Student and Teacher portals, course registration, bus card application, attendance and result workflows, management pages, and library pages. The application also includes graceful handling when the external library service is temporarily unavailable.

## 10. Future enhancements

Possible additions include online payment integration, registration approval workflows, downloadable transcripts, guardian access, email/SMS notifications, hostel management, payroll, transport route tracking, and REST APIs.
