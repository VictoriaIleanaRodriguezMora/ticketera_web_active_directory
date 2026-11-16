from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from .models import Ticket

class TicketTests(TestCase):
    def setUp(self):
        U = get_user_model()
        self.usuario = U.objects.create_user(username='persona', password='clave-fuerte-123')
        self.operador = U.objects.create_user(username='operador', password='clave-fuerte-123')
        self.consulta = U.objects.create_user(username='consulta', password='clave-fuerte-123')
        for nombre, persona in [('Usuario', self.usuario), ('Operador', self.operador), ('Consulta', self.consulta)]:
            grupo, _ = Group.objects.get_or_create(name=nombre)
            persona.groups.add(grupo)
        self.ticket = Ticket.objects.create(titulo='Prueba', descripcion='Algo no funciona', creado_por=self.usuario)

    def test_sin_login_redirige(self):
        self.assertEqual(self.client.get(reverse('ticket_list')).status_code, 302)

    def test_usuario_crea_ticket(self):
        self.client.force_login(self.usuario)
        res = self.client.post(reverse('ticket_create'), {'titulo': 'Nuevo', 'descripcion': 'Consulta', 'prioridad': 'ALTA'})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Ticket.objects.count(), 2)

    def test_usuario_no_puede_editar(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse('ticket_edit', args=[self.ticket.pk])).status_code, 403)

    def test_operador_exporta(self):
        self.client.force_login(self.operador)
        self.assertEqual(self.client.get(reverse('ticket_export')).status_code, 200)

    def test_consulta_no_crea(self):
        self.client.force_login(self.consulta)
        self.assertEqual(self.client.get(reverse('ticket_create')).status_code, 403)
