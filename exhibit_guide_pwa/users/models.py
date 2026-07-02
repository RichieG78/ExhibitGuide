from django.db import models
from exhibits.models import Exhibit

# Create your models here.

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
