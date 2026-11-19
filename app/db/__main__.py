import sys

from app.db.init_db import auto_init_db, init_db, reset_database


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] == "reset":
            reset_database()
        elif sys.argv[1] == "auto":
            auto_init_db()
        else:
            print("Usage: python -m app.db [reset|auto]")
            print("  reset: Reset the database (WARNING: deletes all data)")
            print("  auto:  Auto-initialize database without deleting existing data")
    else:
        print("Warning: This will delete all existing data and reset the database!")
        confirm = input("Are you sure you want to continue? (yes/no): ")
        if confirm.lower() in ["yes", "y"]:
            init_db()
        else:
            print("Database initialization cancelled.")


if __name__ == "__main__":
    main()
