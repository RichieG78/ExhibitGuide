"""Admin configuration for exhibits and inbound prospect records."""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Artist, Artwork, Exhibit, Show
from users.models import GalleryInquiry, Prospect


class ArtworkInline(admin.TabularInline):
	"""Allow gallery staff to create artworks while editing an artist."""
	model = Artwork
	extra = 0
	fields = ('title', 'medium', 'dimensions_height', 'dimensions_width')
	show_change_link = True


class ShowExhibitInline(admin.TabularInline):
	"""Surface exhibits inside a show admin page."""
	model = Exhibit
	extra = 0
	fields = ('artwork', 'gallery_name', 'currency', 'price', 'publish_date', 'qr_identifier')
	readonly_fields = ('qr_identifier',)
	autocomplete_fields = ('artwork',)
	show_change_link = True


class ArtworkExhibitInline(admin.TabularInline):
	"""Surface exhibits inside an artwork admin page."""
	model = Exhibit
	extra = 0
	fields = ('show', 'gallery_name', 'currency', 'price', 'publish_date', 'qr_identifier')
	readonly_fields = ('qr_identifier',)
	autocomplete_fields = ('show',)
	show_change_link = True


class GalleryInquiryInline(admin.TabularInline):
	"""Show visitor enquiries directly on the exhibit edit page."""
	model = GalleryInquiry
	extra = 0
	fields = ('user', 'message', 'created_at')
	readonly_fields = ('user', 'message', 'created_at')
	show_change_link = True


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
	"""CRUD for artist records used by artworks and exhibits."""
	list_display = ('firstname', 'lastname', 'nationality', 'artwork_count')
	list_filter = ('nationality',)
	search_fields = ('firstname', 'lastname')
	ordering = ('lastname', 'firstname')
	inlines = (ArtworkInline,)

	def artwork_count(self, obj):
		"""Return the number of artworks linked to this artist."""
		return obj.artworks.count()

	artwork_count.short_description = 'Artworks'


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
	"""Manage shows and quickly access all exhibits assigned to each show."""
	list_display = ('show_name', 'start_date', 'end_date', 'exhibit_count')
	list_filter = ('start_date', 'end_date')
	search_fields = ('show_name',)
	ordering = ('-start_date', 'show_name')
	inlines = (ShowExhibitInline,)

	def exhibit_count(self, obj):
		"""Return how many exhibits are currently attached to the show."""
		return obj.exhibits.count()

	exhibit_count.short_description = 'Exhibits'


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
	"""CRUD for artworks and artist associations."""
	list_display = ('title', 'artist', 'medium', 'dimensions_height', 'dimensions_width', 'exhibit_count')
	list_filter = ('medium', 'artist__nationality')
	search_fields = ('title', 'artist__firstname', 'artist__lastname', 'medium')
	ordering = ('title',)
	autocomplete_fields = ('artist',)
	inlines = (ArtworkExhibitInline,)

	def exhibit_count(self, obj):
		"""Return how many exhibit records use this artwork."""
		return obj.exhibits.count()

	exhibit_count.short_description = 'Exhibits'


class ProspectInline(admin.TabularInline):
	"""Show related prospect records directly on the exhibit admin page."""
	model = Prospect
	extra = 0
	fields = ('name', 'email', 'phone', 'dwell_time', 'call_back_request', 'saved_at')
	readonly_fields = ('saved_at',)
	show_change_link = True


@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
	"""Admin layout for managing the public exhibit experience."""
	list_display = (
		'artwork',
		'artist',
		'show_name',
		'gallery_name',
		'currency',
		'price',
		'qr_identifier',
		'inquiry_count',
		'prospect_count',
		'public_preview_url',
		'publish_date',
	)
	list_filter = ('gallery_name', 'currency', 'publish_date', 'show')
	search_fields = (
		'artwork__title',
		'artwork__artist__firstname',
		'artwork__artist__lastname',
		'show__show_name',
		'gallery_name',
	)
	ordering = ('-publish_date',)
	autocomplete_fields = ('show', 'artwork', 'user')
	inlines = (GalleryInquiryInline, ProspectInline)
	readonly_fields = ('id', 'qr_identifier', 'public_preview_url')
	fieldsets = (
		('Core Details', {
			'fields': ('id', 'qr_identifier', 'public_preview_url', 'gallery_name', 'show', 'artwork')
		}),
		('Commerce and Delivery', {
			'fields': ('price', 'currency', 'audio_url', 'video_url', 'image', 'image_url')
		}),
		('Publishing', {
			'fields': ('publish_date', 'user', 'tldr', 'full_text')
		}),
	)

	def public_preview_url(self, obj):
		"""Build the public QR preview link once the exhibit has been saved."""
		if not obj or not obj.pk or obj.qr_identifier is None:
			return 'Available after save'
		url = reverse('exhibit_preview_by_qr', args=[obj.qr_identifier])
		return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', url, url)

	public_preview_url.short_description = 'Public exhibit URL'

	def inquiry_count(self, obj):
		"""Return number of gallery inquiries received for this exhibit."""
		return obj.gallery_inquiries.count()

	inquiry_count.short_description = 'Inquiries'

	def prospect_count(self, obj):
		"""Return number of prospect records generated from this exhibit."""
		return obj.prospects.count()

	prospect_count.short_description = 'Prospects'


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
	"""Admin table for people who have shown interest in exhibits."""
	list_display = ('name', 'email', 'phone', 'exhibit', 'show_name', 'saved_at', 'dwell_time', 'call_back_request')
	list_filter = ('saved_at', 'call_back_request', 'exhibit__show', 'exhibit')
	search_fields = ('name', 'email', 'phone', 'exhibit__artwork__title')
	ordering = ('-saved_at',)
	autocomplete_fields = ('exhibit',)

	def show_name(self, obj):
		"""Expose related show name in the prospect list table."""
		return obj.exhibit.show.show_name if obj.exhibit and obj.exhibit.show else ''

	show_name.short_description = 'Show'


@admin.register(GalleryInquiry)
class GalleryInquiryAdmin(admin.ModelAdmin):
	"""Track visitor enquiries by artwork, exhibit, and show for gallery follow-up."""
	list_display = ('user', 'artwork_title', 'show_name', 'exhibit', 'created_at', 'message_preview')
	list_filter = ('created_at', 'exhibit__show', 'exhibit')
	search_fields = (
		'user__username',
		'user__email',
		'exhibit__artwork__title',
		'exhibit__show__show_name',
		'message',
	)
	ordering = ('-created_at',)
	autocomplete_fields = ('user', 'exhibit')
	readonly_fields = ('created_at',)

	def artwork_title(self, obj):
		"""Expose related artwork title in the inquiry list table."""
		return obj.exhibit.artwork.title if obj.exhibit and obj.exhibit.artwork else ''

	artwork_title.short_description = 'Artwork'

	def show_name(self, obj):
		"""Expose related show name in the inquiry list table."""
		return obj.exhibit.show.show_name if obj.exhibit and obj.exhibit.show else ''

	show_name.short_description = 'Show'

	def message_preview(self, obj):
		"""Show a short preview so long inquiry messages don't overwhelm the list view."""
		message = (obj.message or '').strip()
		if len(message) <= 80:
			return message
		return f'{message[:80]}...'

	message_preview.short_description = 'Message'
