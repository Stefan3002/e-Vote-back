from django.contrib import admin

from e_vote_backend.models import AppUser, Otp
from e_vote_backend.models import Ballot

admin.site.register(AppUser)
admin.site.register(Ballot)
admin.site.register(Otp)
