from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Exhibit
from users.models import Prospect


class ProspectInline(admin.TabularInline):
	model = Prospect
	extra = 0
	fields = ('firstname', 'lastname', 'email', 'phone', 'dwell_time')
	show_change_link = True


@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
	list_display = ('artwork', 'artist', 'show_name', 'currency', 'price', 'qr_identifier', 'public_preview_url', 'publish_date')
	list_filter = ('gallery_name', 'currency', 'publish_date')
	search_fields = ('artwork', 'artist', 'show_name', 'gallery_name')
	ordering = ('-publish_date',)
	inlines = (ProspectInline,)
	readonly_fields = ('id', 'public_preview_url')
	fieldsets = (
		('Core Details', {
			'fields': ('id', 'public_preview_url', 'gallery_name', 'show_name', 'artwork', 'artist', 'medium')
		}),
		('Artwork Specifications', {
			'fields': ('dimensions_height', 'dimensions_width', 'provenance')
		}),
		('Commerce and Delivery', {
			'fields': ('price', 'currency', 'audio_url', 'video_url', 'image', 'image_url')
		}),
		('Publishing', {
			'fields': ('qr_identifier', 'publish_date', 'user', 'tldr', 'full_text')
		}),
	)

	def public_preview_url(self, obj):
		url = reverse('exhibit_preview_by_qr', args=[obj.qr_identifier])
		return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', url, url)

	public_preview_url.short_description = 'Public exhibit URL'


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
	list_display = ('firstname', 'lastname', 'email', 'exhibit', 'saved_at', 'dwell_time')
	list_filter = ('saved_at', 'exhibit')
	search_fields = ('firstname', 'lastname', 'email', 'phone', 'exhibit__artwork')
	ordering = ('-saved_at',)
