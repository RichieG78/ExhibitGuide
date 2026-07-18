"""Admin configuration for user profiles, watchlists, and collections."""

from django.contrib import admin

from .models import SavedCollection, SavedExhibit, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	"""Manage collector profile details used during inquiry follow-up."""
	list_display = ('user', 'firstname', 'lastname', 'phone')
	search_fields = ('user__username', 'user__email', 'firstname', 'lastname', 'phone')
	ordering = ('user__username',)
	autocomplete_fields = ('user',)


@admin.register(SavedExhibit)
class SavedExhibitAdmin(admin.ModelAdmin):
	"""Operational view of user watchlist activity."""
	list_display = ('user', 'exhibit', 'saved_at')
	list_filter = ('saved_at', 'exhibit__show', 'exhibit')
	search_fields = ('user__username', 'user__email', 'exhibit__artwork__title', 'exhibit__show__show_name')
	ordering = ('-saved_at',)
	autocomplete_fields = ('user', 'exhibit')


@admin.register(SavedCollection)
class SavedCollectionAdmin(admin.ModelAdmin):
	"""Manage saved collections and their exhibit memberships."""
	list_display = ('name', 'user', 'created_at', 'exhibit_count')
	list_filter = ('created_at',)
	search_fields = ('name', 'user__username', 'user__email', 'notes')
	ordering = ('-created_at',)
	autocomplete_fields = ('user', 'exhibits')

	def exhibit_count(self, obj):
		return obj.exhibits.count()

	exhibit_count.short_description = 'Exhibits'
