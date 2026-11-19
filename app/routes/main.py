from datetime import datetime

from flask import Blueprint, render_template, session

from app.db import get_db, get_user_tasks
from app.utils.decorators import login_required, with_context

main_bp = Blueprint("main", __name__)


@main_bp.route("/home")
@main_bp.route("/")
def index() -> str:
    return render_template("index.html", page_title="Home")


@main_bp.route("/about")
def about() -> str:
    return render_template("about.html", page_title="About")


@main_bp.route("/dashboard")
@login_required
@with_context(get=["task_columns"])
def dashboard() -> str:
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],))
    user = cursor.fetchone()
    db.close()

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_tasks = get_user_tasks(
        user_id=session["user_id"],
        filters=[
            {"column": "status", "operator": "!=", "value": "Completed"},
            {"column": "due_date", "operator": ">", "value": current_date},
        ],
        sort_column="due_date",
        sort_direction="asc",
    )

    return render_template("user/dashboard.html", tasks=user_tasks, user=user, page_title="Dashboard")
