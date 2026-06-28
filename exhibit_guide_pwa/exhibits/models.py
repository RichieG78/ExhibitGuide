from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Exhibit(models.Model):
    """Catalogue record for a museum or gallery exhibit."""

    class CurrencyChoices(models.TextChoices):
        USD = 'USD', 'USD'
        EUR = 'EUR', 'EUR'
        GBP = 'GBP', 'GBP'

    id = models.AutoField(primary_key=True)
    gallery_name = models.CharField(max_length=100, default='Hargreaves Fine Art')
    show_name = models.CharField(max_length=200, db_column='show')
    artwork = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    medium = models.CharField(max_length=255)
    dimensions_height = models.PositiveSmallIntegerField(help_text='Height in centimetres (cm)')
    dimensions_width = models.PositiveSmallIntegerField(help_text='Width in centimetres (cm)')
    provenance = models.TextField()
    price = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
    tldr = models.TextField()
    full_text = models.TextField()
    audio_url = models.URLField()
    video_url = models.URLField()
    image = models.ImageField(upload_to='exhibit_images/', null=True, blank=True)
    image_url = models.URLField()
    qr_identifier = models.PositiveIntegerField(db_index=True, help_text='Printed QR code identifier')
    publish_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exhibits')

    class Meta:
        db_table = 'exhibits'

    def __str__(self):
        return f'{self.artwork} by {self.artist}'


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