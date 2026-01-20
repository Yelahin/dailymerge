from django.urls import path, include
from users.views import profile, SignUp, PasswordChange, PasswordChangeDone

urlpatterns = [
    path("accounts/password_change/", PasswordChange.as_view(), name="password_change"),
    path("accounts/password_change/done/", PasswordChangeDone.as_view(), name="password_change_done"),
    path("profile/", profile, name="profile"),
    path("accounts/signup/", SignUp.as_view(), name="sign_up"),
    path("accounts/", include("django.contrib.auth.urls")),
]