from django.urls import path
from .views import RegisterView, LoginView, LogoutView, UpdateProfileView, DeleteUserView


app_name = "users"


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UpdateProfileView.as_view(), name="update_profile"),
    path("delete/", DeleteUserView.as_view(), name="delete_user"),
]
