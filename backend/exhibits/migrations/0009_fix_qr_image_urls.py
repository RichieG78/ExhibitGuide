from django.db import migrations


def update_qr_image_urls(apps, schema_editor):
    Exhibit = apps.get_model('exhibits', 'Exhibit')

    qr_to_image_url = {
        1002: 'https://upload.wikimedia.org/wikipedia/commons/0/0f/1665_Girl_with_a_Pearl_Earring.jpg',
        1005: 'https://upload.wikimedia.org/wikipedia/commons/8/84/Gustav_Klimt_046.jpg',
        1006: 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Whistlers_Mother_high_res.jpg',
        1007: 'https://upload.wikimedia.org/wikipedia/commons/3/30/The_Fighting_Temeraire%2C_JMW_Turner%2C_National_Gallery.jpg',
        1008: 'https://upload.wikimedia.org/wikipedia/commons/9/94/John_Everett_Millais_-_Ophelia_-_Google_Art_Project.jpg',
        1009: 'https://upload.wikimedia.org/wikipedia/commons/0/0b/Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg',
        1010: 'https://upload.wikimedia.org/wikipedia/commons/3/39/N%C2%BA_24_%28Brown%2C_Black_and_Blue%29%2C_Mark_Rothko%2C_Paintings_in_the_San_Francisco_Museum_of_Modern_Art%2C_SFMOMA_12.jpg',
    }

    for qr_identifier, image_url in qr_to_image_url.items():
        Exhibit.objects.filter(qr_identifier=qr_identifier).update(image_url=image_url)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ('exhibits', '0008_artist_show_remove_exhibit_artist_and_more'),
    ]

    operations = [
        migrations.RunPython(update_qr_image_urls, noop_reverse),
    ]
