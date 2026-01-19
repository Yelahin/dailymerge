from django.urls import path, include
from users.views import profile

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("profile/", profile, name="profile")
]