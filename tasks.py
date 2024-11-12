from flask import Blueprint, request, redirect, url_for, flash, session, render_template
import sqlite3
from datetime import datetime
from database import get_db, get_user_tasks, get_task_columns, get_user_tags, task_priority_options, task_status_options
from middleware import login_required, with_context

tasks_bp = Blueprint('tasks', __name__)


def convert_datetime_format(datetime_string):
    try:
        return datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        print("Invalid datetime string")
        return datetime_string


def validate_task(title, description, due_date, priority, status):
    errors = []

    # Title validation
    if not title or len(title.strip()) == 0:
        errors.append("Title is required")
    elif len(title) > 100:
        errors.append("Title must be less than 100 characters")

    # Description validation (optional but with max length)
    if description and len(description) > 500:
        errors.append("Description must be less than 500 characters")

    # Due date validation
    if due_date:
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            errors.append("Invalid due date format")

    # Priority validation
    valid_priorities = task_priority_options()
    if priority not in valid_priorities:
        errors.append("Invalid priority level")

    # Status validation
    valid_statuses = task_status_options()
    if status not in valid_statuses:
        errors.append("Invalid status")

    return errors


@tasks_bp.route('/tasks')
@login_required
@with_context(
    get=['task_columns'],
)
def tasks():
    user_tasks = get_user_tasks(
        user_id=session['user_id'],
        filters=[
            {'column': 'status', 'operator': '!=', 'value': 'Completed'}
        ],
        sort_column='due_date',
        sort_direction='asc'
    )

    return render_template('user/tasks.html', tasks=user_tasks, page_title='My Tasks')


@tasks_bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
@with_context(
    get=['user_tags'],
)
def create_task():
    if request.method == 'GET':
        return render_template('user/create_task.html', page_title='Create a new task')

    title = request.form.get('title')
    description = request.form.get('description')
    due_date = request.form.get('due-date')
    priority = request.form.get('priority')
    status = request.form.get('status', 'Pending')  # Default to Pending
    tag_ids = request.form.getlist('tags[]')  # Get selected tag IDs as list

    # Validate input
    errors = validate_task(title, description, due_date, priority, status)

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('dashboard'))

    due_date = convert_datetime_format(due_date)
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, due_date, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session['user_id'],
            title,
            description,
            due_date,
            priority,
            status
        ))

        task_id = cursor.lastrowid  # Get the ID of the newly created task

        # Add tags to task
        if tag_ids:
            # Verify all tags belong to the user
            placeholders = ','.join('?' * len(tag_ids))
            cursor.execute(f"""
                SELECT id FROM tags
                WHERE id IN ({placeholders})
                AND user_id = ?
            """, tag_ids + [session['user_id']])

            valid_tag_ids = [str(row['id']) for row in cursor.fetchall()]

            # Insert task-tag relationships
            for tag_id in valid_tag_ids:
                cursor.execute("""
                    INSERT INTO task_tags (task_id, tag_id)
                    VALUES (?, ?)
                """, (task_id, tag_id))

        db.commit()
        flash('Task created successfully!', 'success')

    except sqlite3.Error as e:
        flash('An error occurred while creating the task.', 'danger')
        print(f"Database error: {e}")  # For debugging

    finally:
        db.close()

    if status == 'Completed':
        return redirect(url_for('tasks.completed_tasks'))

    return redirect(url_for('tasks.tasks'))


@tasks_bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
@with_context(
    get=['user_tags'],
)
def edit_task(task_id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due-date')
        priority = request.form.get('priority')
        status = request.form.get('status')
        new_tag_ids = request.form.getlist('tags[]')  # Get updated tag IDs

        errors = validate_task(title, description, due_date, priority, status)

        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            due_date = convert_datetime_format(due_date)
            try:
                cursor.execute("""
                    UPDATE tasks 
                    SET title = ?, description = ?, due_date = ?, 
                        priority = ?, status = ?, modified_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ?
                """, (title, description, due_date, priority, status,
                      task_id, session['user_id']))

                # Update tags
                # First, remove all existing tags
                cursor.execute(
                    "DELETE FROM task_tags WHERE task_id = ?", (task_id,))

                # Then add new tags
                if new_tag_ids:
                    # Verify tags belong to user
                    placeholders = ','.join('?' * len(new_tag_ids))
                    cursor.execute(f"""
                        SELECT id FROM tags
                        WHERE id IN ({placeholders})
                        AND user_id = ?
                    """, new_tag_ids + [session['user_id']])

                    valid_tag_ids = [str(row['id'])
                                     for row in cursor.fetchall()]

                    # Insert new tag relationships
                    for tag_id in valid_tag_ids:
                        cursor.execute("""
                            INSERT INTO task_tags (task_id, tag_id)
                            VALUES (?, ?)
                        """, (task_id, tag_id))

                db.commit()
                flash('Task updated successfully!', 'success')
                return redirect(request.referrer or url_for('tasks.tasks'))
            except sqlite3.Error as e:
                flash('Failed to update task', 'danger')
                print(f"Database error: {e}")
            finally:
                db.close()

    # Get task
    cursor.execute("""
        SELECT * FROM tasks 
        WHERE id = ? AND user_id = ?
    """, (task_id, session['user_id']))
    task = cursor.fetchone()

    if not task:
        flash('Task not found', 'danger')
        return redirect(url_for('tasks.tasks'))

    # Get task's current tags
    cursor.execute("""
        SELECT tag_id FROM task_tags
        WHERE task_id = ?
    """, (task_id,))
    current_tag_ids = [row['tag_id'] for row in cursor.fetchall()]
    db.close()
    return render_template('user/edit_task.html', task=task, current_tag_ids=current_tag_ids, page_title='Edit Task')


@tasks_bp.route('/tasks/<int:task_id>/status', methods=['POST'])
@login_required
def update_status(task_id):
    db = get_db()
    cursor = db.cursor()
    try:
        task_id_hidden = request.form.get('task-id')
        new_status = request.form.get('status')

        if task_id != int(task_id_hidden):
            flash('Error updating status', 'danger')
            return redirect(url_for('tasks.tasks'))

        if new_status not in task_status_options():
            flash('Invalid status', 'danger')
            return redirect(url_for('tasks.tasks'))

        cursor.execute("""
            UPDATE tasks 
            SET status = ?, modified_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (new_status, task_id, session['user_id']))

        db.commit()
        flash(f'Task marked as {new_status}!', 'success')

    except sqlite3.Error as e:
        flash('Failed to update task status', 'danger')
        print(f"Database error: {e}")

    finally:
        db.close()

    # Redirect back to the page that made the request
    if new_status == 'Completed':
        return redirect(url_for('tasks.completed_tasks'))
    return redirect(request.referrer or url_for('tasks.tasks'))


@tasks_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    try:
        task_id_hidden = request.form.get('task-id')
        if task_id != int(task_id_hidden):
            flash('Error deleting task', 'danger')
            return redirect(url_for('tasks.tasks'))
        db = get_db()
        cursor = db.cursor()

        cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?",
                       (task_id, session['user_id']))
        db.commit()

        flash('Task deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash('Failed to delete task', 'danger')
        print(f"Database error: {e}")
    finally:
        db.close()

    return redirect(url_for('tasks.tasks'))


@tasks_bp.route('/tasks/completed')
@login_required
@with_context(get=['task_columns'])
def completed_tasks():
    user_tasks = get_user_tasks(
        user_id=session['user_id'],
        filters=[
            {'column': 'status', 'operator': '=', 'value': 'Completed'}
        ],
        sort_column='due_date',
    )

    # Simplified columns for completed tasks
    completed_columns = [
        {'key': 'title', 'label': 'Task', 'type': 'text'},
        {'key': 'due_date', 'label': 'Due Date', 'type': 'date'}
    ]

    return render_template('user/completed.html',
                           tasks=user_tasks,
                           completed_columns=completed_columns, page_title="Completed Tasks")
