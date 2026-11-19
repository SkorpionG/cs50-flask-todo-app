from datetime import datetime
from typing import Any

from flask import Flask, current_app, g, request, session, url_for

from app.db import (
    get_tag_columns,
    get_task_columns,
    get_user_tags,
    task_priority_options,
    task_status_options,
)
from app.navigation import DASHBOARD_TABS, NAV_ITEMS


def format_datetime(value: Any, format: str = "%d/%m/%Y %H:%M %p") -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            if "T" in value:  # ISO format
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M")
            else:
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return str(value)
    return str(value.strftime(format))


def _build_task_action_info(status_options: list[str]) -> dict[str, dict[str, str]]:
    action_info: dict[str, dict[str, str]] = {status: {} for status in status_options}
    for task_action in action_info:
        if task_action == "In Progress":
            action_info[task_action]["color"] = "btn-info"
            action_info[task_action]["icon"] = " fa-clock"
        elif task_action == "Pending":
            action_info[task_action]["color"] = "btn-warning"
            action_info[task_action]["icon"] = " fa-undo"
        elif task_action == "Completed":
            action_info[task_action]["color"] = "btn-success"
            action_info[task_action]["icon"] = " fa-check"
    return action_info


def _get_schema_metadata() -> dict[str, Any]:
    """Lazily compute and cache schema-derived metadata per Flask app instance."""
    metadata: dict[str, Any] | None = current_app.extensions.get("schema_metadata")
    if metadata is None:
        status_options = task_status_options()
        metadata = {
            "task_priority_options": task_priority_options(),
            "task_status_options": status_options,
            "tag_columns": get_tag_columns(),
            "task_columns": get_task_columns(),
            "task_action_info": _build_task_action_info(status_options),
        }
        current_app.extensions["schema_metadata"] = metadata
    return metadata


def get_nav_links() -> list[dict[str, Any]]:
    nav_links = []
    for item in NAV_ITEMS:
        if item["requires_auth"] and not session.get("user_id"):
            continue

        nav_links.append({"name": item["name"], "url": url_for(item["url"]), "active": request.endpoint == item["url"]})
    return nav_links


def get_context_data(data_type: str) -> Any:
    """Helper function to get specific context data for the current request."""
    if not hasattr(g, "context_cache"):
        g.context_cache = {}

    if data_type in g.context_cache:
        return g.context_cache[data_type]

    data: Any = None
    if session.get("user_id"):
        metadata = _get_schema_metadata()
        if data_type == "task_priority_options":
            data = metadata["task_priority_options"]
        elif data_type == "task_status_options":
            data = metadata["task_status_options"]
        elif data_type == "user_tags":
            data = get_user_tags(session["user_id"])
        elif data_type == "tag_columns":
            data = metadata["tag_columns"]
        elif data_type == "task_columns":
            data = metadata["task_columns"]
        elif data_type == "dashboard_tabs":
            data = DASHBOARD_TABS

    g.context_cache[data_type] = data
    return data


def load_app_context() -> dict[str, Any]:
    nav_links = get_nav_links()
    return {"nav_links": nav_links, "is_authenticated": session.get("user_id")}


def load_authenticated_context() -> dict[str, Any]:
    if not session.get("user_id"):
        return {}
    metadata = _get_schema_metadata()
    context: dict[str, Any] = {
        "dashboard_tabs": DASHBOARD_TABS,
        "task_action_info": metadata["task_action_info"],
    }
    if hasattr(g, "required_context"):
        for data_type in g.required_context:
            data = get_context_data(data_type)
            if data is not None:
                context[data_type] = data

    return context


def register_context(app: Flask) -> None:
    """Register template filters and context processors on the Flask application."""
    app.template_filter("format_datetime")(format_datetime)
    app.context_processor(load_app_context)
    app.context_processor(load_authenticated_context)
