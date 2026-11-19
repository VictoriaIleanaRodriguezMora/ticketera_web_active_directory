from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Group
from ldap3 import Server, Connection, SIMPLE
from ldap3.core.exceptions import LDAPException
from ldap3.utils.conv import escape_filter_chars

ROLES = ('Admin', 'Operador', 'Usuario', 'Consulta')


class ActiveDirectoryBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Una contraseña vacía produce un bind anónimo "exitoso": hay que rechazarla.
        if not username or not password:
            return None
        try:
            server = Server(settings.AD_HOST, port=settings.AD_PORT, connect_timeout=5)
            svc = Connection(server, user=settings.AD_SERVICE_USER,
                             password=settings.AD_SERVICE_PASSWORD, authentication=SIMPLE)
            if not svc.bind():
                return None
            svc.search(settings.AD_BASE_DN,
                       f'(&(objectClass=user)(sAMAccountName={escape_filter_chars(username)}))',
                       attributes=['sAMAccountName', 'memberOf'])
            if not svc.entries:
                return None
            entrada = svc.entries[0]
            user_dn = entrada.entry_dn
            nombre = str(entrada.sAMAccountName)
            grupos_dn = entrada.entry_attributes_as_dict.get('memberOf', [])
            svc.unbind()

            # La contraseña se valida intentando entrar al AD como ese usuario.
            conn = Connection(server, user=user_dn, password=password, authentication=SIMPLE)
            if not conn.bind():
                return None
            conn.unbind()
        except LDAPException:
            return None

        nombres = {dn.split(',')[0].replace('CN=', '', 1) for dn in grupos_dn}
        roles = [r for r in ROLES if r in nombres]

        User = get_user_model()
        user, creado = User.objects.get_or_create(username=nombre)
        if creado:
            user.set_unusable_password()
            user.save()
        user.groups.set([Group.objects.get_or_create(name=r)[0] for r in roles])
        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None