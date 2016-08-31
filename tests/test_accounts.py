import os
from datetime import date

from django.core import mail
from django.conf import settings
from django_webtest import WebTest
from django.contrib.auth import get_user_model

from twitter.models import ValidationToken

User = get_user_model()


class AccountsTestCase(WebTest):
    def setUp(self):
        self.user = User.objects.create_user(
            username='larrypage', first_name='Larry', last_name='Page',
            email='lpage@google.com', birth_date=date(1992, 7, 6),
            password='password123')

    def test_register(self):
        """Should create an inactive user and send validation url by email"""
        # Preconditions
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(ValidationToken.objects.count(), 0)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='sergeybrin')
        self.assertEqual(len(mail.outbox), 0)

        register = self.app.get('/register')
        form = register.form
        form['username'] = 'sergeybrin'
        form['password'] = 'password123'
        form['first_name'] = 'Sergey'
        form['last_name'] = 'Brin'
        form['email'] = 'sbrin@google.com'
        form['birth_date'] = '1973-8-21'
        form.submit()

        # Postconditions
        self.assertEqual(User.objects.count(), 2)
        user = User.objects.get(username='sergeybrin')
        self.assertEqual(user.username, 'sergeybrin')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(user.first_name, 'Sergey')
        self.assertEqual(user.last_name, 'Brin')
        self.assertEqual(user.email, 'sbrin@google.com')
        self.assertEqual(user.birth_date, date(1973, 8, 21))
        self.assertFalse(user.is_active)
        self.assertFalse(user.email_validated)

        self.assertEqual(ValidationToken.objects.count(), 1)
        self.assertTrue(
            ValidationToken.objects.filter(email='sbrin@google.com').exists())

        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body
        token = ValidationToken.objects.get(email='sbrin@google.com')
        expected = ("Thanks for registering. To complete the process, please "
                    "click in the link below: "
                    "http://twitter.com/users/validate/{}".format(token.token))
        self.assertEqual(email_body, expected)

    def test_validate_user(self):
        """Should validate user after clicking in email sending by email"""
        # Preconditions
        User.objects.create_user(
            username='sergeybrin', password='password123', email='sbrin@google.com',
            is_active=False, email_validated=False)
        token = ValidationToken.objects.create(
            email='sbrin@google.com', token='a' * 16)
        self.assertEqual(ValidationToken.objects.count(), 1)

        self.app.get('/users/validate/{}'.format(token.token))

        # Postconditions
        user = User.objects.get(username='sergeybrin')
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_validated)
        self.assertEqual(ValidationToken.objects.count(), 0)


    def test_change_password(self):
        """Should change password of authenticated user when given data is valid"""
        # Preconditions
        self.assertTrue(self.user.check_password('password123'))
        self.assertFalse(self.user.check_password('newpassword123'))

        response = self.app.get('/users/change-password', user=self.user)
        form = response.form
        form['old_password'] = 'password123'
        form['new_password'] = 'newpassword123'
        form['repeated_new_password'] = 'newpassword123'
        form.submit()

        # Postconditions
        user = User.objects.get(username=self.user.username)
        self.assertTrue(user.check_password('newpassword123'))
        self.assertFalse(user.check_password('password123'))


    def test_reset_password(self):
        """Should send password recovery url by email to given address"""
        self.assertEqual(ValidationToken.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

        response = self.app.get('/users/reset-password')
        form = response.form
        form['email'] = 'lpage@google.com'
        form.submit()

        # Postconditions
        self.assertEqual(ValidationToken.objects.count(), 1)
        self.assertTrue(
            ValidationToken.objects.filter(email='lpage@google.com').exists())
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body
        token = ValidationToken.objects.get(email='lpage@google.com')
        expected = ("To reset your password, please click in the link below: "
                    "http://twitter.com/users/confirm-reset-password/{}".format(token.token))
        self.assertEqual(email_body, expected)

    def test_confirm_reset_password(self):
        """Should reset users password when given data is valid"""
        # Preconditions
        self.assertTrue(self.user.check_password('password123'))
        self.assertFalse(self.user.check_password('newpassword123'))
        token = ValidationToken.objects.create(
            email='lpage@google.com', token='a' * 16)
        self.assertEqual(ValidationToken.objects.count(), 1)

        response = self.app.get(
            '/users/confirm-reset-password/{}'.format(token.token))
        form = response.form
        form['new_password'] = 'newpassword123'
        form['repeated_new_password'] = 'newpassword123'
        form.submit()

        # Postconditions
        user = User.objects.get(username=self.user.username)
        self.assertTrue(user.check_password('newpassword123'))
        self.assertFalse(user.check_password('password123'))
        self.assertEqual(ValidationToken.objects.count(), 0)
