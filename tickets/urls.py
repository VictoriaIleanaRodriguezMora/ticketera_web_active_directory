from django.urls import path
from . import views
urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('tickets/nuevo/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:pk>/editar/', views.ticket_edit, name='ticket_edit'),
    path('tickets/<int:pk>/comentario/', views.ticket_comment, name='ticket_comment'),
    path('reportes/csv/', views.ticket_export, name='ticket_export'),
]
