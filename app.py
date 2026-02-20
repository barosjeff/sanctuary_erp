from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session management

# ---------------------- Initialize Database ----------------------
def init_db():
    conn = sqlite3.connect('sanctuary_erp.db')
    cursor = conn.cursor()

    # Members Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            membership_number TEXT UNIQUE,
            full_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            ministry TEXT,
            address TEXT,
            national_id TEXT,
            dob TEXT,
            home_county TEXT
        )
    ''')

    # Donations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_name TEXT NOT NULL,
            amount REAL,
            purpose TEXT,
            date TEXT DEFAULT CURRENT_DATE
        )
    ''')

    # Events Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            date TEXT,
            location TEXT
        )
    ''')

    # Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_name TEXT NOT NULL,
            date TEXT,
            status TEXT
        )
    ''')

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL  -- 'admin' or 'member'
        )
    ''')

    # Create default admin if not exists
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', 'admin123', 'admin'))

    conn.commit()
    conn.close()

init_db()

# ---------------------- Helper Functions ----------------------
def generate_membership_number():
    conn = sqlite3.connect('sanctuary_erp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM members")
    count = cursor.fetchone()[0] + 1
    conn.close()
    return f"SWC-{count:04d}"

# ---------------------- LOGIN MODULE ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('sanctuary_erp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]

            if user[3] == 'admin':
                return redirect(url_for('index'))
            else:
                return redirect(url_for('member_dashboard'))
        else:
            flash("Invalid username or password")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------- ADMIN PAGES ----------------------
def admin_required(func):
    def wrapper(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/', methods=['GET', 'POST'])
@admin_required
def index():
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone = request.form['phone']
        email = request.form['email']
        ministry = request.form['ministry']
        address = request.form['address']
        national_id = request.form['national_id']
        dob = request.form['dob']
        home_county = request.form['home_county']

        membership_number = generate_membership_number()

        conn = sqlite3.connect('sanctuary_erp.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO members
            (membership_number, full_name, phone, email, ministry, address, national_id, dob, home_county)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (membership_number, full_name, phone, email, ministry, address, national_id, dob, home_county))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    conn = sqlite3.connect('sanctuary_erp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    conn.close()
    return render_template('index.html', members=members)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_member(id):
    conn = sqlite3.connect('sanctuary_erp.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        full_name = request.form['full_name']
        phone = request.form['phone']
        email = request.form['email']
        ministry = request.form['ministry']
        address = request.form['address']
        national_id = request.form['national_id']
        dob = request.form['dob']
        home_county = request.form['home_county']

        cursor.execute('''
            UPDATE members SET
            full_name=?, phone=?, email=?, ministry=?, address=?, national_id=?, dob=?, home_county=?
            WHERE id=?
        ''', (full_name, phone, email, ministry, address, national_id, dob, home_county, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM members WHERE id=?", (id,))
    member = cursor.fetchone()
    conn.close()
    return render_template('edit_member.html', member=member)

@app.route('/delete/<int:id>')
@admin_required
def delete_member(id):
    conn = sqlite3.connect('sanctuary_erp.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ---------------------- Donations Module ----------------------
@app.route('/donations', methods=['GET', 'POST'])
@admin_required
def donations():
    if request.method == 'POST':
        donor_name = request.form['donor_name']
        amount = request.form['amount']
        purpose = request.form['purpose']

        conn = sqlite3.connect('sanctuary_erp.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO donations (donor_name, amount, purpose)
            VALUES (?, ?, ?)
        ''', (donor_name, amount, purpose))
        conn.commit()
        conn.close()
        return redirect(url_for('donations'))

    conn = sqlite3.connect('sanctuary_erp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donations ORDER BY date DESC")
    donations_list = cursor.fetchall()
    conn.close()
    return render_template('donations.html', donations=donations_list)

# ---------------------- Events Module ----------------------
@app.route('/events', methods=['GET', 'POST'])
@admin_required
def events():
    if request.method == 'POST':
        # Use get() to avoid KeyError
        event_name = request.form.get('event_name')
        event_date = request.form.get('event_date')
        location = request.form.get('location')

        print("Received Event:", event_name, event_date, location)  # Debug

        if not event_name or not event_date or not location:
            flash("All fields are required!")
            return redirect(url_for('events'))

        conn = sqlite3.connect('sanctuary_erp.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (event_name, date, location)
            VALUES (?, ?, ?)
        ''', (event_name, event_date, location))
        conn.commit()
        conn.close()
        flash("Event added successfully!")
        return redirect(url_for('events'))

    conn = sqlite3.connect('sanctuary_erp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY date DESC")
    events_list = cursor.fetchall()
    conn.close()
    return render_template('events.html', events=events_list)

# ---------------------- Attendance Module ----------------------
@app.route('/attendance', methods=['GET', 'POST'])
@admin_required
def attendance():
    if request.method == 'POST':
        member_name = request.form.get('member_name')
        date = request.form.get('date')
        status = request.form.get('status')

        if not member_name or not date or not status:
            flash("All fields are required!")
            return redirect(url_for('attendance'))

        conn = sqlite3.connect('sanctuary_erp.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attendance (member_name, date, status)
            VALUES (?, ?, ?)
        ''', (member_name, date, status))
        conn.commit()
        conn.close()
        flash("Attendance recorded!")
        return redirect(url_for('attendance'))

    conn = sqlite3.connect('sanctuary_erp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance ORDER BY date DESC")
    attendance_list = cursor.fetchall()
    conn.close()
    return render_template('attendance.html', attendance=attendance_list)

# ---------------------- MEMBER DASHBOARD ----------------------
@app.route('/member_dashboard')
def member_dashboard():
    if 'role' not in session or session['role'] != 'member':
        return redirect(url_for('login'))

    username = session['username']

    conn = sqlite3.connect('sanctuary_erp.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM donations WHERE donor_name=?", (username,))
    donations_list = cursor.fetchall()

    cursor.execute("SELECT * FROM attendance WHERE member_name=?", (username,))
    attendance_list = cursor.fetchall()

    conn.close()
    return render_template('member_dashboard.html', donations=donations_list, attendance=attendance_list)

# ---------------------- RUN APP ----------------------
if __name__ == '__main__':
    app.run(debug=True)
