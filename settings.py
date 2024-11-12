# settings.py
from flask import Blueprint, request, redirect, url_for, flash, session, render_template
import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from validation import validate_email, validate_password
from middleware import login_required

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
@login_required
def settings():
    db = get_db()
    cursor = db.cursor()

    # Get user's current information
    cursor.execute("""
        SELECT username, email 
        FROM users 
        WHERE id = ?
    """, (session['user_id'],))

    user = cursor.fetchone()
    db.close()

    return render_template('user/settings.html',
                           user=user, page_title='Account Settings')


@settings_bp.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')

    if not username or not email:
        flash('Username and email are required', 'info')
        return redirect(url_for('settings.settings'))

    if not validate_email(email):
        flash('Invalid email format', 'warning')
        return redirect(url_for('settings.settings'))

    try:
        db = get_db()
        cursor = db.cursor()

        # Check if email is already in use by another user
        cursor.execute("""
            SELECT id FROM users 
            WHERE email = ? AND id != ?
        """, (email, session['user_id']))

        if cursor.fetchone():
            flash('Email is already in use', 'warning')
            return redirect(url_for('settings.settings'))

        # Update user information
        cursor.execute("""
            UPDATE users 
            SET username = ?, email = ? 
            WHERE id = ?
        """, (username, email, session['user_id']))

        db.commit()
        flash('Profile updated successfully', 'success')

    except sqlite3.Error as e:
        flash('An error occurred while updating profile', 'danger')
        print(f"Database error: {e}")

    finally:
        db.close()

    return redirect(url_for('settings.settings'))


@settings_bp.route('/settings/password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current-password')
    new_password = request.form.get('new-password')
    confirm_password = request.form.get('confirm-password')

    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required', 'info')
        return redirect(url_for('settings.settings'))

    try:
        db = get_db()
        cursor = db.cursor()

        # Verify current password
        cursor.execute("""
            SELECT password_hash 
            FROM users 
            WHERE id = ?
        """, (session['user_id'],))

        user = cursor.fetchone()
        actual_current_password = user['password_hash']
        if not check_password_hash(actual_current_password, current_password):
            flash('Current password is incorrect', 'warning')
            return redirect(url_for('settings.settings'))

        # Validate new password
        errors = []
        if not validate_password(new_password):
            errors.append("Invalid password")
        if new_password != confirm_password:
            errors.append("Passwords do not match")
        if check_password_hash(actual_current_password, new_password):
            errors.append(
                "New password cannot be the same as current password")

        if errors:
            for error in errors:
                flash(error, 'warning')
            return redirect(url_for('settings.settings'))

        # Update password
        password_hash = generate_password_hash(new_password)
        cursor.execute("""
            UPDATE users 
            SET password_hash = ? 
            WHERE id = ?
        """, (password_hash, session['user_id']))

        db.commit()
        flash('Password updated successfully', 'success')

    except sqlite3.Error as e:
        flash('An error occurred while updating password', 'danger')
        print(f"Database error: {e}")

    finally:
        db.close()

    return redirect(url_for('settings.settings'))


@settings_bp.route('/settings/delete-account', methods=['POST'])
@login_required
def delete_account():
    password = request.form.get('delete-account-password')

    if not password:
        flash('Password is required to delete account', 'warning')
        return redirect(url_for('settings.settings'))

    try:
        db = get_db()
        cursor = db.cursor()

        # Verify password
        cursor.execute("""
            SELECT password_hash 
            FROM users 
            WHERE id = ?
        """, (session['user_id'],))

        user = cursor.fetchone()
        if not check_password_hash(user['password_hash'], password):
            flash('Incorrect password', 'warning')
            return redirect(url_for('settings.settings'))

        # Delete all user data in correct order to maintain referential integrity
        # First, delete task_tags associations
        cursor.execute("""
            DELETE FROM task_tags 
            WHERE task_id IN (
                SELECT id FROM tasks WHERE user_id = ?
            )
        """, (session['user_id'],))

        # Delete tasks
        cursor.execute("DELETE FROM tasks WHERE user_id = ?",
                       (session['user_id'],))

        # Delete tags
        cursor.execute("DELETE FROM tags WHERE user_id = ?",
                       (session['user_id'],))

        # Finally, delete the user
        cursor.execute("DELETE FROM users WHERE id = ?",
                       (session['user_id'],))

        db.commit()

        # Clear session
        session.clear()
        flash('Your account has been successfully deleted', 'success')

    except sqlite3.Error as e:
        flash('An error occurred while deleting account', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('settings.settings'))

    finally:
        db.close()

    return redirect(url_for('index'))
