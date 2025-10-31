# auth_system_project/project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("auth_system_project.users.urls", namespace="users")),
    path("roles/", include("auth_system_project.roles.urls", namespace="roles")),
    path("business/", include("auth_system_project.business.urls", namespace="business")),
]