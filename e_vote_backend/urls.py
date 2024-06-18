from django.urls import path
from e_vote_backend.views.auth_views import auth_views
urlpatterns = [
    path('auth', auth_views.log_in.as_view())
]