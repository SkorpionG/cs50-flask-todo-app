from datetime import datetime
from flask import Flask, render_template, session, url_for, request, g
# import sqlite3
import os
# from functools import wraps
from navigation import NAV_ITEMS, DASHBOARD_TABS
from database import get_db, get_task_columns, get_tag_columns, task_priority_options, task_status_options, get_user_tags, get_user_tasks
from middleware import login_required, with_context

from auth import auth_bp
from tasks import tasks_bp
from tags import tags_bp
from settings import settings_bp

# Configure application
app = Flask(__name__)

# Configure session
# In production, use a fixed secret key
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(tags_bp)
app.register_blueprint(settings_bp)


@app.template_filter('format_datetime')
def format_datetime(value, format='%d/%m/%Y %H:%M %p'):
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            # Try to parse the string to datetime object
            if 'T' in value:  # ISO format
                value = datetime.strptime(value, '%Y-%m-%dT%H:%M')
            else:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
    return value.strftime(format)


def get_nav_links():
    nav_links = []
    # auth_required_nav_links = []
    for item in NAV_ITEMS:
        if item['requires_auth'] and not session.get('user_id'):
            continue

        nav_links.append({
            'name': item['name'],
            'url': url_for(item['url']),
            'active': request.endpoint == item['url']
        })
    return nav_links


TASK_PRIORITY_OPTIONS = task_priority_options()
TASK_STATUS_OPTIONS = task_status_options()
TAG_COLUMNS = get_tag_columns()
TASK_COLUMNS = get_task_columns()
TASK_ACTION_INFO = {task_action: {}
                    for task_action in task_status_options()}
for task_action in TASK_ACTION_INFO:
    if task_action == "In Progress":
        TASK_ACTION_INFO[task_action]["color"] = "btn-info"
        TASK_ACTION_INFO[task_action]["icon"] = " fa-clock"
    elif task_action == "Pending":
        TASK_ACTION_INFO[task_action]["color"] = "btn-warning"
        TASK_ACTION_INFO[task_action]["icon"] = " fa-undo"
    elif task_action == "Completed":
        TASK_ACTION_INFO[task_action]["color"] = "btn-success"
        TASK_ACTION_INFO[task_action]["icon"] = " fa-check"


def get_context_data(data_type):
    """Helper function to get specific context data"""
    if not hasattr(g, 'context_cache'):
        g.context_cache = {}

    # If data is already cached in this request, return it
    if data_type in g.context_cache:
        return g.context_cache[data_type]

    # Get the required data based on type
    data = None
    if session.get('user_id'):  # Only fetch data for authenticated users
        if data_type == 'task_priority_options':
            data = TASK_PRIORITY_OPTIONS
        elif data_type == 'task_status_options':
            data = TASK_STATUS_OPTIONS
        elif data_type == 'user_tags':
            data = get_user_tags(session['user_id'])
        elif data_type == 'tag_columns':
            data = TAG_COLUMNS
        elif data_type == 'task_columns':
            data = TASK_COLUMNS
        elif data_type == 'dashboard_tabs':
            data = DASHBOARD_TABS

    # Cache the data for this request
    g.context_cache[data_type] = data
    return data


@app.context_processor
def load_app_context():
    nav_links = get_nav_links()
    return {'nav_links': nav_links, 'is_authenticated': session.get('user_id')}


@app.context_processor
def load_authenticated_context():
    if not session.get('user_id'):
        return {}  # Return empty dict if user is not authenticated
    context = {
        'dashboard_tabs': DASHBOARD_TABS,
        'task_action_info': TASK_ACTION_INFO
        # Add other authenticated-only data here
    }
    # Only load required data specified by the route
    if hasattr(g, 'required_context'):
        for data_type in g.required_context:
            data = get_context_data(data_type)
            if data is not None:
                context[data_type] = data

    return context


@app.route('/home')
@app.route('/')
def index():
    return render_template('index.html', page_title='Home')


@app.route("/about")
def about():
    return render_template('about.html', page_title='About')


@app.route('/dashboard')
@login_required
@with_context(get=['task_columns'])
def dashboard():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT username FROM users WHERE id = ?",
                   (session['user_id'],))
    user = cursor.fetchone()
    db.close()

    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    user_tasks = get_user_tasks(
        user_id=session['user_id'],
        filters=[
            {'column': 'status', 'operator': '!=', 'value': 'Completed'},
            {'column': 'due_date', 'operator': '>', 'value': current_date}
        ],
        sort_column='due_date',
        sort_direction='asc'
    )

    return render_template('user/dashboard.html', tasks=user_tasks, user=user, page_title='Dashboard')


if __name__ == '__main__':
    app.run(debug=True)
