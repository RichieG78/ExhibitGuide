from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Exhibit


@receiver(post_save, sender=Exhibit)
def sync_exhibit_image_url(sender, instance, **kwargs):
    """Keep image_url aligned with uploaded Exhibit image in admin saves."""
    if not instance.image:
        return

    current_image_url = instance.image.url
    if instance.image_url == current_image_url:
        return

    # Update directly to avoid recursively triggering this post_save receiver.
    sender.objects.filter(pk=instance.pk).update(image_url=current_image_url)