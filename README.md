# Addis Ray Secondary School Management System

A clean Django 5.2 school-management application for Director/Admin, Teacher and Student roles.

## Features
- Role-based login: Director, Teacher, Student
- Director-controlled teacher permissions
- Teacher/student account creation with generated temporary passwords
- Student registration with email login
- Teacher registration
- Grades 9-12 and sections A-F
- Daily attendance: Present, Absent, Late
- Academic marks with Total, Average, Pass/Fail and ranking
- Student promotion and promotion history
- Student, class and school reports
- Responsive SIT-inspired red/white/dark visual system

## Setup (Windows PowerShell)

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py makemigrations
py manage.py migrate
py manage.py seed_demo
py manage.py runserver
```

Open http://127.0.0.1:8000/

## Demo accounts
- Director: `director@addisray.local` / `Director123!`
- Teacher: `teacher@addisray.local` / `Teacher123!`
- Student: `student@addisray.local` / `Student123!`

Email uses Django's console email backend in development, so generated credentials are also printed in the terminal. Configure SMTP in `settings.py` for real email delivery.

## Important
This is a development-ready educational project. Before production use, change `SECRET_KEY`, set `DEBUG=False`, configure `ALLOWED_HOSTS`, use a production database, configure SMTP, add stronger password validators, HTTPS and backups.
