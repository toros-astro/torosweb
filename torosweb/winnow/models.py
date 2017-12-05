from django.db import models
from django.core.exceptions import ValidationError
from stdimage.models import StdImageField


class Dataset(models.Model):
    name = models.CharField(max_length=100, unique=True)
    isCurrent = models.BooleanField(default=True)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    cadence_sec = models.FloatField(null=True, blank=True)
    subset_of = models.ForeignKey('self', null=True, blank=True)
    number_of_files = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def number_of_reals(self):
        from django.db.models import Sum
        tc_query = TransientCandidate.objects.filter(dataset=self)
        num_reals = tc_query.annotate(brclass=Sum('ranking__rank')).\
            filter(brclass__gt=0).count()
        return num_reals

    def number_of_bogus(self):
        from django.db.models import Sum
        tc_query = TransientCandidate.objects.filter(dataset=self)
        num_bogus = tc_query.annotate(brclass=Sum('ranking__rank')).\
            filter(brclass__lt=0).count()
        return num_bogus

    def number_of_unclassified(self):
        from django.db.models import Sum
        tc_query = TransientCandidate.objects.filter(dataset=self)
        num_unclassified = tc_query.annotate(brclass=Sum('ranking__rank')).\
            filter(brclass__exact=0).count()
        return num_unclassified

    def number_not_ranked(self):
        not_ranked = TransientCandidate.objects.filter(dataset=self).\
            exclude(ranking=Ranking.objects.all()).count()
        return not_ranked

    def number_of_objects(self):
        return TransientCandidate.objects.filter(dataset=self).count()

    def number_of_rbx(self):
        from django.db.models import Sum
        tc_query = TransientCandidate.objects.filter(dataset=self)
        num_reals = tc_query.annotate(brclass=Sum('ranking__rank')).\
            filter(brclass__gt=0).count()
        num_bogus = tc_query.annotate(brclass=Sum('ranking__rank')).\
            filter(brclass__lt=0).count()
        total = tc_query.count()
        num_no_label = total - (num_reals + num_bogus)
        return num_reals, num_bogus, num_no_label

    def clean(self):
        if self.subset_of == self:
            raise ValidationError("A dataset can't be subset of itself.")

    def __str__(self):
        return self.name


class TransientCandidate(models.Model):
    ra = models.FloatField()
    dec = models.FloatField()
    x_pix = models.IntegerField()
    y_pix = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    filename = models.CharField(max_length=100)
    dataset = models.ForeignKey(Dataset)
    object_id = models.IntegerField()
    slug = models.SlugField(max_length=110)
    refImg = StdImageField(upload_to="winnow_cutouts",
                           variations={'thumbnail': (50, 50, True),
                                       'normal': (400, 400), })
    origImg = StdImageField(upload_to="winnow_cutouts",
                            variations={'thumbnail': (50, 50, True),
                                        'normal': (400, 400), })
    subtImg = StdImageField(upload_to="winnow_cutouts",
                            variations={'thumbnail': (50, 50, True),
                                        'normal': (400, 400), })
    mag_orig = models.FloatField(default=0., null=True)
    mag_ref = models.FloatField(default=0., null=True)
    mag_subt = models.FloatField(default=0., null=True)
    isDeleted = models.IntegerField(default=0)

    def aladin_coords(self):
        ra = self.ra
        dec = self.dec
        ra_deg = int(ra)
        ra_min = int((ra - ra_deg) * 60.)
        dec_deg = int(dec)
        dec_min = abs(int((dec - dec_deg) * 60.))
        sgn = "+" if dec > 0 else ""
        return "%d %02d %s%02d %02d" % (ra_deg, ra_min, sgn, dec_deg, dec_min)

    def number_of_real_votes(self):
        num_real = Ranking.objects.filter(trans_candidate=self).\
            filter(rank=1).count()
        return num_real

    def number_of_bogus_votes(self):
        num_bogus = Ranking.objects.filter(trans_candidate=self).\
            filter(rank=-1).count()
        return num_bogus

    def number_of_unclassified_votes(self):
        num_unclassifed = Ranking.objects.filter(trans_candidate=self).\
            filter(rank=0).count()
        return num_unclassifed

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        self.slug = slugify(self.dataset.name + "_%05d" % (self.object_id))
        super(TransientCandidate, self).save(*args, **kwargs)

    def __str__(self):
        return "Object %s at (%g, %g) from file: %s" % \
            (self.slug, self.ra, self.dec, self.filename)


class SEPInfo(models.Model):
    trans_candidate = models.OneToOneField(TransientCandidate)
    thresh = models.FloatField()
    npix   = models.IntegerField()
    tnpix  = models.IntegerField()
    xmin   = models.IntegerField()
    xmax   = models.IntegerField()
    ymin   = models.IntegerField()
    ymax   = models.IntegerField()
    x      = models.FloatField()
    y      = models.FloatField()
    x2     = models.FloatField()
    y2     = models.FloatField()
    xy     = models.FloatField()
    a      = models.FloatField()
    b      = models.FloatField()
    theta  = models.FloatField()
    cxx    = models.FloatField()
    cyy    = models.FloatField()
    cxy    = models.FloatField()
    cflux  = models.FloatField()
    flux   = models.FloatField()
    cpeak  = models.FloatField()
    peak   = models.FloatField()
    xcpeak = models.IntegerField()
    ycpeak = models.IntegerField()
    xpeak  = models.IntegerField()
    ypeak  = models.IntegerField()
    flag   = models.IntegerField()
    isDeleted = models.IntegerField(default=0)

    def fwhm_x(self):
        import math
        return 2 * math.sqrt(2. * math.log(2.) * self.x2)

    def fwhm_y(self):
        import math
        return 2 * math.sqrt(2. * math.log(2.) * self.y2)

    def flag_labels(self):
        flags = []
        if (self.flag & 1) != 0:
            flags.append('Object is result of deblending')
        if (self.flag & 2) != 0:
            flags.append('Object is truncated at image boundary')
        if (self.flag & 8) != 0:
            flags.append('x, y fully correlated in object')
        if (self.flag & 16) != 0:
            flags.append('Aperture truncated at image boundary')
        if (self.flag & 32) != 0:
            flags.append('Aperture contains one or more masked pixels')
        if (self.flag & 64) != 0:
            flags.append('Aperture contains only masked pixels')
        if (self.flag & 128) != 0:
            flags.append('Aperture sum is negative in kron_radius')
        return flags


class Ranking(models.Model):
    from django.conf import settings

    ranker = models.ForeignKey(settings.AUTH_USER_MODEL)
    trans_candidate = models.ForeignKey(TransientCandidate)
    RANKING_OPTIONS = ((-1, 'Bogus'),
                       (1, 'Real'),
                       (0, 'Unclassified'))
    rank = models.IntegerField(default=0, choices=RANKING_OPTIONS)
    isInteresting = models.BooleanField(default=False)

    def __str__(self):
        return "Ranking %d" % (self.id)


class Experiment(models.Model):
    from django.conf import settings

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset)
    date = models.DateField('date of experiment')
    SOFTWARE = (
        ('0', 'Weka'),
        ('1', 'RapidMiner'),
        ('2', 'scikit-learn'),
        ('3', 'Other'),
    )
    platform = models.CharField(
        'software used', max_length=1, choices=SOFTWARE, default='0')
    other_platform_name = models.CharField(max_length=20,
                                           null=True, blank=True)
    alg_name = models.CharField('algorithm name', max_length=50)
    params_file = models.FileField('parameter file name',
                                   max_length=50, null=True, blank=True)
    labels_file = models.FileField('label file name', null=True, blank=True)

    features = models.ManyToManyField('Feature')
    featureset_infofile = models.FileField('feature set file name',
                                           null=True, blank=True)
    featuretable_datafile = models.FileField('feature table file name',
                                             null=True, blank=True)

    conf_mat_rr = models.IntegerField('reals classified as reals')
    conf_mat_rb = models.IntegerField('reals classified as bogus')
    conf_mat_br = models.IntegerField('bogus classified as reals')
    conf_mat_bb = models.IntegerField('bogus classified as bogus')
    confusion_table_file = models.FileField(
        'confusion matrix file name', null=True, blank=True)

    other_outputfiles = models.TextField(
        'other output files', null=True, blank=True)
    other_inputfiles = models.TextField(
        'other input files', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_favorite = models.BooleanField(default=False)

    def recall(self):
        "Return the Recall: Proportion of Real Positive cases "\
            "that are correctly Predicted Positive."
        r = float(self.conf_mat_rr) / float(self.conf_mat_rr +
                                            self.conf_mat_rb)
        return r

    def precision(self):
        "Return the Precision: Proportion of Predicted Positive cases"\
            "that are correctly Real Positives"
        p = float(self.conf_mat_rr) / float(self.conf_mat_rr +
                                            self.conf_mat_br)
        return p

    def f_measure(self):
        r = float(self.conf_mat_rr) / float(self.conf_mat_rr +
                                            self.conf_mat_rb)
        p = float(self.conf_mat_rr) / float(self.conf_mat_rr +
                                            self.conf_mat_br)
        return 2. * p * r / (p + r)

    def false_positive_rate(self):
        return (float(self.conf_mat_br) /
                float(self.conf_mat_rr + self.conf_mat_br))

    def miss_rate(self):
        return (float(self.conf_mat_rb) /
                float(self.conf_mat_rb + self.conf_mat_bb))

    def predicted_reals(self):
        return self.conf_mat_rr + self.conf_mat_br

    def predicted_bogus(self):
        return self.conf_mat_rb + self.conf_mat_bb

    def total_reals(self):
        return self.conf_mat_rr + self.conf_mat_rb

    def total_bogus(self):
        return self.conf_mat_br + self.conf_mat_bb

    def total_samples(self):
        return (self.conf_mat_rr + self.conf_mat_rb + self.conf_mat_br +
                self.conf_mat_bb)

    def __str__(self):
        if self.platform != '3':
            p_name = self.get_platform_display()
        else:
            if self.other_platform_name is None:
                p_name = "Other"
            else:
                p_name = self.other_platform_name
        return "#{}: {} in {}".format(self.id, self.alg_name, p_name)

    class Meta:
        ordering = ('-date',)


class Feature(models.Model):
    name = models.CharField(max_length=20, unique=True)
    code = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
