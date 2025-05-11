from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VaccinationDriveViewSet

router = DefaultRouter()
router.register(r'drives', VaccinationDriveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]