from flask import Flask
from flask.testing import FlaskClient

from app.db import task_priority_options, task_status_options


def _register_and_login(client: FlaskClient) -> None:
    response = client.post(
        "/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password1!",
            "confirm-password": "Password1!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_public_routes_and_static_assets(client: FlaskClient) -> None:
    for path in ["/", "/home", "/about", "/login", "/register", "/forgot-password", "/static/assets/logo.svg"]:
        response = client.get(path)
        assert response.status_code == 200, f"{path} returned {response.status_code}"


def test_protected_routes_redirect_when_unauthenticated(client: FlaskClient) -> None:
    for path in ["/dashboard", "/tasks", "/tasks/create", "/tasks/completed", "/tags", "/tags/create", "/settings"]:
        response = client.get(path)
        assert response.status_code == 302
        assert "/login" in response.location


def test_schema_constraints_loaded(app: Flask, client: FlaskClient) -> None:
    client.get("/")
    with app.app_context():
        assert task_priority_options() == ["High", "Medium", "Low"]
        assert task_status_options() == ["Pending", "In Progress", "Completed"]


def test_tags_and_tasks_crud_lifecycle(client: FlaskClient) -> None:
    _register_and_login(client)

    # Create tag and inspect API endpoints
    response = client.post("/tags/create", data={"name": "work", "color": "#ff0000"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"work" in response.data

    tags_resp = client.get("/api/user/tags")
    assert tags_resp.status_code == 200
    tags = tags_resp.get_json()
    assert len(tags) == 1
    tag_id = tags[0]["id"]

    search_resp = client.get("/api/user/tags/search?tag=work")
    assert search_resp.status_code == 200
    assert search_resp.get_json()["count"] == 1

    # Edit tag
    assert client.get(f"/tags/{tag_id}/edit").status_code == 200
    response = client.post(
        f"/tags/{tag_id}/edit",
        data={"name": "office", "color": "#00ff00"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Create task with tag
    response = client.post(
        "/tasks/create",
        data={
            "title": "Finish tests",
            "description": "Add automated test coverage",
            "due-date": "2027-01-01T12:00",
            "priority": "High",
            "status": "Pending",
            "tags[]": [str(tag_id)],
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Finish tests" in response.data

    # Dashboard renders upcoming task and updated tag
    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b"Finish tests" in dashboard.data
    assert b"office" in dashboard.data

    # Edit task and transition to Completed
    assert client.get("/tasks/1/edit").status_code == 200
    response = client.post(
        "/tasks/1/edit",
        data={
            "title": "Finish tests v2",
            "description": "Updated",
            "due-date": "2027-01-02T12:00",
            "priority": "Medium",
            "status": "In Progress",
            "tags[]": [str(tag_id)],
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Finish tests v2" in response.data

    response = client.post(
        "/tasks/1/status",
        data={"task-id": "1", "status": "Completed"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Finish tests v2" in response.data

    # Delete task & tag
    assert client.post("/tasks/1/delete", data={"task-id": "1"}, follow_redirects=True).status_code == 200
    assert client.post(f"/tags/{tag_id}/delete", data={"tag-id": str(tag_id)}, follow_redirects=True).status_code == 200


def test_settings_and_auth_lifecycle(client: FlaskClient) -> None:
    _register_and_login(client)

    # Update profile
    response = client.post(
        "/settings/profile",
        data={"username": "alice2", "email": "alice2@example.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"alice2" in response.data

    # Reject weak password
    response = client.post(
        "/settings/password",
        data={
            "current-password": "Password1!",
            "new-password": "weak",
            "confirm-password": "weak",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Password must be at least 8 characters long" in response.data

    # Accept valid password update
    response = client.post(
        "/settings/password",
        data={
            "current-password": "Password1!",
            "new-password": "NewPassword2@",
            "confirm-password": "NewPassword2@",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Password updated successfully" in response.data

    # Logout and login with new password
    assert client.get("/logout", follow_redirects=True).status_code == 200
    response = client.post(
        "/login",
        data={"email": "alice2@example.com", "password": "NewPassword2@"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Dashboard" in response.data

    # Delete account
    response = client.post(
        "/settings/delete-account",
        data={"delete-account-password": "NewPassword2@"},
        follow_redirects=True,
    )
    assert response.status_code == 200
