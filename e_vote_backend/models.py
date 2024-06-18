from django.db import models


class AppUser(models.Model):
    username = models.CharField(max_length=50)
    public_key = models.CharField(max_length=210)
    challenge_issued = models.CharField(max_length=50)
    challenge_burnt = models.BooleanField(default=False)

    def __str__(self):
        return self.username + ' ' + self.public_key
