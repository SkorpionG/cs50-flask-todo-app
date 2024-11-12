from flask import session, request, redirect, url_for, g
from functools import wraps

# Login required decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def with_context(**method_contexts):
    """
    Decorator that specifies required context data for different HTTP methods.
    Usage:
    @with_context(
        get=['task_priorities', 'task_statuses'],
        post=['user_tags'],
        all=['dashboard_tabs']  # Data needed for all methods
    )
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get method-specific context requirements
            method = request.method.lower()
            required_context = set()

            # Add context required for all methods
            if 'all' in method_contexts:
                required_context.update(method_contexts['all'])

            # Add method-specific context
            if method in method_contexts:
                required_context.update(method_contexts[method])

            # Store in Flask's g object
            g.required_context = required_context
            return f(*args, **kwargs)
        return decorated_function
    return decorator
