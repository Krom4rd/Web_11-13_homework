from os import getcwd
import sys
import unittest
from unittest.mock import AsyncMock

from sqlalchemy.orm import Session
sys.path.insert(1, getcwd())

from app.models import models
from app.repository.auth_repo import (get_user_by_email,
                                      create_user,
                                      update_password,
                                      update_avatar
                                      )
from app.schemas import UserCreate


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=Session)
        self.user = models.User(
            id=1,
            username="python",
            email="pyton@study.com",
            confirmed=True,
            refresh_token="test"
        )

    async def test_get_user_by_email(self) -> None:
        """
        Test for app.repository.auth_repo.get_user_by_email
        """
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertEqual(result, self.user)

    async def test_create_user(self) -> None:
        """
        Test for app.repository.auth_repo.create_user
        """
        new_user = UserCreate(
            username="testuser",
            email="newuser@test.py",
            password="userpassword"
        )
        self.session.query().filter_by().first.return_value = None

        result = await create_user(body=new_user, db=self.session)

        self.assertEqual(result.username, new_user.username)
        self.assertEqual(result.email, new_user.email)
        self.assertEqual(result.password, new_user.password)

    async def test_update_password(self) -> None:
        """
        Test for app.repository.auth_repo.update_password
        """        
        new_password = "newpassword"

        result = await update_password(self.user, new_password, self.session)

        self.assertEqual(self.user.password, new_password)

    async def test_update_avatar(self) -> None:
        """
        Test for app.repository.auth_repo.update_avatar
        """        
        new_avatar_url = "test_url"

        result = await update_avatar(self.user, new_avatar_url, self.session)

        self.assertEqual(new_avatar_url, self.user.avatar)







if __name__ == '__main__':
    unittest.main()
