import glob
import os
import sqlite3
from typing import Any

from database import DB_NAME

# SQL file paths
DROP_TABLES_FILE = "sql/drop_tables.sql"
INDEX_FILE = "sql/index.sql"
SCHEMAS_DIR = "sql/schemas"


def parse_sql_columns(sql_content, table_name):
    """Parse SQL CREATE TABLE statement to extract column names by executing it in memory."""
    try:
        mem_db = sqlite3.connect(":memory:")
        mem_db.executescript(sql_content)
        cursor = mem_db.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        mem_db.close()
        return columns
    except Exception as e:
        print(f"Error parsing SQL columns for table '{table_name}': {e}")
        return []


def build_tables_config() -> dict[str, Any]:
    """Dynamically build TABLES configuration by scanning the schemas directory."""
    tables: dict[str, Any] = {}

    if not os.path.exists(SCHEMAS_DIR):
        print(f"Warning: Schemas directory '{SCHEMAS_DIR}' not found")
        return tables

    # Get all .sql files in the schemas directory
    sql_files = glob.glob(os.path.join(SCHEMAS_DIR, "*.sql"))

    for file_path in sql_files:
        # Extract table name from filename
        filename = os.path.basename(file_path)
        table_name = os.path.splitext(filename)[0]

        try:
            # Read and parse the SQL file to get columns
            with open(file_path, "r", encoding="utf-8") as f:
                sql_content = f.read()

            columns = parse_sql_columns(sql_content, table_name)

            if columns:
                tables[table_name] = {"file": file_path, "columns": columns}
                print(f"Loaded table config for '{table_name}': {columns}")
            else:
                print(f"Warning: Could not parse columns for table '{table_name}'")

        except Exception as e:
            print(f"Error reading SQL file '{file_path}': {e}")

    return tables


# Dynamically build TABLES configuration
TABLES = build_tables_config()


def check_database_exists() -> bool:
    """Check if the database file exists."""
    return os.path.exists(DB_NAME)


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


def get_expected_tables() -> dict[str, list[str]]:
    """Return the expected table structure from schema."""
    return {table: config["columns"] for table, config in TABLES.items()}


def get_table_dependency_order() -> list[str]:
    """Return tables in dependency order for safe creation/deletion."""
    # Define dependency order manually for foreign key constraints
    # This could be made dynamic by parsing foreign key relationships
    known_order = ["users", "tasks", "tags", "task_tags"]

    # Add any dynamically discovered tables that aren't in known_order
    all_tables = list(TABLES.keys())
    for table in all_tables:
        if table not in known_order:
            known_order.append(table)

    # Filter to only include tables that actually exist in TABLES
    return [table for table in known_order if table in TABLES]


def verify_database_schema(db: sqlite3.Connection) -> list[str]:
    """Verify that all required tables and columns exist."""
    cursor = db.cursor()
    expected_tables = get_expected_tables()
    missing_tables = []

    for table_name, expected_columns in expected_tables.items():
        if not table_exists(cursor, table_name):
            missing_tables.append(table_name)
        else:
            # Check if all expected columns exist
            table_info = get_table_info(cursor, table_name)
            existing_columns = [
                col[1]
                # col[1] is the column name
                for col in table_info
            ]

            missing_columns = [col for col in expected_columns if col not in existing_columns]
            if missing_columns:
                print(f"Warning: Table '{table_name}' is missing columns: {missing_columns}")
                missing_tables.append(table_name)

    return missing_tables


def create_database_schema(db: sqlite3.Connection) -> bool:
    """Create the database schema from individual SQL files."""
    try:
        # Create tables in dependency order
        table_order = get_table_dependency_order()

        for table_name in table_order:
            if table_name in TABLES:
                file_path = TABLES[table_name]["file"]
                with open(file_path, "r", encoding="utf-8") as f:
                    table_schema = f.read()
                db.executescript(table_schema)

        # Create indexes
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                index_schema = f.read()
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


def create_missing_tables(db: sqlite3.Connection, missing_tables: list[str]) -> bool:
    """Create missing tables using individual SQL files."""
    try:
        # Create tables in dependency order to respect foreign key constraints
        table_order = get_table_dependency_order()

        for table_name in table_order:
            if table_name in missing_tables and table_name in TABLES:
                file_path = TABLES[table_name]["file"]
                print(f"Creating table '{table_name}' from {file_path}")

                with open(file_path, "r", encoding="utf-8") as f:
                    table_schema = f.read()
                db.executescript(table_schema)

        # Create indexes for missing tables
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                index_schema = f.read()
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


def auto_init_db() -> bool:
    """
    Automatically initialize the database if needed.
    This function checks if the database exists and has all required tables.
    If not, it creates them without affecting existing data.
    """
    db_existed = check_database_exists()

    try:
        db = sqlite3.connect(DB_NAME)

        if not db_existed:
            print("Database file not found. Creating new database...")
            if create_database_schema(db):
                print("Database created successfully!")
            else:
                print("Failed to create database!")
                return False
        else:
            # Check if all required tables exist
            missing_tables = verify_database_schema(db)

            if missing_tables:
                print(f"Missing tables detected: {missing_tables}")
                print("Creating missing tables...")

                if create_missing_tables(db, missing_tables):
                    print("Missing tables created successfully!")
                else:
                    print("Failed to create missing tables!")
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


def init_db() -> bool:
    """Initialize the database by dropping existing tables and recreating them."""
    try:
        db = sqlite3.connect(DB_NAME)

        # First drop all tables and indexes
        with open(DROP_TABLES_FILE, "r", encoding="utf-8") as f:
            db.executescript(f.read())

        # Then create the schema
        if create_database_schema(db):
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


def reset_database() -> bool:
    """Reset the database by dropping all tables and recreating them."""
    print("Warning: This will delete all existing data!")
    confirm = input("Are you sure you want to reset the database? (yes/no): ")

    if confirm.lower() in ["yes", "y"]:
        if init_db():
            print("Database reset completed!")
            return True
        else:
            print("Database reset failed!")
            return False
    else:
        print("Database reset cancelled.")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "reset":
            reset_database()
        elif sys.argv[1] == "auto":
            auto_init_db()
        else:
            print("Usage: python init_db.py [reset|auto]")
            print("  reset: Reset the database (WARNING: deletes all data)")
            print("  auto:  Auto-initialize database without deleting existing data")
    else:
        # Default behavior - full initialization with confirmation
        print("Warning: This will delete all existing data and reset the database!")
        confirm = input("Are you sure you want to continue? (yes/no): ")
        if confirm.lower() in ["yes", "y"]:
            init_db()
        else:
            print("Database initialization cancelled.")
