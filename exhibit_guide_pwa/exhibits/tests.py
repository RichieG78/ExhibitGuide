from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Exhibit
from users.models import Prospect


class ExhibitModelTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='tester', password='pw123456')

	def test_exhibit_defaults_and_string_representation(self):
		# This test checks that a new Exhibit gets expected default values
		# and that its text label is readable in admin lists and logs.
		exhibit = Exhibit.objects.create(
			show_name='Summer Collection',
			artwork='The Starry Night',
			artist='Vincent van Gogh',
			medium='Oil on canvas',
			dimensions_height=74,
			dimensions_width=92,
			provenance='Demo provenance',
			price=1000000,
			tldr='Short summary',
			full_text='Long summary',
			audio_url='https://example.com/audio',
			video_url='https://example.com/video',
			image_url='https://example.com/image',
			qr_identifier=1001,
			publish_date=timezone.now(),
			user=self.user,
		)

		self.assertEqual(exhibit.gallery_name, 'Hargreaves Fine Art')
		self.assertEqual(exhibit.currency, Exhibit.CurrencyChoices.USD)
		self.assertEqual(str(exhibit), 'The Starry Night by Vincent van Gogh')

	def test_qr_identifier_is_auto_generated_on_create(self):
		exhibit = Exhibit.objects.create(
			show_name='Autogen Collection',
			artwork='Blue Segment',
			artist='Test Artist',
			medium='Oil on board',
			dimensions_height=60,
			dimensions_width=40,
			provenance='Demo provenance',
			price=125000,
			tldr='Short summary',
			full_text='Long summary',
			audio_url='https://example.com/audio',
			video_url='https://example.com/video',
			image_url='https://example.com/image',
			publish_date=timezone.now(),
			user=self.user,
		)

		self.assertIsNotNone(exhibit.qr_identifier)
		self.assertEqual(exhibit.qr_identifier, exhibit.id + 1000)


class ProspectModelTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='tester', password='pw123456')
		self.exhibit = Exhibit.objects.create(
			show_name='Winter Collection',
			artwork='The Great Wave off Kanagawa',
			artist='Katsushika Hokusai',
			medium='Ink on paper',
			dimensions_height=25,
			dimensions_width=37,
			provenance='Demo provenance',
			price=250000,
			currency=Exhibit.CurrencyChoices.GBP,
			tldr='Short summary',
			full_text='Long summary',
			audio_url='https://example.com/audio',
			video_url='https://example.com/video',
			image_url='https://example.com/image',
			qr_identifier=1002,
			publish_date=timezone.now(),
			user=self.user,
		)

	def test_prospect_string_representation(self):
		# This test confirms the Prospect display text includes key details
		# so staff can quickly understand who is interested in which artwork.
		prospect = Prospect.objects.create(
			firstname='Ada',
			lastname='Lovelace',
			email='ada@example.com',
			phone='+441234567890',
			exhibit=self.exhibit,
			dwell_time=120,
		)

		self.assertEqual(
			str(prospect),
			'Ada Lovelace (ada@example.com) interested in The Great Wave off Kanagawa',
		)


class ExhibitViewsTests(TestCase):
	def test_scan_view_uses_scan_template(self):
		# This test checks the main scan page loads successfully and uses
		# the expected template.
		response = self.client.get(reverse('scan'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'exhibits/scan.html')

	def test_exhibit_preview_view_uses_base_template(self):
		# This test checks a concrete exhibit preview route works and renders
		# the exhibit preview template.
		user = User.objects.create_user(username='preview-user', password='pw123456')
		exhibit = Exhibit.objects.create(
			show_name='Spring Collection',
			artwork='No. 5',
			artist='Wassily Kandinsky',
			medium='Oil on canvas',
			dimensions_height=100,
			dimensions_width=80,
			provenance='Demo provenance',
			price=500000,
			tldr='Short summary',
			full_text='Long summary',
			audio_url='https://example.com/audio',
			video_url='https://example.com/video',
			image_url='https://example.com/image',
			qr_identifier=1003,
			publish_date=timezone.now(),
			user=user,
		)
		response = self.client.get(reverse('exhibit_preview', args=[exhibit.id]))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'exhibits/base.html')

	def test_qr_exhibit_preview_route_uses_base_template(self):
		user = User.objects.create_user(username='qr-preview-user', password='pw123456')
		exhibit = Exhibit.objects.create(
			show_name='QR Collection',
			artwork='Composition VIII',
			artist='Wassily Kandinsky',
			medium='Oil on canvas',
			dimensions_height=140,
			dimensions_width=201,
			provenance='Demo provenance',
			price=700000,
			tldr='Short summary',
			full_text='Long summary',
			audio_url='https://example.com/audio',
			video_url='https://example.com/video',
			image_url='https://example.com/image',
			qr_identifier=1908,
			publish_date=timezone.now(),
			user=user,
		)
		response = self.client.get(reverse('exhibit_preview_by_qr', args=[exhibit.qr_identifier]))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'exhibits/base.html')

	def test_unknown_exhibit_route_returns_404(self):
		# This test checks that unknown exhibit URLs do not silently work;
		# they should return a clear 404 page.
		response = self.client.get('/exhibits/not-a-route/')
		self.assertEqual(response.status_code, 404)

