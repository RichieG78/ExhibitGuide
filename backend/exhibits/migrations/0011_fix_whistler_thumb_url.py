from django.db import migrations


def fix_whistler_thumb_url(apps, schema_editor):
    Exhibit = apps.get_model('exhibits', 'Exhibit')

    # Some local databases ended up with a Wikimedia thumbnail URL for QR 1006
    # that now returns HTTP 400. Normalize to a stable full image URL.
    Exhibit.objects.filter(
        qr_identifier=1006,
        image_url__icontains='Whistlers_Mother_high_res.jpg',
    ).update(
        image_url='https://upload.wikimedia.org/wikipedia/commons/1/1b/Whistlers_Mother_high_res.jpg'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('exhibits', '0010_alter_exhibit_audio_url_alter_exhibit_image_url_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_whistler_thumb_url, migrations.RunPython.noop),
    ]
