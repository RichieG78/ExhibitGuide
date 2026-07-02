from django.db import models
from django.contrib.auth.models import User
from exhibits.models import Exhibit

# Create your models here.

class Prospect(models.Model):
    """Gallery visitor that is interested in an exhibit."""

    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, help_text='Phone number in international or local format')
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE, related_name='prospects')
    saved_at = models.DateTimeField(auto_now_add=True)
    dwell_time = models.PositiveIntegerField()

    class Meta:
        db_table = 'prospects'

    def __str__(self):
        return f'{self.firstname} {self.lastname} ({self.email}) interested in {self.exhibit.artwork}'


class UserProfile(models.Model):
    """Extended details for a signed-in user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    firstname = models.CharField(max_length=150, blank=True)
    lastname = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f'Profile for {self.user.username}'


class SavedExhibit(models.Model):
    """A painting/exhibit saved by a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_exhibits')
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE, related_name='saved_by_users')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_exhibits'
        unique_together = ('user', 'exhibit')

    def __str__(self):
        return f'{self.user.username} saved {self.exhibit.artwork}'


class SavedCollection(models.Model):
    """A custom collection of saved exhibits for a user."""

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
    """Message from a user to a gallery owner about an exhibit."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gallery_inquiries')
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE, related_name='gallery_inquiries')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gallery_inquiries'

    def __str__(self):
        return f'Inquiry by {self.user.username} about {self.exhibit.artwork}'
