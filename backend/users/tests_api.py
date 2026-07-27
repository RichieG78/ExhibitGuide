from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class UserApiProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='collector',
            email='collector@example.com',
            password='StrongPass123!',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_profile_get_returns_user_data(self):
        response = self.client.get('/api/auth/profile/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'collector')
        self.assertEqual(response.data['email'], 'collector@example.com')

    def test_profile_patch_updates_user_and_profile(self):
        response = self.client.patch(
            '/api/auth/profile/',
            {
                'username': 'collector-updated',
                'email': 'updated@example.com',
                'first_name': 'Ada',
                'last_name': 'Lovelace',
                'phone': '+3538888888',
                'bio': 'Collector of modern art',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'collector-updated')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.first_name, 'Ada')
        self.assertEqual(self.user.last_name, 'Lovelace')
        self.assertEqual(self.user.profile.phone, '+3538888888')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    FRONTEND_URL='http://localhost:5173',
)
class UserApiPasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='reset-user',
            email='reset@example.com',
            password='OldPass123!',
        )
        self.client = APIClient()

    def test_password_reset_request_sends_link(self):
        response = self.client.post('/api/auth/password-reset/', {'email': 'reset@example.com'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/reset-password?uid=', mail.outbox[0].body)

    def test_password_reset_confirm_sets_new_password(self):
        request_response = self.client.post(
            '/api/auth/password-reset/',
            {'email': 'reset@example.com'},
            format='json',
        )
        self.assertEqual(request_response.status_code, 200)

        body = mail.outbox[0].body
        marker = '/reset-password?uid='
        start = body.find(marker)
        self.assertNotEqual(start, -1)
        query = body[start + len('/reset-password?'):].splitlines()[0]
        parts = dict(chunk.split('=', 1) for chunk in query.split('&'))

        confirm_response = self.client.post(
            '/api/auth/password-reset/confirm/',
            {
                'uid': parts['uid'],
                'token': parts['token'],
                'new_password': 'NewStrongPass123!',
            },
            format='json',
        )

        self.assertEqual(confirm_response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass123!'))
