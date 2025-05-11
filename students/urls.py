from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet
from .views import StudentCSVUploadView


router = DefaultRouter()
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('', include(router.urls)),
     path('upload-csv/', StudentCSVUploadView.as_view(), name='student-csv-upload'),
]

