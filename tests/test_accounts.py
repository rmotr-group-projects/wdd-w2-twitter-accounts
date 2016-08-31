import os
from datetime import date

from django.conf import settings
from django_webtest import WebTest
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsTestCase(WebTest):
    def setUp(self):
        self.user = User.objects.create_user(
            username='larrypage', first_name='Larry', last_name='Page',
            email='larrypage@twitter.com', birth_date=date(1992, 7, 6),
            password='coffee')

    def test_update_user_profile(self):
        """Should update user profile when given data is valid"""
        # Preconditions
        self.assertEqual(self.user.username, 'larrypage')
        self.assertEqual(self.user.first_name, 'Larry')
        self.assertEqual(self.user.last_name, 'Page')
        self.assertEqual(self.user.birth_date, date(1992, 7, 6))
        self.assertEqual(self.user.avatar, None)

        profile = self.app.get('/profile', user=self.user)
        form = profile.form
        form['username'] = 'sergeybrin'
        form['first_name'] = 'Sergey'
        form['last_name'] = 'Brin'
        form['birth_date'] = '1988-4-25'
        avatar_url = os.path.join(
            settings.BASE_DIR, 'twitter/static/img/sample.jpg')
        form.submit(
            upload_files=[('avatar', avatar_url)]
        )

        # Postconditions
        updated_user = User.objects.get(username='larrypage')
        self.assertEqual(updated_user.username, 'larrypage')
        self.assertEqual(updated_user.first_name, 'Sergey')
        self.assertEqual(updated_user.last_name, 'Brin')
        self.assertEqual(updated_user.birth_date, date(1988, 4, 25))
        self.assertEqual(updated_user.avatar.url, '/media/avatars/sample.jpg')

        os.remove(os.path.join(
            settings.BASE_DIR, 'twitter/media/avatars/sample.jpg'))

    def test_cant_update_username(self):
        """Should not update the user's username"""
        # Preconditions
        self.assertEqual(self.user.username, 'larrypage')

        profile = self.app.get('/profile', user=self.user)
        form = profile.form
        form['username'] = 'sergeybrin'
        form.submit()
        User.objects.get(username='larrypage')
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='sergeybrin')

    def test_update_user_profile_invalid_data(self):
        """Should not update user profile when given data is invalid"""
        # Preconditions
        self.assertEqual(self.user.username, 'larrypage')

        profile = self.app.get('/profile', user=self.user)
        form = profile.form
        form['birth_date'] = 123
        with self.assertRaises(TypeError) as e:
            form.submit()
        User.objects.get(username='larrypage')

    def test_update_user_profile_unauthenticated(self):
        """Should return 302 and redirect to login template when user is unauthenticated"""
        response = self.app.get('/profile')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login?next=/profile'))
