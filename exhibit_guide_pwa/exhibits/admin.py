from django.contrib import admin

from .models import Exhibit
from users.models import Prospect


class ProspectInline(admin.TabularInline):
	model = Prospect
	extra = 0
	fields = ('firstname', 'lastname', 'email', 'phone', 'dwell_time')
	show_change_link = True


@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
	list_display = ('artwork', 'artist', 'show_name', 'currency', 'price', 'qr_identifier', 'publish_date')
	list_filter = ('gallery_name', 'currency', 'publish_date')
	search_fields = ('artwork', 'artist', 'show_name', 'gallery_name')
	ordering = ('-publish_date',)
	inlines = (ProspectInline,)
	readonly_fields = ('id',)
	fieldsets = (
		('Core Details', {
			'fields': ('id', 'gallery_name', 'show_name', 'artwork', 'artist', 'medium')
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


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
	list_display = ('firstname', 'lastname', 'email', 'exhibit', 'saved_at', 'dwell_time')
	list_filter = ('saved_at', 'exhibit')
	search_fields = ('firstname', 'lastname', 'email', 'phone', 'exhibit__artwork')
	ordering = ('-saved_at',)
