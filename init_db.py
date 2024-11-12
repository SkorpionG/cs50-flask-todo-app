import sqlite3
from database import DB_NAME


def init_db():
    db = sqlite3.connect(DB_NAME)
    with open('schema.sql', 'r', encoding="utf-8") as f:
        db.executescript(f.read())
    db.close()
    print("Database initialized successfully!")


if __name__ == '__main__':
    init_db()
