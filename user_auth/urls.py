from django.urls import path
from . import views
from .views import MyTokenObtainPairView

urlpatterns = [
    path('register/', views.register_view, name='register'),
    # path('login-old/', views.login_user, name='login_old'),  # your basic session login (optional)
    path('logout/', views.logout_view, name='logout'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT Token login
]