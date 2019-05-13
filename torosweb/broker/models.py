from django.db import models


class CatalogManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class SourceCatalog(models.Model):
    objects = CatalogManager()

    pgc = models.IntegerField("PGC Identifier from HYPERLEDA", null=True, blank=True)
    name = models.CharField("Common Name", max_length=40, unique=True)
    ra = models.FloatField("Right Ascension [deg]", null=True, blank=True)
    dec = models.FloatField("Declination [deg]", null=True, blank=True)
    obj_type = models.CharField("Type", max_length=5, null=True, blank=True)
    b_mag = models.FloatField("Apparent B Magnitude", null=True, blank=True)
    b_err = models.FloatField("Error on Apparent B Magnitude", null=True, blank=True)
    b_abs = models.FloatField("Absolute B Magnitude", null=True, blank=True)
    j_mag = models.FloatField("Apparent J Magnitude", null=True, blank=True)
    j_err = models.FloatField("Error on Apparent J Magnitude", null=True, blank=True)
    h_mag = models.FloatField("Apparent H Magnitude", null=True, blank=True)
    h_err = models.FloatField("Error on Apparent H Magnitude", null=True, blank=True)
    k_mag = models.FloatField("Apparent K Magnitude", null=True, blank=True)
    k_err = models.FloatField("Error on Apparent K Magnitude", null=True, blank=True)
    dist = models.FloatField("Distance", null=True, blank=True)
    dist_err = models.FloatField("Error on Distance", null=True, blank=True)

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name


class ObservatoryManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Observatory(models.Model):
    objects = ObservatoryManager()

    name = models.CharField(max_length=50, unique=True)
    short_name = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation = models.FloatField()

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name

    class Meta():
        verbose_name_plural = "observatories"


class SuperEventManager(models.Manager):
    def get_by_natural_key(self, grace_id):
        return self.get(grace_id=grace_id)

class SuperEvent(models.Model):
    objects = SuperEventManager()

    ligo_run = models.CharField("LIGO run", max_length=20,
                                null=True, blank=True)
    grace_id = models.CharField("GraceDB ID", max_length=20, unique=True)
    SETYPE_OPTIONS = (('T', 'Test'),
                      ('M', 'Mock'),
                      ('S', 'Observation'),
                      ('D', 'Drill'))
    se_type = models.CharField(max_length=1, choices=SETYPE_OPTIONS, default='S', verbose_name="Super Event type")
    was_retracted = models.BooleanField(default=False)
    was_confirmed_GW = models.BooleanField(default=False)
    datetime = models.DateTimeField()
    description = models.TextField(null=True, blank=True)

    def natural_key(self):
        return (self.grace_id,)

    def __str__(self):
        return self.grace_id


class GCNNotice(models.Model):
    "Gamma-ray Coordinates Network Notice"
    GCNORIGIN_OPTIONS = (('GW', 'Gravitational Wave'),
                         ('GRB', 'Gamma Ray Burst'),
                         ('OTH', 'Other'))
    gcnorigin = models.CharField(
        default='GW', max_length=3, choices=GCNORIGIN_OPTIONS, verbose_name="GCN Origin")
    GCNTYPE_OPTIONS = ((0, 'Preliminary'),
                       (1, 'Initial'),
                       (2, 'Update'),
                       (3, 'Retraction'))
    gcntype = models.IntegerField(default=0, choices=GCNTYPE_OPTIONS, verbose_name="GCN Type")
    superevent = models.ForeignKey(SuperEvent, verbose_name="Super Event")
    datetime = models.DateTimeField()

    class Meta():
        verbose_name = "GCN Notice"
        verbose_name_plural = "GCN Notices"

    def __str__(self):
        return "{} GCN for {}".format(self.get_gcntype_display(), self.superevent.grace_id)


class Assignment(models.Model):
    target = models.ForeignKey(SourceCatalog)
    observatory = models.ForeignKey(Observatory)
    gcnnotice = models.ForeignKey(GCNNotice)
    datetime = models.DateTimeField()
    is_taken = models.BooleanField(default=False)
    was_observed = models.BooleanField(default=False)
    probability = models.FloatField(null=True, blank=True, default=0.)

    def __str__(self):
        obs_name = self.observatory.short_name
        if obs_name is None:
            obs_name = self.observatory
        return "{} for obs {} for {}".format(
            self.target, obs_name, self.gcnnotice)
