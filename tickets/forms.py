from django import forms
from django.contrib.auth import get_user_model
from .models import Ticket, Seguimiento

class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titulo', 'descripcion', 'prioridad']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}

class TicketEditForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titulo', 'descripcion', 'estado', 'prioridad', 'responsable']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}

class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = Seguimiento
        fields = ['texto']
        widgets = {forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribí un comentario...'})}
