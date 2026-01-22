from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from users.views import profile, SignUp, PasswordChange, PasswordChangeDone, PasswordReset, PasswordResetDone, PasswordResetComplete, PasswordResetConfirm

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password_change/", PasswordChange.as_view(), name="password_change"),
    path("password_change/done/", PasswordChangeDone.as_view(), name="password_change_done"),
    path("password_reset/",PasswordReset.as_view(), name="password_reset"),
    path("password_reset/done/", PasswordResetDone.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirm.as_view(), name="password_reset_confirm"),
    path("password_reset/complete/", PasswordResetComplete.as_view(), name="password_reset_complete"),
    path("signup/", SignUp.as_view(), name="sign_up"),
]