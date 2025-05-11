from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('user_auth.urls')),  
    path('students/', include('students.urls')),
    path('drives/', include('drives.urls')),
    path('vaccinations/', include('vaccinations.urls')),
    path('reports/', include('reports.urls')),
]