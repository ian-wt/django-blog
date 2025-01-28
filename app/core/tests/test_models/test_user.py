from django.test import TestCase
from django.db import IntegrityError

import factory

from ...models import User, UserProfile
from ..factories import UserFactory

class TestUser(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        # make sure multiple user object creations don't collide
        self.user = UserFactory()

    def test_create_user(self):
        first_name = 'John'
        last_name = 'Doe'
        email = f'{first_name}.{last_name}@example.com'

        # confirm user isn't already in the system
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=email)

        user = User.objects.create_user(
            email=email,
            **{
                'first_name': first_name,
                'last_name': last_name
            }
        )

        # check user is appropriately created
        user_query = User.objects.filter(email=email)
        self.assertTrue(
            user_query.exists()
        )
        self.assertEqual(user, user_query[0])

        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        # make sure different than create_user or we'll get a conflict
        first_name = 'Jane'
        last_name = 'Doe'
        email = f'{first_name}.{last_name}@example.com'

        # confirm user isn't already in the system
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=email)

        user = User.objects.create_superuser(
            email=email,
            **{
                'first_name': first_name,
                'last_name': last_name
            }
        )

        # check user is appropriately created
        user_query = User.objects.filter(email=email)
        self.assertTrue(
            user_query.exists()
        )
        self.assertEqual(user, user_query[0])

        self.assertTrue(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_user_str_method(self):
        self.assertEqual(
            str(self.user),
            self.user.email
        )

    def test_get_full_name(self):
        self.assertEqual(
            self.user.get_full_name(),
            f'{self.user.first_name} {self.user.last_name}'
        )

    def test_get_user_initials(self):
        self.assertEqual(
            self.user.get_user_initials(),
            '{}{}'.format(
                self.user.first_name[0].upper(),
                self.user.last_name[0].upper()
            )
        )

    def test_unique_user(self):
        user_data = factory.build(dict, FACTORY_CLASS=UserFactory)
        _ = User.objects.create(**user_data)
        with self.assertRaises(IntegrityError):
            _ = User.objects.create(**user_data)

    def test_user_has_profile(self):
        self.assertTrue(
            hasattr(self.user, 'user_profile')
        )
        self.assertIsInstance(self.user.user_profile, UserProfile)
