from django.contrib import admin
from .models import Ticket, Seguimiento
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'estado', 'prioridad', 'creado_por', 'responsable', 'creado_el')
    list_filter = ('estado', 'prioridad')
    search_fields = ('titulo', 'descripcion')
@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'autor', 'fecha')
