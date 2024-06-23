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
    slug = models.SlugField(max_length=50, default='')

    def __str__(self):
        return f'{self.title}, {self.year}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super(Ballot, self).save(*args, **kwargs)
