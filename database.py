import sqlite3
import re
from datetime import datetime

DB_NAME = 'database.db'

# Database connection helper


def get_db():
    """
    Connects to the database file and returns a connection object.

    The connection object is set to use the Row factory, which provides
    a dictionary-like interface to the columns of a query result.

    Returns:
        sqlite3.Connection: A connection to the database.
    """
    db = sqlite3.connect(DB_NAME)
    db.row_factory = sqlite3.Row
    return db


def get_task_columns():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("PRAGMA table_info(tasks)")
    columns = cursor.fetchall()
    result = []
    orders = {'title': 1, 'description': 2,
              'priority': 3, 'status': 4, 'tags': 5, 'due_date': 6, 'created_at': 7, 'modified_at': 8}
    for column in columns:
        if column[1] in ['created_at', 'modified_at', 'due_date']:
            result.append({'key': column[1], 'label': column[1].title(
            ).replace("_", " "), 'type': 'date'})
        elif column[1] in ['priority', 'status']:
            result.append(
                {'key': column[1], 'label': column[1].title(), 'type': 'select'})
        elif column[1] in ['user_id', 'id']:
            continue  # Skip id and user_id column in the output
        else:
            result.append(
                {'key': column[1], 'label': column[1].title(), 'type': 'text'})
        result[len(result)-1]['order'] = orders.get(column[1], 0)

    db.close()
    result.append(
        {'key': 'tags', 'label': 'Tags', 'type': 'tags', 'order': orders['tags']})
    result.sort(key=lambda x: x['order'])
    return result


def get_tag_columns():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("PRAGMA table_info(tags)")
    columns = cursor.fetchall()
    db.close()
    result = []
    orders = {
        'name': 1, 'color': 2, 'created_at': 3
    }
    for column in columns:
        if column[1] in ['created_at']:
            result.append({'key': column[1], 'label': column[1].title(
            ).replace("_", " "), 'type': 'date'})
        elif column[1] in ['user_id', 'id']:
            continue
        elif column[1] in ["color"]:
            result.append(
                {'key': column[1], 'label': column[1].title(), 'type': 'color'})
        else:
            result.append(
                {'key': column[1], 'label': column[1].title(), 'type': 'text'})
        result[len(result)-1]['order'] = orders[column[1]]

    result.sort(key=lambda x: x['order'])
    return result


def get_user_tags(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT *
        FROM tags
        WHERE user_id = ?
    """, (user_id,))

    tags = cursor.fetchall()
    db.close()

    return tags


def get_user_tag(user_id, tag_id):
    db = get_db()
    cursor = db.cursor()

    # Get tag
    cursor.execute("""
        SELECT * FROM tags
        WHERE id = ? AND user_id = ?
    """, (tag_id, user_id))
    tag = cursor.fetchone()
    db.close()
    return tag


def get_user_tasks(user_id, sort_column=None, sort_direction='asc', filters=None):
    """
    Get user tasks with sorting and filtering capabilities.

    Args:
        user_id (int): The user ID
        sort_column (str, optional): Column name to sort by
        sort_direction (str, optional): 'asc' or 'desc'
        filters (list, optional): List of filter dictionaries
            Example filters:
            [
                {'column': 'status', 'operator': '!=', 'value': 'Completed'},
                {'column': 'priority', 'operator': '=', 'value': 'High'},
                {'column': 'due_date', 'operator': '<', 'value': '2024-12-31'},
            ]

    Returns:
        list: List of task dictionaries with tags included
    """
    try:
        db = get_db()
        cursor = db.cursor()

        # Base query
        query = """
            SELECT 
                t.*,
                GROUP_CONCAT(tag.id) as tag_ids,
                GROUP_CONCAT(tag.name) as tag_names,
                GROUP_CONCAT(tag.color) as tag_colors
            FROM tasks t
            LEFT JOIN task_tags tt ON t.id = tt.task_id
            LEFT JOIN tags tag ON tt.tag_id = tag.id
            WHERE t.user_id = ?
        """
        params = [user_id]

        # Add filters if provided
        if filters:
            valid_operators = ['=', '!=', '<', '>', '<=', '>=', 'LIKE']
            date_columns = ['due_date', 'created_at', 'modified_at']

            for filter_dict in filters:
                column = filter_dict.get('column')
                operator = filter_dict.get('operator', '=')
                value = filter_dict.get('value')

                if not all([column, operator, value]) or operator not in valid_operators:
                    continue

                # Handle date columns
                if column in date_columns:
                    try:
                        # Convert to consistent datetime format
                        if not isinstance(value, str):
                            continue
                        if 'T' in value:
                            value = datetime.strptime(value, '%Y-%m-%dT%H:%M')
                        else:
                            # Try different date formats
                            date_formats = [
                                '%Y-%m-%d %H:%M:%S',
                                '%Y-%m-%d %H:%M',
                                '%Y-%m-%d'
                            ]
                            for fmt in date_formats:
                                try:
                                    value = datetime.strptime(value, fmt)
                                    break
                                except ValueError:
                                    continue
                        # Convert datetime back to string in SQLite format
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        continue

                # Handle LIKE operator
                if operator == 'LIKE':
                    value = f'%{value}%'

                query += f" AND t.{column} {operator} ?"
                params.append(value)

        # Group by to handle tag concatenation
        query += " GROUP BY t.id"

        # Add sorting if provided
        valid_sort_columns = [
            'title', 'description', 'due_date', 'priority',
            'status', 'created_at', 'modified_at'
        ]

        if sort_column and sort_column in valid_sort_columns:
            sort_direction = 'DESC' if sort_direction.lower() == 'desc' else 'ASC'
            query += f" ORDER BY t.{sort_column} {sort_direction}"
        else:
            # Default sorting by due date
            query += " ORDER BY t.due_date ASC"

        cursor.execute(query, params)
        tasks_raw = cursor.fetchall()

        # Process results
        tasks = []
        for task in tasks_raw:
            task_dict = dict(task)

            # Process tags
            if task_dict['tag_names']:
                names = task_dict['tag_names'].split(',')
                colors = task_dict['tag_colors'].split(',')
                ids = task_dict['tag_ids'].split(',')
                task_dict['tags'] = [
                    {'id': int(id), 'name': name, 'color': color}
                    for id, name, color in zip(ids, names, colors)
                ]
            else:
                task_dict['tags'] = []

            # Remove the concatenated columns as they're no longer needed
            del task_dict['tag_names']
            del task_dict['tag_colors']
            del task_dict['tag_ids']

            tasks.append(task_dict)

        return tasks

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        db.close()


def get_column_constraints(table_name, column_name):
    db = get_db()
    cursor = db.cursor()

    # Get table info
    cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    create_sql = cursor.fetchone()['sql']

    # Parse the CHECK constraint
    constraint_pattern = fr"{
        column_name} TEXT CHECK\({column_name} IN \((.+?)\)\)"
    match = re.search(constraint_pattern, create_sql)

    if match:
        # Extract values from the constraint
        values_str = match.group(1)
        # Convert "'High', 'Medium', 'Low'" to ['High', 'Medium', 'Low']
        values = [val.strip("' ") for val in values_str.split(',')]
        return values

    return []


def task_priority_options():
    return get_column_constraints('tasks', 'priority')


def task_status_options():
    return get_column_constraints('tasks', 'status')


if __name__ == "__main__":
    # columns = get_task_columns()
    # print(columns)
    # columns = get_tag_columns()
    # print(columns)
    # priority_options = task_priority_options()
    # print(priority_options)
    # status_options = task_status_options()
    # print(status_options)

    tasks = get_user_tasks(
        user_id=1,
    )

    for task in tasks:
        print(task)
