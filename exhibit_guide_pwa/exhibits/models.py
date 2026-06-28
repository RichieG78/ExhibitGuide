from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Exhibit(models.Model):
    """Catalogue record for a museum or gallery exhibit."""

    id = models.AutoField(primary_key=True)
    gallery_name = models.TextField(default='Hargreaves Fine Art')
    show_name = models.TextField(db_column='show')
    artwork = models.TextField()
    artist = models.TextField()
    medium = models.TextField()
    dimensions_height = models.IntegerField()
    dimensions_width = models.IntegerField()
    provenance = models.TextField()
    price = models.IntegerField()
    currency = models.TextField()
    tldr = models.TextField()
    full_text = models.TextField()
    audio_url = models.URLField()
    video_url = models.URLField()
    image_url = models.URLField()
    qr_identifier = models.IntegerField()
    publish_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exhibits')

    class Meta:
        db_table = 'exhibits'

    def __str__(self):
        return f'{self.artwork} by {self.artist}'


class Prospect(models.Model):
    """Gallery visitor that is interested in an exhibit."""

    id = models.AutoField(primary_key=True)
    firstname = models.TextField()
    lastname = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE, related_name='prospects')
    saved_at = models.DateTimeField(auto_now_add=True)
    dwell_time = models.IntegerField()

    class Meta:
        db_table = 'prospects'

    def __str__(self):
        return f'{self.firstname} {self.lastname} ({self.email}) interested in {self.exhibit.artwork}'