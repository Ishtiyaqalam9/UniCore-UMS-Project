# UniCore University Management System

A role-based Django University Management System for students, teachers and administrators. The project preserves the original database connections while providing a unified and user-friendly portal.

## Main user experience

After login, every role receives a dedicated left-sidebar dashboard with separate pages and role-specific permissions.

### Student portal

- Personal profile
- Self-service course registration
- Registered course list and safe course withdrawal
- Course-wise attendance percentage and history
- Results and automatic grades
- Fee statement and outstanding balance
- Weekly class routine
- Library catalog and self-service book issue
- Personal issue/return history
- Bus card application and application tracking
- Student notices
- Password change

### Faculty portal

- Faculty profile
- Assigned course list
- Enrolled student lists
- Date-wise attendance entry and update
- Result entry and update
- Teaching routine
- Library catalog and self-service book issue
- Personal issue/return history
- Faculty notices
- Password change

### Administration portal

- Student and teacher profile management
- Department and course management
- Enrollment and teacher-course assignments
- Attendance and result administration
- Student fee ledger
- Class routine and notices
- Library catalog, copy availability, issue and return records
- Bus card application review, approval, printing and collection status
- Student, teacher and administrator login account management
- Django system administration

## Database mapping

| Area | Database | Django app |
|---|---|---|
| Student profiles | MySQL database `student` | `student` |
| Teacher profiles | PostgreSQL database `teacher` | `teacher` |
| Library books and transactions | MongoDB database `library_db` | `library` |
| Authentication, academics, bus cards and admin | SQLite `db.sqlite3` | `accounts`, `academic`, Django core |

Academic records store stable student and teacher reference IDs, such as `STU-0001` and `TCH-0001`, instead of unsupported cross-database foreign keys.

## Requirements

- Python 3.10 or newer
- MySQL Server
- PostgreSQL Server
- MongoDB Server

## First-time Windows setup

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py migrate --database=mysql
python manage.py migrate --database=postgres
python manage.py createsuperuser
python manage.py runserver
```

The included scripts provide the same workflow:

```bat
setup_windows.bat
run_server.bat
```

## First-time macOS/Linux setup

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py migrate --database=mysql
python manage.py migrate --database=postgres
python manage.py createsuperuser
python manage.py runserver
```

Or use:

```bash
chmod +x setup_mac.sh run_server_mac.sh
./setup_mac.sh
./run_server_mac.sh
```

Open `http://127.0.0.1:8000/`.

## Upgrading from the previous ZIP

The updated version includes a new SQLite migration for Bus Card Applications. Run:

```bash
python manage.py migrate
```

The migration files for Student and Teacher remain in their respective applications. Run their alias migrations after changes to those models:

```bash
python manage.py migrate --database=mysql
python manage.py migrate --database=postgres
```

MongoDB documents do not use Django migrations.

## Creating Student and Teacher login accounts

1. Sign in as the superuser.
2. Add the Student or Teacher profile.
3. Open **User Accounts** from the sidebar.
4. Select **Create Account**.
5. Select the correct role and enter the matching reference ID.
6. Set a username and password.

The user is automatically redirected to the correct portal after login.

## Course registration behavior

Students can register themselves for active courses offered in their current semester. Duplicate enrollment is prevented. A student can withdraw a course only before attendance or result records exist.

## Library behavior

Students and teachers can browse the catalog and issue available books directly to their own accounts. The default issue period is 14 days, and each member can hold up to five active books. Users can return books from **My Library**. Administrators can also issue and return books for either role.

## Bus card workflow

1. Student opens **Bus Card** and submits contact, pickup and emergency information.
2. The request starts as **Pending**.
3. Administrator reviews the request from **Bus Cards**.
4. Administrator can mark it Approved, Rejected, Printed or Collected and add card details.
5. The student sees the updated status in the portal.

## Development checks

To test without live MySQL and PostgreSQL servers:

**Windows CMD**

```bat
set UMS_USE_SQLITE_FOR_ALL=1
python manage.py test
```

**macOS/Linux**

```bash
UMS_USE_SQLITE_FOR_ALL=1 python manage.py test
```

The project includes automated tests for role permissions, navigation pages, course registration, bus card application, attendance and result entry.

## Troubleshooting

- **MySQL connection error:** verify the `student` database, credentials, service and port 3306.
- **PostgreSQL connection error:** verify the `teacher` database, credentials, service and port 5432.
- **Library unavailable:** start MongoDB and verify port 27017.
- **New page reports a missing table:** run `python manage.py migrate`.
- **Student/Teacher columns missing:** run migration with the correct database alias.
- **CSS does not load:** start the project using Django rather than opening HTML files directly.

## Project structure

```text
UniCore_UMS/
├── accounts/       # Roles, portals, registration and campus services
├── academic/       # Courses, attendance, results, fees, routine, bus cards
├── home/           # Administration dashboard
├── library/        # Catalog and issue/return workflow
├── student/        # Student profiles
├── teacher/        # Faculty profiles
├── sms_project/    # Settings, root routes and database router
├── static/ums/     # Responsive UI styles and sidebar JavaScript
├── templates/      # Base layout and authentication templates
├── db.sqlite3
├── manage.py
└── requirements.txt
```
