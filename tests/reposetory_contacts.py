from os import getcwd
import sys
import unittest
from unittest.mock import MagicMock, AsyncMock
from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_
from faker import Faker


sys.path.insert(1, getcwd())
from app.models import models
from app.repository.contacts_repo import (
                                        create_contact,
                                        update_contact,
                                        delete_contact,
                                        get_all_contact,
                                        get_contact_with_id,
                                        get_upcoming_birthdays
                                        )
from app import schemas

fake = Faker()


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=Session)
        self.user = models.User(
            id=1,
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
            refresh_token="test",
            avatar=None,
            confirmed=True,
        )

    async def test_create_contact(self):
        """
        Test for app.repository.contacts_repo.create_contact
        """  
        body = schemas.Contact(
            id=1,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone_number=str(fake.phone_number()[:15]),
            birthday=fake.date(),
            owner_id=1
        )
        result = await create_contact(user=self.user, contact=body, db=self.session)
        self.assertIsInstance(result, models.Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)

    async def test_update_contact_with_valid_values(self) -> None:
        """
        Test for app.repository.contacts_repo.update_contact
        """  
        contact = schemas.Contact(
            id=1,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone_number="+380888888888",
            birthday=fake.date(),
            owner_id=1
        )
        body = schemas.ContactBase(
            id=1,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone_number="+380888888888",
            birthday="2000-02-20",
            owner_id=1
        )

        self.session.query().filter().first.return_value = contact
        self.session.commit = MagicMock()

        result = await update_contact(
            contact_id=contact.id, update_body=body, user=self.user, db=self.session
        )

        self.assertEqual(result, contact)
        self.session.commit.assert_called_once()

    async def test_delete_contact_with_valid_values(self) -> None:
        """
        Test for app.repository.contacts_repo.delete_contact
        """  
        contact = schemas.Contact(
            id=1,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone_number="+380888888888",
            birthday=fake.date(),
            owner_id=1
        )
        self.session.query().filter().first.return_value = contact
        self.session.delete = MagicMock(contact)
        self.session.commit = MagicMock()

        result = await delete_contact(contact.id, self.user, self.session)
        self.assertEqual(result, contact)
        self.session.delete.assert_called_once_with(contact)
        self.session.commit.assert_called_once()

    async def test_delete_contact_with_nagative_result(self) -> None:
        """
        Test for app.repository.contacts_repo.delete_contact
        """   
        contact_id = 1
        self.session.query().filter().first.return_value = None
        self.session.delete = MagicMock()
        self.session.commit = MagicMock()
        result = await delete_contact(
            contact_id=contact_id, user=self.user, db=self.session
        )
        self.assertIsNone(result)
        self.session.delete.assert_not_called()
        self.session.commit.assert_not_called()

    async def test_get_contacts(self) -> None:
        """
        Test for app.repository.contacts_repo.get_all_contact
        """   
        contacts = [models.Contact(), models.Contact(), models.Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_all_contact(
            user=self.user, db=self.session
        )
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id(self) -> None:
        """
        Test for app.repository.contacts_repo.get_contact_with_id
        """   
        contact_id = 1
        contact = models.Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_with_id(
            contact_id=contact_id, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_upcoming_birthday(self):
        """
        Test for app.repository.contacts_repo.get_upcoming_birthday
        """        
        today = date(2024, 6, 16)  
        upcoming_birthdays_same_month = [
            models.Contact(birthday=today + timedelta(days=i), owner_id=self.user.id)
            for i in range(1, 4) 
        ]
        upcoming_birthdays_next_month = [
            models.Contact(birthday=today + timedelta(days=i), owner_id=self.user.id)
            for i in range(4, 8) 
        ]
        upcoming_birthdays = (
            upcoming_birthdays_same_month + upcoming_birthdays_next_month
        )

        self.session.query().filter().all.return_value = upcoming_birthdays
        result = await get_upcoming_birthdays(db=self.session, user=self.user)
        self.assertEqual(result, upcoming_birthdays)




    




if __name__ == '__main__':
    unittest.main()