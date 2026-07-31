from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from exhibits.models import Artist, Artwork, Exhibit, Show
from users.models import GalleryInquiry


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
                'preferred_contact_method': 'phone',
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
        self.assertEqual(self.user.profile.preferred_contact_method, 'phone')

    def test_profile_patch_requires_phone_for_phone_or_text_preference(self):
        response = self.client.patch(
            '/api/auth/profile/',
            {
                'preferred_contact_method': 'text',
                'phone': '',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.data)


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


class UserApiInquiryTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(
            username='gallery-owner',
            email='owner@example.com',
            password='StrongPass123!',
        )
        self.user = User.objects.create_user(
            username='inquirer',
            email='inquirer@example.com',
            password='StrongPass123!',
        )

        artist = Artist.objects.create(firstname='Vincent', lastname='van Gogh', nationality='Dutch')
        artwork = Artwork.objects.create(
            title='The Starry Night',
            artist=artist,
            medium='Oil on canvas',
            dimensions_height=74,
            dimensions_width=92,
            provenance='Museum collection provenance',
        )
        show = Show.objects.create(show_name='Masters of Light')
        self.exhibit = Exhibit.objects.create(
            user=owner,
            show=show,
            artwork=artwork,
            price=1000,
            currency='USD',
            tldr='Short summary',
            full_text='Longer description',
            audio_url='https://example.com/audio.mp3',
            video_url='https://example.com/video.mp4',
            image_url='https://example.com/image.jpg',
            publish_date=timezone.now(),
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_inquiry_create_returns_notified_status(self):
        response = self.client.post(
            '/api/inquiries/',
            {'exhibit': self.exhibit.id},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['already_expressed'], False)
        self.assertIn('notified', response.data['detail'].lower())
        self.assertEqual(GalleryInquiry.objects.filter(user=self.user, exhibit=self.exhibit).count(), 1)

    def test_inquiry_repeat_returns_already_expressed(self):
        GalleryInquiry.objects.create(
            user=self.user,
            exhibit=self.exhibit,
            message='Initial inquiry',
        )

        response = self.client.post(
            '/api/inquiries/',
            {'exhibit': self.exhibit.id},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['already_expressed'], True)
        self.assertIn('already', response.data['detail'].lower())
        self.assertEqual(GalleryInquiry.objects.filter(user=self.user, exhibit=self.exhibit).count(), 1)
