import sqlite3
from pathlib import Path
from typing import Any

from app.config import DATABASE_PATH, DROP_TABLES_FILE, INDEX_FILE, SCHEMAS_DIR


def parse_sql_columns(sql_content: str, table_name: str) -> list[str]:
    """Parse SQL CREATE TABLE statement to extract column names by executing it in memory."""
    try:
        mem_db = sqlite3.connect(":memory:")
        mem_db.executescript(sql_content)
        cursor = mem_db.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [str(row[1]) for row in cursor.fetchall()]
        mem_db.close()
        return columns
    except Exception as e:
        print(f"Error parsing SQL columns for table '{table_name}': {e}")
        return []


def build_tables_config(schemas_dir: Path = SCHEMAS_DIR) -> dict[str, dict[str, Any]]:
    """Dynamically build tables configuration by scanning the schemas directory."""
    tables: dict[str, dict[str, Any]] = {}

    if not schemas_dir.exists():
        print(f"Warning: Schemas directory '{schemas_dir}' not found")
        return tables

    for file_path in sorted(schemas_dir.glob("*.sql")):
        table_name = file_path.stem

        try:
            sql_content = file_path.read_text(encoding="utf-8")
            columns = parse_sql_columns(sql_content, table_name)

            if columns:
                tables[table_name] = {"file": file_path, "columns": columns}
                print(f"Loaded table config for '{table_name}': {columns}")
            else:
                print(f"Warning: Could not parse columns for table '{table_name}'")

        except Exception as e:
            print(f"Error reading SQL file '{file_path}': {e}")

    return tables


def check_database_exists(db_path: Path = DATABASE_PATH) -> bool:
    """Check if the database file exists."""
    return db_path.exists()


def get_table_info(cursor: sqlite3.Cursor, table_name: str) -> list[Any]:
    """Get information about a table's columns."""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        return cursor.fetchall()
    except sqlite3.Error:
        return []


def table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    """Check if a table exists in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def get_expected_tables(tables: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """Return the expected table structure from schema."""
    return {table: config["columns"] for table, config in tables.items()}


def get_table_dependency_order(tables: dict[str, dict[str, Any]]) -> list[str]:
    """Return tables in dependency order for safe creation/deletion."""
    known_order = ["users", "tasks", "tags", "task_tags"]

    for table in tables:
        if table not in known_order:
            known_order.append(table)

    return [table for table in known_order if table in tables]


def verify_database_schema(db: sqlite3.Connection, tables: dict[str, dict[str, Any]]) -> list[str]:
    """Verify that all required tables and columns exist."""
    cursor = db.cursor()
    expected_tables = get_expected_tables(tables)
    missing_tables: list[str] = []

    for table_name, expected_columns in expected_tables.items():
        if not table_exists(cursor, table_name):
            missing_tables.append(table_name)
        else:
            table_info = get_table_info(cursor, table_name)
            existing_columns = [col[1] for col in table_info]

            missing_columns = [col for col in expected_columns if col not in existing_columns]
            if missing_columns:
                print(f"Warning: Table '{table_name}' is missing columns: {missing_columns}")
                missing_tables.append(table_name)

    return missing_tables


def create_database_schema(db: sqlite3.Connection, tables: dict[str, dict[str, Any]]) -> bool:
    """Create the database schema from individual SQL files."""
    try:
        table_order = get_table_dependency_order(tables)

        for table_name in table_order:
            if table_name in tables:
                file_path: Path = tables[table_name]["file"]
                table_schema = file_path.read_text(encoding="utf-8")
                db.executescript(table_schema)

        try:
            index_schema = INDEX_FILE.read_text(encoding="utf-8")
            db.executescript(index_schema)
        except FileNotFoundError:
            print(f"Warning: {INDEX_FILE} not found, skipping index creation")

        return True
    except FileNotFoundError as e:
        print(f"Error: Required SQL file not found: {e}")
        return False
    except sqlite3.Error as e:
        print(f"Error executing schema: {e}")
        return False


def create_missing_tables(
    db: sqlite3.Connection,
    missing_tables: list[str],
    tables: dict[str, dict[str, Any]],
) -> bool:
    """Create missing tables using individual SQL files."""
    try:
        table_order = get_table_dependency_order(tables)

        for table_name in table_order:
            if table_name in missing_tables and table_name in tables:
                file_path: Path = tables[table_name]["file"]
                print(f"Creating table '{table_name}' from {file_path}")

                table_schema = file_path.read_text(encoding="utf-8")
                db.executescript(table_schema)

        try:
            index_schema = INDEX_FILE.read_text(encoding="utf-8")
            db.executescript(index_schema)
        except FileNotFoundError:
            print(f"Warning: {INDEX_FILE} not found, skipping index creation")

        return True
    except FileNotFoundError as e:
        print(f"Error: Required SQL file not found: {e}")
        return False
    except sqlite3.Error as e:
        print(f"Error creating missing tables: {e}")
        return False


def auto_init_db(db_path: Path = DATABASE_PATH) -> bool:
    """
    Automatically initialize the database if needed.
    This function checks if the database exists and has all required tables.
    If not, it creates them without affecting existing data.
    """
    db_existed = check_database_exists(db_path)
    tables = build_tables_config()

    try:
        db = sqlite3.connect(db_path)

        if not db_existed:
            print("Database file not found. Creating new database...")
            if create_database_schema(db, tables):
                print("Database created successfully!")
            else:
                print("Failed to create database!")
                db.close()
                return False
        else:
            missing_tables = verify_database_schema(db, tables)

            if missing_tables:
                print(f"Missing tables detected: {missing_tables}")
                print("Creating missing tables...")

                if create_missing_tables(db, missing_tables, tables):
                    print("Missing tables created successfully!")
                else:
                    print("Failed to create missing tables!")
                    db.close()
                    return False
            else:
                print("Database schema is up to date.")

        db.close()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def init_db(db_path: Path = DATABASE_PATH) -> bool:
    """Initialize the database by dropping existing tables and recreating them."""
    tables = build_tables_config()
    try:
        db = sqlite3.connect(db_path)

        db.executescript(DROP_TABLES_FILE.read_text(encoding="utf-8"))

        if create_database_schema(db, tables):
            db.close()
            print("Database initialized successfully!")
            return True
        else:
            db.close()
            return False

    except FileNotFoundError as e:
        print(f"Error: Required SQL file not found: {e}")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def reset_database(db_path: Path = DATABASE_PATH) -> bool:
    """Reset the database by dropping all tables and recreating them."""
    print("Warning: This will delete all existing data!")
    confirm = input("Are you sure you want to reset the database? (yes/no): ")

    if confirm.lower() in ["yes", "y"]:
        if init_db(db_path):
            print("Database reset completed!")
            return True
        else:
            print("Database reset failed!")
            return False
    else:
        print("Database reset cancelled.")
        return False
