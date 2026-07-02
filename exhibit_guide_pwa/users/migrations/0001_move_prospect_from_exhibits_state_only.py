from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('exhibits', '0005_move_prospect_to_users_state_only'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Prospect',
                    fields=[
                        ('id', models.AutoField(primary_key=True, serialize=False)),
                        ('firstname', models.CharField(max_length=150)),
                        ('lastname', models.CharField(max_length=150)),
                        ('email', models.EmailField(max_length=254)),
                        ('phone', models.CharField(help_text='Phone number in international or local format', max_length=30)),
                        ('saved_at', models.DateTimeField(auto_now_add=True)),
                        ('dwell_time', models.PositiveIntegerField()),
                        ('exhibit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prospects', to='exhibits.exhibit')),
                    ],
                    options={
                        'db_table': 'prospects',
                    },
                ),
            ],
        ),
    ]
