# ServiceNow - IT Service Management System

A Flask-based IT Service Management web application inspired by ServiceNow. The system allows users to create, manage, and track IT incidents and service requests through a simple web interface.

## Features

- User registration and login
- Employment number based authentication
- Dashboard with ticket statistics
- Create and manage Incidents
- Create and manage Requests
- Automatic ticket number generation
- My Tickets section
- Ticket details and tracking
- Update tickets
- Resolve incidents
- Close tickets
- Reopen tickets
- SQLite database
- ServiceNow-inspired user interface

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript
- Werkzeug

## Project Structure

```text
ServiceNow/
│
├── app.py
├── migrate_database.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── incident.html
│   ├── request.html
│   ├── tickets.html
│   └── ticket_detail.html
│
└── instance/
    └── servicenow.db