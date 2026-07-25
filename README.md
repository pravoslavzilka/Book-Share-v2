# Book-Share (eSklad)

A Flask web application for managing **textbook and book lending in a secondary school**. Librarians and teachers track who has borrowed which book across subjects and grades; students log in to see and manage their own borrowed books.

Built for **Gymnázium matky Alexie**, where it ran in production for **three years**, serving roughly **400 students** and a catalogue of around **1,800 books**. Branded in use as *eSklad*. The interface is in Slovak.

> This is version 2 — a rewrite of the original Book-Share with a cleaner structure, student self-service accounts, email-based password reset, and bulk Excel import.

## What it does

The app has three role-based interfaces, each a Flask blueprint:

| Interface | Prefix | Used by | Purpose |
| --- | --- | --- | --- |
| **Admin** | `/admin` | Librarians / staff | Manage the student roster by grade, add/remove students, promote or demote all students a grade at year rollover, return books on a student's behalf, and import students from Excel |
| **Book** | `/book` | Librarians / staff | Manage the catalogue: browse by title, add copies, track rented vs. available state, add/edit/delete book types, return books through several workflows, and import the catalogue from Excel |
| **Student** | `/student` | Students | Log in, view their account and borrowed books, rent a book, and reset their password |

### Lending model

Each physical copy of a book (a `Book`) has a code and is linked to its title (`BookType`, with author) and, when borrowed, to the `Student` currently holding it. Returning a book clears that link. Librarians can return a single book, all of a student's books at once, or books in bulk by code, list, or type.

### Students and grades

Students belong to a `Grade` (the Slovak gymnázium grades: Prima–Oktáva and 1.A–4.B). At the end of a school year, admins can move every student up or down a grade in one action. Students are pre-created with a unique code, then complete their own registration and set a password using that code; accounts can also be grouped with `Tags` (e.g. extracurricular groups) and associated with `Events`.

### Authentication

Students and admins are separate account types with a shared login flow. Password reset is handled by emailing a signed, time-limited token (via `itsdangerous`) and sending it through SMTP with Flask-Mail. Sessions use hardened, secure, same-site cookies.

## Tech stack

- **Backend:** Python, [Flask](https://flask.palletsprojects.com/) 2.0 with blueprints
- **Auth:** Flask-Login, Werkzeug password hashing, `itsdangerous` reset tokens
- **Database:** SQLAlchemy ORM — MySQL in production, SQLite for local development
- **Email:** Flask-Mail (SMTP) on background threads
- **Import/export:** pandas + openpyxl for Excel spreadsheets
- **Serving:** Gunicorn

## Data model

- **User** — an admin/librarian account
- **Student** — a pupil: name, email, unique code, authorization flag, grade, borrowed books, tags, events
- **Grade** — a class/year group
- **Tag** — an optional grouping of students
- **Event** — a student event with a teacher and date
- **BookType** — a title and its author
- **Book** — a physical copy: code, its type, and the student currently borrowing it

## Project structure

```
Book-Share-v2/
├── __init__.py            # App factory: blueprints, login, mail, password reset
├── database.py            # SQLAlchemy engine + session
├── models.py              # User, Student, Grade, Tag, Event, Book, BookType
├── migration.py           # Seed script: creates grades and sample data
├── gunicorn_config.py     # Production server config
├── requirements.txt
├── blueprints/
│   ├── admin/             # Student roster & grade management
│   ├── book/              # Catalogue & lending management
│   └── student/           # Student self-service
├── templates/             # Jinja2 templates (incl. error pages, emails)
└── static/                # CSS, JS, assets
```

## Running locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure secrets via environment variables (see Configuration)

# 3. Create the database and seed grades + sample data (uses local SQLite)
python migration.py

# 4. Run
#    Development:
flask run
#    Production:
gunicorn -c gunicorn_config.py __init__:app
```

`database.py` is set to use local SQLite by default; point the engine at MySQL for production.

## Configuration

Provide these through **environment variables**, never in source:

- `secretKey` — Flask session signing key (already read from the environment)
- Database URL (MySQL in production; SQLite locally)
- SMTP mail server, username, and password for password-reset emails

## Status

Ran in production for three years at Gymnázium matky Alexie. Published here as an archive of the project; not actively maintained.
