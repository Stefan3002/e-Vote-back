from django.contrib import admin

from e_vote_backend.models import AppUser, Otp, BallotSection, BallotSectionOption
from e_vote_backend.models import Ballot

admin.site.register(AppUser)
admin.site.register(Ballot)
admin.site.register(BallotSection)
admin.site.register(BallotSectionOption)
admin.site.register(Otp)
