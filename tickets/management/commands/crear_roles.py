from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
class Command(BaseCommand):
    help = 'Crea los cuatro grupos para pruebas locales (NO reemplaza AD).'
    def handle(self, *args, **kwargs):
        for nombre in ('Admin', 'Operador', 'Usuario', 'Consulta'):
            Group.objects.get_or_create(name=nombre)
        self.stdout.write(self.style.SUCCESS('Grupos creados: Admin, Operador, Usuario, Consulta'))
