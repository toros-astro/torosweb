from django.db import models


class Activity(models.Model):
    name = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    activity = models.CharField(max_length=500)
    email = models.EmailField(max_length=70, blank=True, null=True)
    phone = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return "'{}...' by {}".format(self.activity[:10], self.name)