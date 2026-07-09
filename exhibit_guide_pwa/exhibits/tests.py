from django.contrib.auth.models import User
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Artist, Artwork, Exhibit, Show
from users.models import Prospect


class ExhibitFixtureMixin:
	"""Create normalized exhibit records in one place for the tests below."""

	def make_exhibit(
		self,
		*,
		username='tester',
		show_name='Default Collection',
		artwork_title='Untitled Work',
		artist_firstname='Test',
		artist_lastname='Artist',
		medium='Oil on canvas',
		dimensions_height=74,
		dimensions_width=92,
		provenance='Demo provenance',
		price=1000000,
		currency=Exhibit.CurrencyChoices.USD,
		tldr='Short summary',
		full_text='Long summary',
		audio_url='https://example.com/audio',
		video_url='https://example.com/video',
		image_url='https://example.com/image',
		qr_identifier=None,
	):
		user = User.objects.create_user(username=username, password='pw123456')
		artist = Artist.objects.create(
			firstname=artist_firstname,
			lastname=artist_lastname,
			nationality='Unknown',
		)
		artwork = Artwork.objects.create(
			title=artwork_title,
			artist=artist,
			medium=medium,
			dimensions_height=dimensions_height,
			dimensions_width=dimensions_width,
			provenance=provenance,
		)
		show = Show.objects.create(show_name=show_name)
		return Exhibit.objects.create(
			show=show,
			artwork=artwork,
			price=price,
			currency=currency,
			tldr=tldr,
			full_text=full_text,
			audio_url=audio_url,
			video_url=video_url,
			image_url=image_url,
			qr_identifier=qr_identifier,
			publish_date=timezone.now(),
			user=user,
		)


class ExhibitModelTests(ExhibitFixtureMixin, TestCase):

	def test_exhibit_defaults_and_string_representation(self):
		# This test checks that a new Exhibit gets expected default values
		# and that its text label is readable in admin lists and logs.
		exhibit = self.make_exhibit(
			show_name='Summer Collection',
			artwork_title='The Starry Night',
			artist_firstname='Vincent',
			artist_lastname='van Gogh',
			qr_identifier=1001,
		)

		self.assertEqual(exhibit.gallery_name, 'Hargreaves Fine Art')
		self.assertEqual(exhibit.currency, Exhibit.CurrencyChoices.USD)
		self.assertEqual(exhibit.show_name, 'Summer Collection')
		self.assertEqual(exhibit.medium, 'Oil on canvas')
		self.assertEqual(str(exhibit), 'The Starry Night by Vincent van Gogh')

	def test_qr_identifier_is_auto_generated_on_create(self):
		exhibit = self.make_exhibit(
			username='autogen-user',
			show_name='Autogen Collection',
			artwork_title='Blue Segment',
			artist_firstname='Test',
			artist_lastname='Artist',
			medium='Oil on board',
			dimensions_height=60,
			dimensions_width=40,
			price=125000,
		)

		self.assertIsNotNone(exhibit.qr_identifier)
		self.assertEqual(exhibit.qr_identifier, exhibit.id + 1000)



class ProspectModelTests(ExhibitFixtureMixin, TestCase):
	def setUp(self):
		self.exhibit = self.make_exhibit(
			show_name='Winter Collection',
			artwork_title='The Great Wave off Kanagawa',
			artist_firstname='Katsushika',
			artist_lastname='Hokusai',
			medium='Ink on paper',
			dimensions_height=25,
			dimensions_width=37,
			price=250000,
			currency=Exhibit.CurrencyChoices.GBP,
			qr_identifier=1002,
		)

	def test_prospect_string_representation(self):
		# This test confirms the Prospect display text includes key details
		# so staff can quickly understand who is interested in which artwork.
		prospect = Prospect.objects.create(
			name='Ada Lovelace',
			email='ada@example.com',
			phone='+441234567890',
			exhibit=self.exhibit,
			dwell_time=120,
		)

		self.assertEqual(
			str(prospect),
			'Ada Lovelace (ada@example.com) interested in The Great Wave off Kanagawa',
		)


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class ExhibitViewsTests(ExhibitFixtureMixin, TestCase):
	def test_scan_view_uses_scan_template(self):
		# This test checks the main scan page loads successfully and uses
		# the expected template.
		response = self.client.get(reverse('scan'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'exhibits/scan.html')

	def test_exhibit_preview_view_uses_base_template(self):
		# This test checks a concrete exhibit preview route works and renders
		# the exhibit preview template.
		exhibit = self.make_exhibit(
			username='preview-user',
			show_name='Spring Collection',
			artwork_title='No. 5',
			artist_firstname='Wassily',
			artist_lastname='Kandinsky',
			dimensions_height=100,
			dimensions_width=80,
			price=500000,
			qr_identifier=1003,
		)
		response = self.client.get(reverse('exhibit_preview', args=[exhibit.id]))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'exhibits/base.html')

	def test_qr_exhibit_preview_route_uses_base_template(self):
		exhibit = self.make_exhibit(
			username='qr-preview-user',
			show_name='QR Collection',
			artwork_title='Composition VIII',
			artist_firstname='Wassily',
			artist_lastname='Kandinsky',
			dimensions_height=140,
			dimensions_width=201,
			price=700000,
			qr_identifier=1908,
		)
		response = self.client.get(reverse('exhibit_preview_by_qr', args=[exhibit.qr_identifier]))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'exhibits/base.html')

	def test_unknown_exhibit_route_returns_404(self):
		# This test checks that unknown exhibit URLs do not silently work;
		# they should return a clear 404 page.
		response = self.client.get('/exhibits/not-a-route/')
		self.assertEqual(response.status_code, 404)

