from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RoleViewSet, BusinessElementViewSet, AccessRolesRulesViewSet

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'elements', BusinessElementViewSet)
router.register(r'rules', AccessRolesRulesViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
