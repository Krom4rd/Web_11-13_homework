import os
import sys
sys.path.insert(1, os.getcwd())
from unittest.mock import MagicMock, patch
from time import sleep

from pytest import mark, fixture
from fastapi import status

from app.models import models
from app.services.auth import auth_service, Hash

hash_handler = Hash()

@fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("app.services.email.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: models.User = (
        session.query(models.User).filter(models.User.email == user.get('email')).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]

@mark.usefixtures("mock_rate_limit")
def test_add_new_contact(client, token):
    """
    Test for method "Post", function app.rotes.contacts.add_new_contact
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/contact",
            json={"first_name": "Oleh",
                  "last_name": "Novosad",
                  "email": "test@test.net",
                  "phone_number": "777777777777",
                  "birthday": "1996-06-20",
                  "additional_info": "Test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        assert data["first_name"] == "Oleh"
        assert data["last_name"] == "Novosad"
        assert data["email"] == "test@test.net"
        assert data["phone_number"] == "777777777777"
        assert data["birthday"] == "1996-06-20"
        assert data["additional_info"] == "Test"

@mark.usefixtures("mock_rate_limit")
def test_get_contact(client, token):
    """
    Test for method "get", function app.rotes.contacts.get_contact_by_id
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contact/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["first_name"] == "Oleh"
        assert data["last_name"] == "Novosad"
        assert data["email"] == "test@test.net"
        assert data["phone_number"] == "777777777777"
        assert data["birthday"] == "1996-06-20"
        assert data["additional_info"] == "Test"
        assert "id" in data

@mark.usefixtures("mock_rate_limit")
def test_get_contacts(client, token):
    """
    Test for method "get", function app.rotes.contacts.all_contacts
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contact",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["first_name"] == "Oleh"
        assert data[0]["last_name"] == "Novosad"
        assert data[0]["email"] == "test@test.net"
        assert data[0]["phone_number"] == "777777777777"
        assert data[0]["birthday"] == "1996-06-20"
        assert data[0]["additional_info"] == "Test"
        assert "id" in data[0]


@mark.usefixtures("mock_rate_limit")
def test_get_upcoming_birthdays(client, token):
    """
    Test for method "get", function app.rotes.contacts.get_upcoming_birthdays
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contact/birthdays",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["first_name"] == "Oleh"
        assert data[0]["last_name"] == "Novosad"
        assert data[0]["email"] == "test@test.net"
        assert data[0]["phone_number"] == "777777777777"
        assert data[0]["birthday"] == "1996-06-20"
        assert data[0]["additional_info"] == "Test"
        assert "id" in data[0]


@mark.usefixtures("mock_rate_limit")
def test_update_contact(client, token):
    """
    Test for method "get", function app.rotes.contacts.update_contact
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(
            "/api/contact/1",
            json={"first_name": "Olena",
                  "last_name": "Safiian",
                  "email": "new_email@test.net",
                  "phone_number": "123123123",
                  "birthday": "1998-05-24",
                  "additional_info": "String"},
            headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["first_name"] == "Olena"
        assert data["email"] == "new_email@test.net"
        assert data["birthday"] == "1998-05-24"
        assert data["additional_info"] == "String"
        assert "id" in data

@mark.usefixtures("mock_rate_limit")
def test_delete_contact(client, token):
    """
    Test for method "get", function app.rotes.contacts.delete_contact
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contact/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["first_name"] == "Olena"
        assert data["last_name"] == "Novosad"
        assert data["email"] == "new_email@test.net"
        assert data["phone_number"] == "777777777777"
        assert data["birthday"] == "1998-05-24"
        assert data["additional_info"] == "String"
        assert "id" in data



