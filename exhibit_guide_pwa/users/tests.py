from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from exhibits.models import Artist, Artwork, Exhibit, Show

from .models import GalleryInquiry, Prospect, SavedCollection, SavedExhibit, UserProfile


class UsersFixtureMixin:
	"""Build valid user and exhibit records for repeatable tests."""

	def make_user(self, username='collector', email='collector@example.com', password='pw123456'):
		return User.objects.create_user(username=username, email=email, password=password)

	def make_exhibit(self, *, owner=None, title='Untitled Work'):
		owner = owner or self.make_user(username='owner')
		artist = Artist.objects.create(firstname='Test', lastname='Artist', nationality='Unknown')
		artwork = Artwork.objects.create(
			title=title,
			artist=artist,
			medium='Oil on canvas',
			dimensions_height=80,
			dimensions_width=60,
			provenance='Collection provenance',
		)
		show = Show.objects.create(show_name='Main Show')
		return Exhibit.objects.create(
			show=show,
			artwork=artwork,
			price=250000,
			currency=Exhibit.CurrencyChoices.USD,
			tldr='Short summary',
			full_text='Long summary',
			audio_url='https://example.com/audio',
			video_url='https://example.com/video',
			image_url='https://example.com/image',
			publish_date=timezone.now(),
			user=owner,
		)


class ProspectModelTests(UsersFixtureMixin, TestCase):
	"""Model-level checks for compatibility helpers and string formatting on Prospect."""

	def test_name_compatibility_properties_and_str(self):
		exhibit = self.make_exhibit(title='Blue Geometry')
		prospect = Prospect.objects.create(
			name='Ada Lovelace',
			email='ada@example.com',
			phone='12345',
			exhibit=exhibit,
			dwell_time=20,
		)

		self.assertEqual(prospect.firstname, 'Ada')
		self.assertEqual(prospect.lastname, 'Lovelace')
		self.assertIn('Blue Geometry', str(prospect))

	def test_single_name_has_empty_lastname(self):
		exhibit = self.make_exhibit(title='Red Circle')
		prospect = Prospect.objects.create(
			name='Prince',
			email='prince@example.com',
			phone='12345',
			exhibit=exhibit,
			dwell_time=10,
		)

		self.assertEqual(prospect.firstname, 'Prince')
		self.assertEqual(prospect.lastname, '')


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class UsersViewStabilityTests(UsersFixtureMixin, TestCase):
	"""Integration tests for register/login/profile/dashboard user flows."""

	def setUp(self):
		self.user = self.make_user()
		self.owner = self.make_user(username='owner-1', email='owner@example.com')
		self.exhibit = self.make_exhibit(owner=self.owner, title='Echoes in Gold')

	def test_register_get_persists_interest_in_session(self):
		response = self.client.get(reverse('register'), {'interest_exhibit': self.exhibit.id})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(self.client.session.get('interest_exhibit_id'), str(self.exhibit.id))

	def test_register_post_creates_user_and_redirects_dashboard(self):
		response = self.client.post(
			reverse('register'),
			{
				'username': 'new-user',
				'email': 'new-user@example.com',
				'password1': 'StrongPass123!',
				'password2': 'StrongPass123!',
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('dashboard'))
		self.assertTrue(User.objects.filter(username='new-user').exists())

	def test_login_honors_next_parameter(self):
		response = self.client.post(
			reverse('login'),
			{
				'username': self.user.username,
				'password': 'pw123456',
				'next': reverse('profile'),
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('profile'))

	def test_profile_requires_login(self):
		response = self.client.get(reverse('profile'))
		self.assertEqual(response.status_code, 302)
		self.assertIn(reverse('login'), response.url)

	def test_profile_get_creates_profile_and_prefills_names(self):
		self.user.first_name = 'Grace'
		self.user.last_name = 'Hopper'
		self.user.save(update_fields=['first_name', 'last_name'])
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.get(reverse('profile'))

		self.assertEqual(response.status_code, 200)
		profile = UserProfile.objects.get(user=self.user)
		self.assertEqual(profile.firstname, 'Grace')
		self.assertEqual(profile.lastname, 'Hopper')

	def test_dashboard_save_exhibit_action_is_idempotent(self):
		self.client.login(username=self.user.username, password='pw123456')

		first = self.client.post(
			reverse('dashboard'),
			{'action': 'save_exhibit', 'exhibit_id': self.exhibit.id},
		)
		second = self.client.post(
			reverse('dashboard'),
			{'action': 'save_exhibit', 'exhibit_id': self.exhibit.id},
		)

		self.assertEqual(first.status_code, 302)
		self.assertEqual(second.status_code, 302)
		self.assertEqual(
			SavedExhibit.objects.filter(user=self.user, exhibit=self.exhibit).count(),
			1,
		)

	def test_dashboard_remove_saved_exhibit_action(self):
		SavedExhibit.objects.create(user=self.user, exhibit=self.exhibit)
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.post(
			reverse('dashboard'),
			{'action': 'remove_saved_exhibit', 'exhibit_id': self.exhibit.id},
		)

		self.assertEqual(response.status_code, 302)
		self.assertFalse(SavedExhibit.objects.filter(user=self.user, exhibit=self.exhibit).exists())

	def test_dashboard_initial_filter_is_scanned_for_scan_origin(self):
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.get(reverse('dashboard'), {'interest_exhibit': self.exhibit.id})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['initial_filter'], 'scanned')

	def test_dashboard_initial_filter_is_watching_without_scan_context(self):
		SavedExhibit.objects.create(user=self.user, exhibit=self.exhibit)
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.get(reverse('dashboard'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['initial_filter'], 'watching')

	def test_dashboard_initial_filter_is_enquired_when_only_enquired_saved_items_exist(self):
		SavedExhibit.objects.create(user=self.user, exhibit=self.exhibit)
		GalleryInquiry.objects.create(
			user=self.user,
			exhibit=self.exhibit,
			message='Interested in this artwork.',
		)
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.get(reverse('dashboard'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['initial_filter'], 'enquired')

	def test_dashboard_create_collection_action(self):
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.post(
			reverse('dashboard'),
			{
				'action': 'create_collection',
				'name': 'Weekend Shortlist',
				'notes': 'Works to revisit',
				'exhibits': [self.exhibit.id],
			},
		)

		self.assertEqual(response.status_code, 302)
		collection = SavedCollection.objects.get(user=self.user, name='Weekend Shortlist')
		self.assertEqual(collection.exhibits.count(), 1)

	def test_dashboard_send_inquiry_creates_inquiry_and_prospect_without_profile(self):
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.post(
			reverse('dashboard'),
			{
				'action': 'send_inquiry',
				'exhibit': self.exhibit.id,
				'contact_methods': ['email'],
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('dashboard'))
		self.assertEqual(GalleryInquiry.objects.filter(user=self.user, exhibit=self.exhibit).count(), 1)
		inquiry = GalleryInquiry.objects.get(user=self.user, exhibit=self.exhibit)
		self.assertIn('Preferred contact methods: Email', inquiry.message)

		prospect = Prospect.objects.get(email=self.user.email, exhibit=self.exhibit)
		self.assertEqual(prospect.name, self.user.username)
		self.assertEqual(prospect.phone, '')
		self.assertFalse(prospect.call_back_request)

	def test_dashboard_send_inquiry_requires_phone_for_phone_or_text_contact(self):
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.post(
			reverse('dashboard'),
			{
				'action': 'send_inquiry',
				'exhibit': self.exhibit.id,
				'contact_methods': ['phone'],
				'contact_email': self.user.email,
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('dashboard'))
		self.assertEqual(GalleryInquiry.objects.filter(user=self.user, exhibit=self.exhibit).count(), 0)
		self.assertEqual(Prospect.objects.filter(email=self.user.email, exhibit=self.exhibit).count(), 0)

	def test_dashboard_send_inquiry_save_to_profile_updates_user_profile(self):
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.post(
			reverse('dashboard'),
			{
				'action': 'send_inquiry',
				'exhibit': self.exhibit.id,
				'message': 'Please text me with details.',
				'contact_methods': ['email', 'text'],
				'contact_email': 'new-contact@example.com',
				'first_name': 'Ada',
				'last_name': 'Lovelace',
				'contact_phone': '+3538888888',
				'save_to_profile': 'on',
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('dashboard'))

		profile = UserProfile.objects.get(user=self.user)
		self.assertEqual(profile.firstname, 'Ada')
		self.assertEqual(profile.lastname, 'Lovelace')
		self.assertEqual(profile.phone, '+3538888888')

		self.user.refresh_from_db()
		self.assertEqual(self.user.email, 'new-contact@example.com')

		prospect = Prospect.objects.get(email='new-contact@example.com', exhibit=self.exhibit)
		self.assertEqual(prospect.name, 'Ada Lovelace')
		self.assertEqual(prospect.phone, '+3538888888')
		self.assertTrue(prospect.call_back_request)

	def test_dashboard_send_inquiry_updates_existing_prospect(self):
		UserProfile.objects.create(
			user=self.user,
			firstname='Ada',
			lastname='Lovelace',
			phone='+3539999999',
		)
		Prospect.objects.create(
			name='Old Name',
			email=self.user.email,
			phone='old-phone',
			exhibit=self.exhibit,
			dwell_time=3,
			call_back_request=False,
		)
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.post(
			reverse('dashboard'),
			{
				'action': 'send_inquiry',
				'exhibit': self.exhibit.id,
				'message': 'Please contact me.',
				'contact_methods': ['phone'],
			},
		)

		self.assertEqual(response.status_code, 302)
		prospect = Prospect.objects.get(email=self.user.email, exhibit=self.exhibit)
		self.assertEqual(prospect.name, 'Ada Lovelace')
		self.assertEqual(prospect.phone, '+3539999999')
		self.assertTrue(prospect.call_back_request)

	def test_dashboard_enquiry_modal_accessibility_contract_is_present(self):
		"""Render-level guard for modal hooks used by keyboard/focus handling JS."""
		SavedExhibit.objects.create(user=self.user, exhibit=self.exhibit)
		self.client.login(username=self.user.username, password='pw123456')

		response = self.client.get(reverse('dashboard'))
		self.assertEqual(response.status_code, 200)

		html = response.content.decode('utf-8')
		self.assertIn('data-inquiry-modal', html)
		self.assertIn('aria-hidden="true"', html)
		self.assertIn('data-inquiry-close', html)
		self.assertIn('data-inquiry-toggle', html)
		self.assertIn('id="inquiry-message"', html)
		self.assertIn('data-inquiry-form', html)
		self.assertIn('data-phone-block', html)
		self.assertIn('data-profile-consent', html)
