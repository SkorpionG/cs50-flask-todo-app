from typing import Any

NAV_ITEMS: list[dict[str, Any]] = [
    {
        "name": "Home",
        "url": "main.index",  # Blueprint endpoint name
        "requires_auth": False,
    },
    {"name": "About", "url": "main.about", "requires_auth": False},
]

AUTH_ITEMS: list[dict[str, Any]] = [
    {"name": "Register", "url": "auth.register", "requires_auth": False},
    {"name": "Login", "url": "auth.login", "requires_auth": False},
]

DASHBOARD_TABS: list[dict[str, Any]] = [
    {
        "name": "Home",
        "url": "main.dashboard",
        "icon": "fa-home",
    },
    {
        "name": "Tasks",
        "url": "tasks.tasks",
        "icon": "fa-check-square",
        "children": [
            {
                "name": "New Task",
                "url": "tasks.create_task",
                "icon": "fa-plus",
            }
        ],
    },
    {
        "name": "Tags",
        "url": "tags.tags",
        "icon": "fa-tags",
        "children": [
            {
                "name": "New Tag",
                "url": "tags.create_tag",
                "icon": "fa-plus",
            }
        ],
    },
    {
        "name": "Completed",
        "url": "tasks.completed_tasks",
        "icon": "fa-check-double",
    },
    # {
    #     'name': 'Trash',
    #     'url': 'dashboard',
    #     'icon': 'fa-trash',
    # }
]
