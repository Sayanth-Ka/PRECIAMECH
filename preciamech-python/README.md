# Preciamech Engineering Consultants — Python / Flask

Full website for Preciamech Engineering Consultants built with **Python (Flask)**, **HTML**, **CSS**, and **JavaScript**. Designed to open and run in PyCharm.

## Quick Start

### 1. Open in PyCharm
Open the `preciamech-python` folder as a project.

### 2. Create a Virtual Environment
In PyCharm: **File → Settings → Project → Python Interpreter → Add → Virtualenv**
Or in the terminal:
```bash
python -m venv venv
```
Activate:
- **Windows:** `venv\Scripts\activate`
- **Mac / Linux:** `source venv/bin/activate`

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python app.py
```
Open **http://localhost:5000** in your browser.

The SQLite database (`preciamech.db`) and sample projects are created automatically on first run.

---

## Default Admin Login

| Field    | Value                              |
|----------|------------------------------------|
| URL      | http://localhost:5000/admin/login  |
| Email    | admin@preciamech.com               |
| Password | Admin@1234                         |

> Change the password after first login.

---

## Project Structure

```
preciamech-python/
├── app.py                        # Flask app, routes, models, DB init
├── requirements.txt              # Python dependencies
├── preciamech.db                 # SQLite database (auto-created)
├── static/
│   ├── css/style.css             # All styles (responsive)
│   ├── js/main.js                # Mobile menu, confirm dialogs
│   └── uploads/                  # Uploaded project images (auto-created)
└── templates/
    ├── base.html                 # Shared navbar + footer layout
    ├── index.html                # Home page
    ├── services.html             # Services page
    ├── projects.html             # Projects portfolio with filters
    ├── project_detail.html       # Individual project page
    ├── about.html                # About us + timeline
    ├── contact.html              # Contact form
    └── admin/
        ├── login.html            # Admin login page
        ├── dashboard.html        # Projects table + stats
        └── project_form.html     # Create / Edit project form
```

---

## Features

### Public Website
| Page | Description |
|------|-------------|
| **Home** | Hero, featured projects from DB, services overview, CTA |
| **Services** | Full list of 8 engineering service offerings |
| **Projects** | Portfolio grid with sector + status filters |
| **Project Detail** | Full project info, image, scope, client details |
| **About** | Company history, milestone timeline, core values |
| **Contact** | Inquiry form (flash message on submit) |

### Admin Panel (`/admin`)
| Feature | Details |
|---------|---------|
| **Secure Login** | Email + hashed password via Werkzeug |
| **Dashboard** | Stats cards + full projects table |
| **Create Project** | Title, client, location, sector, status, description, image |
| **Edit Project** | Same form pre-filled with existing data |
| **Delete Project** | Confirmation dialog before delete |
| **Toggle Featured** | ⭐ / ☆ button — controls homepage display |
| **Image Upload** | Stored in `static/uploads/`, served by Flask |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | Flask 3.0 |
| Database | SQLite via SQLAlchemy |
| Auth | Flask-Login + Werkzeug password hashing |
| Templates | Jinja2 (built into Flask) |
| Styling | Custom CSS (no frameworks) |
| JavaScript | Vanilla JS |
