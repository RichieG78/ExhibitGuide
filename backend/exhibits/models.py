"""Data models for the public exhibit experience.

These models separate reusable art data from exhibit-specific presentation data.
That keeps artists, artworks, shows, and public exhibit records easier to reuse.
"""

from django.contrib.auth.models import User
from django.db import models
from PIL import Image, ImageOps


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
    # Django's URLField defaults to 200 characters, which is too short for real
    # image sources: a Wikimedia thumbnail repeats the filename in the path and
    # commonly exceeds 200. Widened so full source URLs can be stored directly,
    # without depending on a third-party link shortener.
    audio_url = models.URLField(max_length=500)
    video_url = models.URLField(max_length=500)
    image = models.ImageField(default='exhibit_images/default.jpg', upload_to='exhibit_images/', null=True, blank=True)
    image_url = models.URLField(max_length=500)
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

    # Uploaded exhibit images are shown as a full-width hero on mobile. A max
    # edge around 1440px stays visually crisp on high-density phone screens
    # while keeping transfer size much lower than camera originals.
    MAX_IMAGE_SIZE = (1440, 1440)

    def save(self, *args, **kwargs):
        """Save the exhibit, downscale large uploads, and generate a stable QR number."""
        super().save(*args, **kwargs)

        self._downscale_image()

        if self.qr_identifier is None and self.id is not None:
            # The QR identifier is derived from the database id so it stays predictable.
            generated_qr_identifier = self.id + 1000
            type(self).objects.filter(pk=self.pk, qr_identifier__isnull=True).update(
                qr_identifier=generated_qr_identifier
            )
            self.qr_identifier = generated_qr_identifier

    def _downscale_image(self):
        """Downscale/compress uploaded exhibit images for fast mobile loading."""
        if not self.image:
            return

        try:
            image_file = Image.open(self.image.path)
        except (FileNotFoundError, OSError):
            # Remote/missing storage or an unreadable file: leave it untouched.
            return

        image_file = ImageOps.exif_transpose(image_file)
        original_format = (image_file.format or '').upper()
        original_size_bytes = self.image.size if hasattr(self.image, 'size') else 0

        max_width, max_height = self.MAX_IMAGE_SIZE
        resized = False
        if image_file.width > max_width or image_file.height > max_height:
            image_file.thumbnail(self.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            resized = True

        # Re-encode large uploads even when dimensions already fit; many direct
        # camera exports are still unnecessarily heavy for mobile delivery.
        should_reencode = resized or original_size_bytes > 1_200_000

        if not should_reencode:
            return

        save_kwargs = {'optimize': True}

        if original_format in {'JPEG', 'JPG'}:
            if image_file.mode not in {'RGB', 'L'}:
                image_file = image_file.convert('RGB')
            save_kwargs.update({'quality': 82, 'progressive': True})
        elif original_format == 'WEBP':
            save_kwargs.update({'quality': 82, 'method': 6})
        elif original_format == 'PNG':
            save_kwargs.update({'compress_level': 6})

        image_file.save(self.image.path, **save_kwargs)

    def __str__(self):
        if self.artwork:
            return f'{self.artwork.title} by {self.artist}'
        return f'Exhibit #{self.id}'
