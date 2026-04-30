create table if not exists tasks (
    id INTEGER primary key AUTOINCREMENT,
    user_id INTEGER not null,
    title TEXT not null,
    description TEXT,
    due_date DATETIME,
    priority TEXT check(priority in ('High', 'Medium', 'Low')) not null,
    status TEXT check(
        status in ('Pending', 'In Progress', 'Completed')
    ) not null default 'Pending',
    created_at TIMESTAMP default current_timestamp,
    modified_at TIMESTAMP default current_timestamp,
    foreign key (user_id) references users (id)
);