from django.core.exceptions import PermissionDenied

def rol(usuario):
    if not usuario.is_authenticated:
        return None
    if usuario.is_superuser or usuario.groups.filter(name='Admin').exists():
        return 'Admin'
    for nombre in ['Operador', 'Usuario', 'Consulta']:
        if usuario.groups.filter(name=nombre).exists():
            return nombre
    return None

def puede_ver(usuario, ticket):
    r = rol(usuario)
    return r in ('Admin', 'Operador', 'Consulta') or (r == 'Usuario' and ticket.creado_por_id == usuario.pk)

def exigir_rol(usuario, *roles):
    if rol(usuario) not in roles:
        raise PermissionDenied('No tenés permiso para realizar esta acción.')
