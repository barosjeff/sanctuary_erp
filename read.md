# Sanctuary Worship Center ERP

## Project Overview
Sanctuary Worship Center ERP is a web-based Church Management System developed using Flask and SQLite.  
The system is designed to help manage church operations such as member registration, attendance tracking, donations, events, and user authentication.

This project aims to digitize church administrative processes and improve efficiency, accountability, and record keeping.

---

## Objectives
- To manage church members efficiently
- To track attendance records
- To record and manage donations
- To manage church events
- To provide role-based access (Admin & Member)
- To ensure secure login and session management

---

## System Features

### Admin Module
- Admin login and logout
- Register, edit, and delete church members
- Automatically generate membership numbers
- Record and view attendance
- Manage donations
- Create and manage church events
- View all system records

### Member Module
- Member login
- View personal donations
- View personal attendance records

---

## Technologies Used
- Python (Flask Framework)
- SQLite Database
- HTML, CSS (Jinja2 Templates)
- Bootstrap (UI styling)
- Git & GitHub (Version Control)

---

## System Architecture
- Frontend: HTML templates rendered using Jinja2
- Backend: Flask application (Python)
- Database: SQLite (`sanctuary_erp.db`)
- Authentication: Session-based authentication

---

## Installation Guide

### Prerequisites
- Python 3.9+
- Git
- Web browser

### Installation Steps

1. Clone the repository
```bash
git clone https://github.com/barosjeff/sanctuary_erp.git
cd sanctuary_erp.git
