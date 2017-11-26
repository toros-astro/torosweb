from django.db import models
from django.contrib.auth.models import AbstractUser


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
