from django.urls import path
from django.contrib.auth.views import LogoutView
from users.views import Profile, SignUp, PasswordChange, PasswordChangeDone, PasswordReset, PasswordResetDone, PasswordResetComplete, PasswordResetConfirm, Login, UserSourceUpdateView, UserSourceCreateView, CategoryCreateView, CategoryUpdate, FavoriteArticles, ToggleFavorite

urlpatterns = [
    path("profile/", Profile.as_view(), name="profile"),
    path("profile/source/create/", UserSourceCreateView.as_view(), name="source_create"),
    path("profile/source/update/<pk>/", UserSourceUpdateView.as_view(), name="source_update"),
    path("profile/category/create/", CategoryCreateView.as_view(), name="category_create"),
    path("profile/category/update/<pk>", CategoryUpdate.as_view(), name="category_update"),
    path("favorite/", FavoriteArticles.as_view(), name="favorite"),
    path("favorite/toggle/<pk>/", ToggleFavorite.as_view(), name="toggle_favorite"),
    path("login/", Login.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password_change/", PasswordChange.as_view(), name="password_change"),
    path("password_change/done/", PasswordChangeDone.as_view(), name="password_change_done"),
    path("password_reset/",PasswordReset.as_view(), name="password_reset"),
    path("password_reset/done/", PasswordResetDone.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirm.as_view(), name="password_reset_confirm"),
    path("password_reset/complete/", PasswordResetComplete.as_view(), name="password_reset_complete"),
    path("signup/", SignUp.as_view(), name="sign_up"),
]