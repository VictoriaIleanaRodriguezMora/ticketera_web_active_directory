# Avance inicial de Ticketera Web con AD

Incluye una aplicación Django con persistencia SQLite de tickets, estados,
prioridades, responsables, comentarios, historial básico, filtros, CSV y
roles locales de prueba. **No incluye todavía autenticación AD ni restricción
horaria.** No presentar el login local como si fuera Active Directory.

## Instalación (Mac/Linux)

Desde la raíz del repo:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py makemigrations tickets
python manage.py migrate
python manage.py crear_roles
python manage.py createsuperuser
python manage.py runserver
```

Ingresá a http://127.0.0.1:8000/admin/, creá usuarios adicionales y asignalos
a los grupos `Operador`, `Usuario` y `Consulta` en Usuarios > Grupos.
El superusuario actúa como Admin en la app. Entrá a `/login/` con las cuentas.

## Qué queda pendiente

- Autenticación REAL contra `IFTS.local` mediante LDAP y conexión VM VirtualBox
- Restricción de login a 08:00–18:00 hora Buenos Aires
- Sincronizar grupos AD con roles
- Mejorar historial estructurado, permisos de reportes, reportes avanzados
- Capturas de evidencia y documentación técnica final

## Seguridad

El `SECRET_KEY` por defecto, `DEBUG=True` y usuarios locales son **solo para desarrollo**.
No publicar sin configurar entorno seguro, HTTPS, secreto de producción y AD.
No subir `.venv`, `.env`, SQLite ni contraseñas al repositorio.
