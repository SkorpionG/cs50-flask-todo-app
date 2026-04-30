from functools import wraps
from typing import Any, Callable

from flask import g, redirect, request, session, url_for

# Login required decorator


def login_required(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if session.get("user_id") is None:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def with_context(**method_contexts: list[str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator that specifies required context data for different HTTP methods.
    Usage:
    @with_context(
        get=['task_priorities', 'task_statuses'],
        post=['user_tags'],
        all=['dashboard_tabs']  # Data needed for all methods
    )
    """

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Get method-specific context requirements
            method: str = request.method.lower()
            required_context: set[str] = set()

            # Add context required for all methods
            if "all" in method_contexts:
                required_context.update(method_contexts["all"])

            # Add method-specific context
            if method in method_contexts:
                required_context.update(method_contexts[method])

            # Store in Flask's g object
            g.required_context = required_context
            return f(*args, **kwargs)

        return decorated_function

    return decorator
