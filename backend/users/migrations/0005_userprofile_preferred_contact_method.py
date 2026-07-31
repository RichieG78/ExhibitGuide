from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_userprofile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='preferred_contact_method',
            field=models.CharField(blank=True, choices=[('email', 'Email'), ('phone', 'Phone'), ('text', 'Text')], max_length=10),
        ),
    ]
