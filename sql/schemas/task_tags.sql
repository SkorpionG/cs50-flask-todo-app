create table if not exists task_tags (
    task_id INTEGER not null,
    tag_id INTEGER not null,
    foreign key (task_id) references tasks (id) on delete cascade,
    foreign key (tag_id) references tags (id) on delete cascade,
    primary key (task_id, tag_id)
);