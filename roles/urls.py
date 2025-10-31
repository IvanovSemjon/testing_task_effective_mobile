from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RoleViewSet, BusinessElementViewSet, AccessRolesRulesViewSet

app_name = "roles"

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="roles")
router.register(r"elements", BusinessElementViewSet, basename="elements")
router.register(r"rules", AccessRolesRulesViewSet, basename="rules")

urlpatterns = [
    path("", include(router.urls)),
]