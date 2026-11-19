# Flask Todo App

## Running the Application

To run the application, follow these steps:

1. Clone the repository to your local machine.
2. Install Python 3.x and pip if you haven't already.
3. Optional: Install the `uv` Python package manager (see [installation guide](https://docs.astral.sh/uv/getting-started/installation/))
4. Install the required libraries by running:

   ```bash
   pip install -r requirements.txt
   ```

   If you are using `uv`, you can install dependencies and set up the environment by running:

   ```bash
   uv sync
   ```

5. Set up the database by running:

   ```bash
   uv run poe db-init
   ```

   *(Alternatively, run `python -m app.db auto` or `flask --app app db-init`)*

6. Run the app by running:

   ```bash
   uv run poe dev
   ```

   *(Alternatively, run `uv run flask --app app run --debug` or `uv run python run.py`)*

## Development Commands

This project uses **Ruff** for linting and formatting, **mypy** for type checking, **pytest** for testing, and **pre-commit** for git hooks. You can run these tasks using `uv run poe <command>`:

| Command | Description |
| :--- | :--- |
| **`uv run poe check`** | Run all checks (linting + format check + type checking + tests) |
| **`uv run poe test`** | Run `pytest` test suite |
| **`uv run poe typecheck`** | Run `mypy` type checking |
| **`uv run poe lint`** | Run `ruff` linting |
| **`uv run poe lint-fix`** | Run `ruff` linting with auto-fix |
| **`uv run poe format`** | Format code with `ruff format` |
| **`uv run poe format-check`** | Verify code formatting without modifying files |
| **`uv run poe dev`** | Start the Flask development server (`flask --app app run --debug`) |
| **`uv run poe db-init`** | Auto-initialize the database (`python -m app.db auto`) |
| **`uv run poe db-reset`** | Reset the database — wipes all data (`python -m app.db reset`) |

To enable the pre-commit hooks locally on a fresh clone:

```bash
uv sync
uv run pre-commit install
```

## Description

### About

This project is a simple todo app that allow users to create, organize, and track their todo tasks. The user has the option of creating a new account if they don't already have one, or to login with their existing account before they can create or manage their task. After logging in, the user will be redirected to the dashboard page. This page will show tasks that are due within a week. In this app, the user can create new tasks and customize it by:

1. Create a task title
2. Give it a description
3. Set a status (Pending, In Progress, Completed),
4. Set a priority (Low, Medium, High),
5. Set a due date for the task
6. Set one or more tags

Beside the above properties of a task, the app will record the **created time** and **last modified** time of the task. These properties will remain editable throughout the entire lifetime of the task until deleted by the user. In addition, the user will have the ability to sort tasks by priority, status, due date, and created time, as well as filter tasks by priority, status, created time, tags, and by user search. The user also can organize tasks by creating tags. Each task can be associated with multiple tags, and one tag can be associated with multiple tasks. The user can customize a tag by:

1. Give a tag name
2. Set a color coding for easy recognition

Lastly, the app provides a setting page where the user can modify their account settings, including username, email address, password. In the same page, the user can delete their account after entering their current password and confirm the action.

### Frontend Logic

The majority of the code associated with the frontend is located within `app/static/` and `app/templates/`. The `app/templates/` directory is where all the HTML and Jinja templates are located:

- `auth/`: user authentication pages (login, registration, password reset).
- `components/`: reusable HTML components that do not depend on backend data.
- `macros/`: Jinja macros that accept arguments and can be imported across templates.
- `user/`: authenticated pages including dashboard, settings, tasks, and tags views and forms.
- Root templates (`index.html`, `about.html`, `layout.html`): public pages and base layout.

Inside `app/static/` are CSS/SCSS stylesheets (`css/`), client-side JavaScript (`js/`), and image/icon assets (`assets/`).

### Backend Logic

The backend follows the Flask **Application Factory** and **Blueprints** convention inside the `app/` package (with a thin `run.py` entry point at the repository root):

- `app/__init__.py`: Application factory (`create_app()`) that loads config, initializes the database, and registers blueprints, context processors, template filters, and Flask CLI commands.
- `app/config.py`: Configuration settings and `pathlib.Path`-based locations for the database and `sql/` directory.
- `app/context.py`: Jinja template filters (`format_datetime`), context processors, and lazy schema metadata helpers.
- `app/navigation.py`: Navigation links and dashboard sidebar tab definitions.
- `app/routes/`: Feature blueprints:
  - `main.py` (`main_bp`): Home (`/`), about (`/about`), and user dashboard (`/dashboard`).
  - `auth.py` (`auth_bp`): Registration, login, logout, and password reset routes.
  - `tasks.py` (`tasks_bp`): Task CRUD, status updates, and completed tasks views.
  - `tags.py` (`tags_bp`): Tag CRUD and tag search/listing API endpoints.
  - `settings.py` (`settings_bp`): Profile updates, password changes, and account deletion.
- `app/db/`: Database layer:
  - `queries.py`: SQLite connection helper (`get_db`) and reusable query helpers.
  - `init_db.py`: Schema verification, auto-initialization, and reset utilities reading from `sql/schemas/`.
  - `__main__.py`: CLI entry point (`python -m app.db [auto|reset]`).
- `app/utils/`: Shared utilities:
  - `decorators.py`: Route decorators (`login_required`, `with_context`).
  - `validation.py`: Input validation and datetime conversion helpers.

### Database

Inside the database.db, there are 3 tables that are responsible for storing user data, which are the **users** table, **tasks** table, **tags** table, and **task_tags** table.

- The **users** table store account related user data, such as email, username, and password hash.
- The **tasks** table store task related to user tasks. Each task is associated with one user and has a user_id field. The tasks table also stores the other various properties associated with a task.
- The **tags** table store tags created by the users. Each tag is associated with one user and has a user_id field. The tags table also stores the name and color coding for each tag.
- The **task_tags** table is a many to many relationship database that join the tasks and tags table. This is because each task can have many tags attached or connected, while each tags can be connected by multiple tasks.

### Notes

Before running the application, be sure to install all the required libraries and run `uv run poe db-init` (or `python -m app.db auto`) to initialize the database.
