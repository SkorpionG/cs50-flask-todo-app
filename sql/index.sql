create index if not exists idx_tasks_user_id on tasks(user_id);
create index if not exists idx_task_tags_task_id on task_tags(task_id);
create index if not exists idx_task_tags_tag_id on task_tags(tag_id);