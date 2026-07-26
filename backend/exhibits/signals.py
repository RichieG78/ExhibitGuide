"""Signals that keep exhibit data in sync after admin saves."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Exhibit


@receiver(post_save, sender=Exhibit)
def sync_exhibit_image_url(sender, instance, **kwargs):
    """Mirror an uploaded image path into image_url so templates can use one field."""
    if not instance.image:
        return

    # Keep curated/external image_url values when only the default placeholder is set.
    if instance.image.name == 'exhibit_images/default.jpg':
        return

    current_image_url = instance.image.url
    if instance.image_url == current_image_url:
        return

    # Update directly to avoid recursively triggering this post_save receiver.
    sender.objects.filter(pk=instance.pk).update(image_url=current_image_url)