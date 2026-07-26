from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exhibits', '0004_alter_exhibit_artist_alter_exhibit_artwork_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(
                    name='Prospect',
                ),
            ],
        ),
    ]
