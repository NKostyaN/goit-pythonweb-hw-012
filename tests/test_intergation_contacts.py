import pytest

# !!! Redis needs to be running !!!

@pytest.fixture
def test_contact_data():
    return {
        "first_name": "Taras",
        "last_name": "Shevchenko",
        "email": "taras.shevchenko@email.com",
        "phone": "380-111-1111",
        "birthday": "1814-03-09",
        "info": "Test contact",
    }


def test_create_contact(client, get_token, test_contact_data):
    response = client.post(
        "/api/contacts",
        json=test_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data
    assert data["first_name"] == "Taras"


def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["first_name"] == "Taras"


def test_get_all_contacts(client, get_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert "id" in data[0]
    assert data[0]["first_name"] == "Taras"


def test_update_contact(client, get_token):
    response = client.patch(
        "/api/contacts/1",
        json={"first_name": "John"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["first_name"] == "John"


def test_find_contact(client, get_token):
    response = client.get(
        "/api/contacts/find/",
        params={"query": "John"},
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert "id" in data[0]
    assert data[0]["first_name"] == "John"


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["first_name"] == "John"
