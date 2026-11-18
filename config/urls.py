from django.contrib import admin
from django.contrib.auth import views as auth_views
from .auth_views import LoginConHorarioView
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginConHorarioView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('tickets.urls')),
]
