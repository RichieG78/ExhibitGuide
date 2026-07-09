"""Data models for the public exhibit experience.

These models separate reusable art data from exhibit-specific presentation data.
That keeps artists, artworks, shows, and public exhibit records easier to reuse.
"""

from django.contrib.auth.models import User
from django.db import models


class Artist(models.Model):
    """Stores the person who created an artwork."""

    artist_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    nationality = models.CharField(max_length=120, blank=True)

    class Meta:
        db_table = 'artists'

    def __str__(self):
        full_name = f'{self.firstname} {self.lastname}'.strip()
        return full_name or 'Unknown Artist'


class Show(models.Model):
    """Stores the exhibition or show that an exhibit belongs to."""

    show_id = models.AutoField(primary_key=True)
    show_name = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'shows'

    def __str__(self):
        return self.show_name


class Artwork(models.Model):
    """Stores reusable artwork facts that can be shared across exhibits."""

    artwork_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artworks')
    medium = models.CharField(max_length=255)
    dimensions_height = models.PositiveSmallIntegerField(help_text='Height in centimetres (cm)')
    dimensions_width = models.PositiveSmallIntegerField(help_text='Width in centimetres (cm)')
    provenance = models.TextField()

    class Meta:
        db_table = 'artworks'

    def __str__(self):
        return self.title


class Exhibit(models.Model):
    """Public-facing exhibit record shown after a visitor scans a code."""

    class CurrencyChoices(models.TextChoices):
        USD = 'USD', 'USD'
        EUR = 'EUR', 'EUR'
        GBP = 'GBP', 'GBP'

    id = models.AutoField(primary_key=True)
    gallery_name = models.CharField(max_length=100, default='Hargreaves Fine Art')
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='exhibits', null=True, blank=True)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='exhibits', null=True, blank=True)
    price = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
    tldr = models.TextField()
    full_text = models.TextField()
    audio_url = models.URLField()
    video_url = models.URLField()
    image = models.ImageField(default='exhibit_images/default.jpg', upload_to='exhibit_images/', null=True, blank=True)
    image_url = models.URLField()
    qr_identifier = models.PositiveIntegerField(
        unique=True,
        db_index=True,
        null=True,
        blank=True,
        editable=False,
        help_text='Printed QR code identifier',
    )
    publish_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exhibits')

    class Meta:
        db_table = 'exhibits'

    @property
    def artist(self):
        """Expose artist name directly on Exhibit to keep templates simple."""
        if not self.artwork or not self.artwork.artist:
            return ''
        return str(self.artwork.artist)

    @property
    def medium(self):
        return self.artwork.medium if self.artwork else ''

    @property
    def dimensions_height(self):
        return self.artwork.dimensions_height if self.artwork else None

    @property
    def dimensions_width(self):
        return self.artwork.dimensions_width if self.artwork else None

    @property
    def provenance(self):
        return self.artwork.provenance if self.artwork else ''

    @property
    def show_name(self):
        return self.show.show_name if self.show else ''

    def save(self, *args, **kwargs):
        """Save the exhibit and generate a stable QR number after the first save."""
        super().save(*args, **kwargs)

        if self.qr_identifier is None and self.id is not None:
            # The QR identifier is derived from the database id so it stays predictable.
            generated_qr_identifier = self.id + 1000
            type(self).objects.filter(pk=self.pk, qr_identifier__isnull=True).update(
                qr_identifier=generated_qr_identifier
            )
            self.qr_identifier = generated_qr_identifier

    def __str__(self):
        if self.artwork:
            return f'{self.artwork.title} by {self.artist}'
        return f'Exhibit #{self.id}'
