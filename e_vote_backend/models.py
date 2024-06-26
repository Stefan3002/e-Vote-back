from django.db import models
from django.template.defaultfilters import slugify


class AppUser(models.Model):
    username = models.CharField(max_length=50)
    public_key = models.CharField(max_length=210)
    challenge_issued = models.CharField(max_length=100)
    challenge_burnt = models.BooleanField(default=False)
    email = models.EmailField(max_length=50)
    def __str__(self):
        return self.username + ' ' + self.public_key


class Otp(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='otp')
    otp = models.CharField(max_length=6)
    valid = models.BooleanField(default=True)
    generation_date = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)


class Ballot(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    year = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    eligible_people = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, default='', unique=True, null=True, blank=True)

    def __str__(self):
        return f'{self.title}, {self.year}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super(Ballot, self).save(*args, **kwargs)


class BallotSection(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, default='', unique=True, null=True, blank=True)
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super(BallotSection, self).save(*args, **kwargs)


class BallotSectionOption(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, default='', unique=True, null=True, blank=True)
    ballot_section = models.ForeignKey(BallotSection, on_delete=models.CASCADE, related_name='options')
    option_id = models.IntegerField()

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super(BallotSectionOption, self).save(*args, **kwargs)
