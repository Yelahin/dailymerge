from django.urls import path
from django.contrib.auth.views import LogoutView
from users.views import HomePageListView, ProfileView, PendingView, SignUpView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView, LoginView, UserSourceUpdateView, UserSourceCreateView, CategoryCreateView, CategoryUpdateView, FavoriteArticlesView, ToggleFavoriteView

urlpatterns = [
    path("", HomePageListView.as_view(), name="home"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/source/create/", UserSourceCreateView.as_view(), name="source_create"),
    path("profile/source/update/<pk>/", UserSourceUpdateView.as_view(), name="source_update"),
    path("profile/category/create/", CategoryCreateView.as_view(), name="category_create"),
    path("profile/category/update/<pk>", CategoryUpdateView.as_view(), name="category_update"),
    path("category/favorite/", FavoriteArticlesView.as_view(), name="favorite"),
    path("favorite/toggle/<pk>/", ToggleFavoriteView.as_view(), name="toggle_favorite"),
    path("pending/", PendingView.as_view(), name="pending"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password_change/", PasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password_reset/",PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password_reset/complete/", PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("signup/", SignUpView.as_view(), name="sign_up"),
]