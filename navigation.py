NAV_ITEMS = [
    {
        'name': 'Home',
        'url': 'index',  # should be name of the route function
        'requires_auth': False
    },
    {
        'name': 'About',
        "url": "about",
        'requires_auth': False
    }
]

AUTH_ITEMS = [
    {
        'name': 'Register',
        'url': 'register',
        'requires_auth': False
    },
    {
        'name': 'Login',
        'url': 'login',
        'requires_auth': False
    }
]

DASHBOARD_TABS = [
    {
        'name': 'Home',
        'url': 'dashboard',
        'icon': 'fa-home',
    },
    {
        'name': 'Tasks',
        'url': 'tasks.tasks',
        'icon': 'fa-check-square',
        'children': [
            {
                'name': 'New Task',
                'url': 'tasks.create_task',
                'icon': 'fa-plus',
            }
        ]
    },
    {
        'name': 'Tags',
        'url': 'tags.tags',
        'icon': 'fa-tags',
        'children': [
            {
                'name': 'New Tag',
                'url': 'tags.create_tag',
                'icon': 'fa-plus',
            }
        ]
    },
    {
        'name': 'Completed',
        'url': 'tasks.completed_tasks',
        'icon': 'fa-check-double',
    }
    # {
    #     'name': 'Trash',
    #     'url': 'dashboard',
    #     'icon': 'fa-trash',
    # }
]
