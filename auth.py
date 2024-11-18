from flask import Blueprint, request, session, redirect, url_for, render_template, flash
import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash
from validation import validate_email, validate_password
from database import get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("user_id"):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm-password')
        remember = request.form.get('keep-logged-in')

        # Form validation
        if not username or not email or not password or not confirm:
            flash('All fields are required', 'info')
            return render_template('auth/register.html')

        if not validate_email(email):
            flash('Invalid email address', 'warning')
            return render_template('auth/register.html')

        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg, 'warning')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match', 'warning')
            return render_template('auth/register.html')

        db = get_db()
        cursor = db.cursor()

        try:
            # Check if email already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                flash('Email already registered', 'warning')
                return render_template('auth/register.html')

            # Insert new user
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, generate_password_hash(password))
            )
            db.commit()

            # Get the user id of newly created user
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()

            # Log the user in
            session['user_id'] = user['id']
            if remember:
                session.permanent = True
            flash('Registration successful!', 'success')

            return redirect(url_for('dashboard'))

        except sqlite3.Error:
            flash('Registration failed', 'danger')
            return render_template('auth/register.html')
        finally:
            db.close()

    return render_template('auth/register.html', page_title='Register')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("user_id"):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')

        if not email or not password:
            flash('Please provide both email and password', 'info')
            return render_template('auth/login.html')

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()

            if user is None or not check_password_hash(user['password_hash'], password):
                flash('Invalid email or password', 'warning')
                return render_template('auth/login.html')

            # Set session
            session['user_id'] = user['id']
            if remember:
                session.permanent = True

            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard'))

        except sqlite3.Error:
            flash('Login failed', 'danger')
            return render_template('auth/login.html')
        finally:
            db.close()

    return render_template('auth/login.html', page_title='Login')


@auth_bp.route('/logout')
def logout():
    if session.get("user_id"):
        session.clear()
        flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        if not email or not validate_email(email):
            flash('Please provide a valid email address')
            return render_template('auth/forgot-password.html')

        # Here you would typically:
        # 1. Generate a reset token
        # 2. Store it in the database with an expiration
        # 3. Send an email with the reset link
        # For now, we'll just show a message

        flash('If an account exists with that email, you will receive password reset instructions')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot-password.html', page_title='Forgot Password')
