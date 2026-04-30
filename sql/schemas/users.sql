create table if not exists users (
    id INTEGER primary key AUTOINCREMENT,
    username TEXT not null,
    email TEXT unique not null,
    password_hash TEXT not null,
    created_at TIMESTAMP default current_timestamp
);