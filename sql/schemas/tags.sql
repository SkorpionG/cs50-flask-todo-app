create table if not exists tags (
    id INTEGER primary key AUTOINCREMENT,
    user_id INTEGER not null,
    name TEXT not null,
    color TEXT default '#6c757d' not null,
    created_at TIMESTAMP default current_timestamp,
    unique(user_id, name),
    foreign key (user_id) references users (id)
);