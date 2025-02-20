from django.db import models
from django.contrib.auth.models import AbstractUser
from stdimage.models import StdImageField
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    institutions_choice = (
        ('IATE', 'Instituto Astronomico Teorico Experimental - OAC'),
        ('UTRGV', 'University of Texas Rio Grande Valley'),
        ('TAMU', 'Texas A&M University'),
        ('SER', 'Universidad de La Serena'),
        ('OTHER', 'Other')
        )
    affiliation = models.CharField(
        max_length=5,
        choices=institutions_choice,
        default='OTHER',
    )
    picture = StdImageField(upload_to='profile_images', blank=True, null=True,
        variations={
        'thumbnail': (100, 100, True),
        'medium': (200, 200),
    })
    is_active = models.BooleanField(_('active'), default=False)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_active = True
        super().save(*args, **kwargs)
