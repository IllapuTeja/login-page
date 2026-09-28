from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_this_in_production'

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  username TEXT UNIQUE NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Helper function to validate email
def is_valid_email(email):
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

# Helper function to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Route to serve login page
@app.route('/')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# API endpoint for login
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        # Validation
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        if not is_valid_email(email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Check user in database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id, password FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['email'] = email
            
            # Remember me functionality
            if remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

# Route for user registration
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        username = data.get('username', '').strip()
        
        # Validation
        if not email or not password or not username:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if not is_valid_email(email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert user into database
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (email, password, username) VALUES (?, ?, ?)',
                     (email, hashed_password, username))
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Registration successful. Please login.'}), 201
        
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Email or username already exists'}), 409
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return jsonify({'message': f'Welcome {session.get("email")}', 'user_id': session.get('user_id')})

# Logout route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Get user info
@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id, email, username, created_at FROM users WHERE id = ?', (session.get('user_id'),))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'email': user[1],
            'username': user[2],
            'created_at': user[3]
        })
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
