from django.urls import path

from e_vote_backend.views.auth_views import auth_views
from e_vote_backend.views.ballots_views import ballots_views

urlpatterns = [
    path('auth', auth_views.log_in.as_view()),
    path('ballots', ballots_views.all_ballots.as_view()),
    path('otp', auth_views.otp.as_view())
]