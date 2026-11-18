# Mejoras incrementales para la ticketera (desarrollo local)

Se agregaron: control horario del inicio de sesión (08:00 a 18:00, Argentina), búsqueda por texto, filtro de prioridad, evento inicial de creación y corrección de historial de edición. Se añadieron pruebas de roles y horario.

## Aplicación
Los archivos de este paquete deben COPIARSE al repositorio, conservando `.git`, `README.md`, `configuracion-ad.md`, `.venv` y `db.sqlite3`. Hacer commit en la rama de trabajo luego de probar.

## Comandos
```
source .venv/bin/activate
python manage.py check
python manage.py test tickets
python manage.py runserver 8001
```

## Qué no cubre
No incluye conexión LDAP/Active Directory; son usuarios Django locales de desarrollo. El control horario se aplica a nuevos inicios de sesión, no expira sesiones ya abiertas. Un superusuario también queda sujeto a este horario en la ruta `/login/`, pero el admin de Django utiliza esa misma pantalla si se redirige desde una sesión no autenticada. El historial refleja cambios efectuados a través de `ticket_edit`, no cambios realizados directamente desde Django Admin u otras vías.
