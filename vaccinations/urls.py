from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VaccinationRecordViewSet

router = DefaultRouter()
router.register(r'vaccination-records', VaccinationRecordViewSet, basename='vaccination-records')

urlpatterns = [
    path('', include(router.urls)),
]