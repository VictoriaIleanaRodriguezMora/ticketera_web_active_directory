from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from unittest.mock import patch
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Seguimiento
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

    def test_usuario_solo_ve_sus_tickets(self):
        otro = get_user_model().objects.create_user(username='otro', password='clave-fuerte-123')
        otro.groups.add(Group.objects.get(name='Usuario'))
        Ticket.objects.create(titulo='Privado', descripcion='Otro usuario', creado_por=otro)
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse('ticket_list'))
        self.assertContains(respuesta, 'Prueba')
        self.assertNotContains(respuesta, 'Privado')

    def test_consulta_solo_lectura(self):
        self.client.force_login(self.consulta)
        self.assertEqual(self.client.post(reverse('ticket_comment', args=[self.ticket.pk]), {'texto': 'No permitido'}).status_code, 403)
        self.assertEqual(self.client.get(reverse('ticket_edit', args=[self.ticket.pk])).status_code, 403)

    def test_cambio_estado_se_registra_en_historial(self):
        self.client.force_login(self.operador)
        respuesta = self.client.post(reverse('ticket_edit', args=[self.ticket.pk]), {
            'titulo': 'Prueba', 'descripcion': 'Algo no funciona',
            'estado': 'PROGRESO', 'prioridad': 'MEDIA', 'responsable': '',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.estado, 'PROGRESO')
        self.assertTrue(Seguimiento.objects.filter(ticket=self.ticket, texto__contains='Estado: Abierto -> En progreso').exists())

    def test_busqueda_y_filtro_prioridad(self):
        self.client.force_login(self.operador)
        respuesta = self.client.get(reverse('ticket_list'), {'q': 'Prueba', 'prioridad': 'MEDIA'})
        self.assertContains(respuesta, 'Prueba')
        respuesta = self.client.get(reverse('ticket_list'), {'q': 'inexistente'})
        self.assertNotContains(respuesta, 'Prueba')

    def test_login_fuera_del_horario_bloqueado(self):
        with patch('config.auth_views.timezone.localtime', return_value=datetime(2026, 11, 16, 19, 0, tzinfo=ZoneInfo('America/Argentina/Buenos_Aires'))):
            respuesta = self.client.post(reverse('login'), {'username': 'persona', 'password': 'clave-fuerte-123'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, '08:00 a 18:00')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_dentro_del_horario_permitido(self):
        with patch('config.auth_views.timezone.localtime', return_value=datetime(2026, 11, 16, 10, 0, tzinfo=ZoneInfo('America/Argentina/Buenos_Aires'))):
            respuesta = self.client.post(reverse('login'), {'username': 'persona', 'password': 'clave-fuerte-123'})
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
