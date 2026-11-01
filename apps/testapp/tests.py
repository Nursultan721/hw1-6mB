from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import authenticate, get_user_model
from django.core.management import call_command
from django.test import TestCase

from .admin import CustomUserCreationForm


class CustomUserTests(TestCase):
    def test_user_defaults_and_email_authentication(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="client",
            email="client@example.com",
            password="Complex-test-password-483!",
        )

        self.assertEqual(user.role, user_model.Role.CLIENT)
        self.assertFalse(user.is_verified)
        self.assertEqual(user.bio, "")
        self.assertIsNone(user.birth_date)
        self.assertEqual(
            authenticate(email="client@example.com", password="Complex-test-password-483!"),
            user,
        )

    def test_admin_can_create_regular_user(self):
        form = CustomUserCreationForm(
            data={
                "email": "new-client@example.com",
                "username": "new-client",
                "password1": "Complex-test-password-483!",
                "password2": "Complex-test-password-483!",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.role, get_user_model().Role.CLIENT)

    def test_createsuperuser_command(self):
        with patch.dict("os.environ", {"DJANGO_SUPERUSER_PASSWORD": "Complex-test-password-483!"}):
            call_command(
                "createsuperuser",
                email="admin@example.com",
                username="admin",
                interactive=False,
                verbosity=0,
            )

        admin_user = get_user_model().objects.get(email="admin@example.com")
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)

    def test_admin_configuration(self):
        user_admin = admin.site._registry[get_user_model()]

        self.assertEqual(
            user_admin.list_display,
            ("email", "role", "is_verified", "is_active"),
        )
        self.assertEqual(user_admin.list_filter, ("role", "is_verified"))
        self.assertEqual(user_admin.search_fields, ("email", "username"))
        field_names = {
            field
            for _, options in user_admin.fieldsets
            for field in options["fields"]
        }
        self.assertTrue({"bio", "birth_date", "is_verified"}.issubset(field_names))
