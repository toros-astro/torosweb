from django.db import models


class Activity(models.Model):
    name = models.CharField(max_length=100)
    organization = models.CharField(max_length=100, blank=True, null=True)
    activity = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    email = models.EmailField(max_length=70, blank=True, null=True)
    phone = models.CharField(max_length=20)
    requires_power = models.BooleanField(default=False)
    requires_table = models.BooleanField(default=False)
    requires_chair = models.BooleanField(default=False)
    requires_volunteer = models.BooleanField(default=False)
    comment = models.CharField(max_length=500, blank=True, null=True)
    STATUS_CHOICES = [('ok', 'Approved'),
                      ('no', 'Rejected'),
                      ('pe', 'Pending'),
                      ]
    status = models.CharField(max_length=2, default='pe', choices=STATUS_CHOICES)

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return "'{}...' by {}".format(self.activity[:10], self.name)
