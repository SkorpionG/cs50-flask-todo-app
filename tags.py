from flask import Blueprint, request, redirect, url_for, flash, session, render_template, jsonify
import sqlite3
from database import get_db, get_tag_columns, get_user_tags, get_user_tag
from middleware import login_required, with_context
import re

tags_bp = Blueprint('tags', __name__)


def validate_tag(name, color=None):
    errors = []

    if not name or len(name.strip()) == 0:
        errors.append("Tag name is required")
    elif len(name) > 50:
        errors.append("Tag name must be less than 50 characters")

    # Check for special characters
    if not name.replace('-', '').replace('_', '').isalnum():
        errors.append(
            "Tag name can only contain letters, numbers, hyphens, and underscores")

    # Validate color if provided
    if color:
        # Check if color is a valid hex color
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
            errors.append(
                "Invalid color format. Please use hex color (e.g., #FF0000)")

    return errors


@tags_bp.route('/tags')
@login_required
@with_context(
    get=['user_tags', 'tag_columns'],
)
def tags():
    return render_template('user/tags.html', page_title='My Tags')


@tags_bp.route('/tags/create', methods=['GET', 'POST'])
@login_required
def create_tag():
    if request.method == 'GET':
        return render_template('user/create_tag.html', page_title='Create a new tag')
    name = request.form.get('name')
    color = request.form.get('color', '#6c757d')

    # Validate input
    errors = validate_tag(name, color)

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('dashboard'))

    try:
        db = get_db()
        cursor = db.cursor()

        # Check if tag already exists for this user
        cursor.execute("SELECT id FROM tags WHERE user_id = ? AND name = ?",
                       (session['user_id'], name))

        if cursor.fetchone():
            flash('A tag with this name already exists.', 'danger')
            return redirect(url_for('dashboard'))

        # Create new tag
        cursor.execute("""
            INSERT INTO tags (user_id, name, color)
            VALUES (?, ?, ?)
        """, (session['user_id'], name, color))

        db.commit()
        flash('Tag created successfully!', 'success')

    except sqlite3.Error as e:
        flash('An error occurred while creating the tag.', 'danger')
        print(f"Database error: {e}")  # For debugging

    finally:
        db.close()

    return redirect(url_for('tags.tags'))


@tags_bp.route('/api/user/tags', methods=['GET'])
@login_required
def get_user_tags_api():
    user_id = session.get('user_id')
    raw_user_tags = get_user_tags(user_id)
    user_tags = [dict(tag) for tag in raw_user_tags]
    return jsonify(user_tags)


@tags_bp.route('/api/user/tags/search', methods=['GET'])
@login_required
def search_user_tags_api():
    user_id = session.get('user_id')
    tag_name = request.args.get('tag')
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT COUNT(*) as count FROM tags WHERE user_id = ? AND name = ?", (user_id, tag_name))
    tags = cursor.fetchall()
    db.close()
    return jsonify(dict(tags[0]))


@tags_bp.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color', '#6c757d')
        errors = validate_tag(name, color)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('tags.edit_tag', tag_id=tag_id))

        try:
            cursor.execute("""
                UPDATE tags 
                SET name = ?, color = ?
                WHERE id = ? AND user_id = ?
            """, (name, color, tag_id, session['user_id']))
            db.commit()
            flash('Tag updated successfully!', 'success')
            db.close()
            return redirect(url_for('tags.tags'))
        except sqlite3.Error as e:
            flash('Failed to update tag', 'danger')
            print(f"Database error: {e}")

    tag = get_user_tag(session['user_id'], tag_id)
    if not tag:
        flash('Tag not found', 'danger')
        return redirect(request.referrer or url_for('tags.tags'))

    return render_template('user/edit_tag.html', tag=tag, page_title='Edit Tag')


@tags_bp.route('/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
    try:
        tag_id_hidden = request.form.get("tag-id")
        if tag_id != int(tag_id_hidden):
            flash('Error deleting tag', 'danger')
        db = get_db()
        cursor = db.cursor()

        cursor.execute("DELETE FROM tags WHERE id = ? AND user_id = ?",
                       (tag_id, session['user_id']))
        db.commit()

        flash('Tag deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash('Failed to delete tag', 'danger')
        print(f"Database error: {e}")
    finally:
        db.close()

    return redirect(url_for('tags.tags'))
