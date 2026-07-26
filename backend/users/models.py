"""Data models for signed-in user activity and gallery follow-up.

This app stores the collector profile, saved works, collections, inquiries,
and prospect records created from user interest.
"""

from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from exhibits.models import Exhibit

class Prospect(models.Model):
    """Represents a person the gallery may want to contact about a work."""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300)
    email = models.EmailField()
    phone = models.CharField(max_length=30, help_text='Phone number in international or local format')
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE, related_name='prospects')
    saved_at = models.DateTimeField(auto_now_add=True)
    dwell_time = models.PositiveIntegerField()
    call_back_request = models.BooleanField(default=False)

    class Meta:
        db_table = 'prospects'

    @property
    def firstname(self):
        """Compatibility helper for older code that still expects first name."""
        return self.name.split(' ', 1)[0] if self.name else ''

    @property
    def lastname(self):
        """Compatibility helper for older code that still expects last name."""
        return self.name.split(' ', 1)[1] if self.name and ' ' in self.name else ''

    def __str__(self):
        return f'{self.name} ({self.email}) interested in {self.exhibit.artwork}'


class UserProfile(models.Model):
    """Stores extra profile details that Django's default User does not include."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='profile_pics', blank=True)
    firstname = models.CharField(max_length=150, blank=True)
    lastname = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        db_table = 'user_profiles'

    def save(self, *args, **kwargs):
        """Save the profile and shrink large uploaded images for faster page loads."""
        super().save(*args, **kwargs)

        if not self.image:
            return

        image_file = Image.open(self.image.path)
        if image_file.height > 600 or image_file.width > 600:
            # Resize in place so uploaded profile pictures stay lightweight.
            image_file.thumbnail((600, 600))
            image_file.save(self.image.path)

    def __str__(self):
        return f'Profile for {self.user.username}'


class SavedExhibit(models.Model):
    """A single exhibit a user has added to their watchlist."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_exhibits')
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE, related_name='saved_by_users')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_exhibits'
        unique_together = ('user', 'exhibit')

    def __str__(self):
        return f'{self.user.username} saved {self.exhibit.artwork}'


class SavedCollection(models.Model):
    """A named group of exhibits curated by the signed-in user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_collections')
    name = models.CharField(max_length=120)
    notes = models.TextField(blank=True)
    exhibits = models.ManyToManyField(Exhibit, related_name='in_user_collections', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_collections'

    def __str__(self):
        return f'{self.name} ({self.user.username})'


class GalleryInquiry(models.Model):
    """Message a user sends to the gallery about a specific exhibit."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gallery_inquiries')
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE, related_name='gallery_inquiries')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gallery_inquiries'

    def __str__(self):
        return f'Inquiry by {self.user.username} about {self.exhibit.artwork}'
