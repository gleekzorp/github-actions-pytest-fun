import pytest


@pytest.mark.todos
def test_create_new_todo(login, client):
    # Arrange
    url = '/create-todo'
    payload = {
        "title": "Buy Milk",
        "complete": False
    }
    headers = {
        "Authorization": f"Bearer {login['access_token']}"
    }

    # Act
    response = client.post(url, headers=headers, json=payload)
    body = response.json()

    # Assert
    assert response.status_code == 200
    assert body['title'] == 'Buy Milk'
    assert body['complete'] == False
    assert body['id'] == 1
    assert body['owner_id'] == 1


@pytest.mark.todos
def test_create_new_todo_raises_not_authenticated(client):
    # Arrange
    url = '/create-todo'
    payload = {
        "title": "Buy Milk",
        "complete": False
    }

    # Act
    response = client.post(url, json=payload)
    body = response.json()

    # Assert
    assert response.status_code == 401
    assert body["detail"] == "Not authenticated"


@pytest.mark.todos
def test_get_user_todos_has_todos(login, client, create_single_todo):
    # Arrange
    url = "/get-todos"
    headers = {
        "Authorization": f"Bearer {login['access_token']}"
    }

    # Act
    response = client.get(url, headers=headers)
    body = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(body['todos'], list)
    assert len(body['todos']) == 1


@pytest.mark.todos
def test_mark_todo_complete(login, client, create_single_todo):
    url = f"/toggle-complete/{create_single_todo.id}"
    headers = {
        "Authorization": f"Bearer {login['access_token']}"
    }

    response = client.patch(url, headers=headers)
    body = response.json()
    assert response.status_code == 200
    assert body["complete"] is True


@pytest.mark.todos
def test_toggle_todo_complete_to_uncomplete(login, client, create_single_todo):
    url = f"/toggle-complete/{create_single_todo.id}"
    headers = {
        "Authorization": f"Bearer {login['access_token']}"
    }

    response = client.patch(url, headers=headers)
    body = response.json()
    assert response.status_code == 200
    assert body["complete"] is True

    second_response = client.patch(url, headers=headers)
    second_body = second_response.json()
    assert second_response.status_code == 200
    assert second_body["complete"] is False


@pytest.mark.todos
def test_user_marks_second_user_todo_complete_raises_error(client, create_single_todo):
    # Create Second User
    second_user_url = '/create-user'
    second_user_payload = {
        "username": "test2",
        "password": "test2"
    }
    client.post(second_user_url, json=second_user_payload)

    # Login Second User
    second_user_login_url = "/login"
    second_user_login_response = client.post(second_user_login_url, data=second_user_payload)
    second_user_login_body = second_user_login_response.json()
    second_user_headers = {
        "Authorization": f"Bearer {second_user_login_body['access_token']}"
    }

    # Mark first users first todo complete
    toggle_complete_url = f"/toggle-complete/{create_single_todo.id}"
    toggle_complete_response = client.patch(toggle_complete_url, headers=second_user_headers)
    toggle_complete_body = toggle_complete_response.json()

    assert toggle_complete_body["detail"] == "Not authenticated"


@pytest.mark.todos
def test_mark_todo_complete_raises_not_authenticated(client, create_single_todo):
    url = f"/toggle-complete/{create_single_todo.id}"

    response = client.patch(url)
    body = response.json()

    assert response.status_code == 401
    assert body["detail"] == "Not authenticated"
