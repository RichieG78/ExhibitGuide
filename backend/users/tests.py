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
