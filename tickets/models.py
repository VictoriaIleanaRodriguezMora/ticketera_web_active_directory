from django.conf import settings
from django.db import models

class Ticket(models.Model):
    class Estado(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        PROGRESO = 'PROGRESO', 'En progreso'
        RESUELTO = 'RESUELTO', 'Resuelto'
        CERRADO = 'CERRADO', 'Cerrado'

    class Prioridad(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRITICA', 'Crítica'

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ABIERTO)
    prioridad = models.CharField(max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='tickets_creados')
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_asignados')
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_el']

    def __str__(self):
        return f'#{self.pk} {self.titulo}'

class Seguimiento(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='seguimientos')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha', 'pk']
