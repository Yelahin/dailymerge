from django.urls import path, include
from users.views import profile, SignUp

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("profile/", profile, name="profile"),
    path("accounts/signup/", SignUp.as_view(), name="sign_up")
]