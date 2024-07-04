from django.test import TestCase
from django.contrib.auth import get_user_model

class ProfileUserTests(TestCase):

    # helper methods

    def create_user_and_assert_common_fields(self, test_superuser=False):
        USERNAME = 'test_user'
        EMAIL = 'test@test.com'
        FIRST_NAME = 'test_first'
        LAST_NAME = 'test_last'
        AVATAR_NAME = 'test.png'

        user_model = get_user_model()
        user_create_func = user_model.objects.create_superuser if test_superuser else user_model.objects.create_user
        user = user_create_func(USERNAME, email=EMAIL, first_name=FIRST_NAME, last_name=LAST_NAME, avatar=AVATAR_NAME)

        self.assertEqual(user.get_full_name(), f'{FIRST_NAME} {LAST_NAME}')
        self.assertEqual(user.username, USERNAME)
        self.assertEqual(user.get_username(), EMAIL)
        self.assertEqual(user.avatar.name, AVATAR_NAME)

        self.assertTrue(user.is_authenticated)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)

        return user

    # tests

    def test_create_user(self):
        user = self.create_user_and_assert_common_fields()

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = self.create_user_and_assert_common_fields(test_superuser=True)

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
