# Ticketera web con Active Directory

Aplicación web de tickets de soporte, hecha con Django, que autentica a los usuarios contra un Active Directory (`IFTS.local`) y asigna los permisos según los grupos del dominio.

## Funcionalidades

- Inicio de sesión validado contra Active Directory.
- Roles definidos por los grupos del AD: `Admin`, `Operador`, `Usuario` y `Consulta`.
- Inicio de sesión permitido únicamente de 08:00 a 18:00 (hora de Argentina).
- Alta, edición, comentarios e historial de cambios de los tickets.
- Exportación de tickets a CSV.

## Roles

| Rol | Ve | Crea | Edita | Comenta | Exporta CSV |
|---|---|---|---|---|---|
| Admin | Todos | Sí | Sí | Sí | Sí |
| Operador | Todos | Sí | Sí | Sí | Sí |
| Usuario | Solo los suyos | Sí | No | Solo en los suyos | No |
| Consulta | Todos | No | No | No | No |

Un usuario del AD que no pertenezca a ninguno de los cuatro grupos puede autenticarse, pero la aplicación le niega el acceso (error 403).

## Tecnologías

- Python y Django: aplicación web.
- ldap3: conexión y autenticación contra Active Directory.
- SQLite: persistencia de los tickets.
- Bootstrap 5: interfaz.

## Entorno de pruebas (Active Directory)

La app autentica contra un Active Directory (`IFTS.local`) alojado en una VM de VirtualBox. Para probarla se necesita:

- Los grupos `Admin`, `Operador`, `Usuario` y `Consulta`.
- Un usuario de prueba por grupo (`test_admin`, `test_operador`, `test_usuario`, `test_consulta`).
- Una cuenta de servicio de solo lectura (`svc_ticketera`).
- El puerto 389 (LDAP) accesible desde la PC (reenvío de puertos `127.0.0.1:389`).

Guía paso a paso: [docs/configuracion-ad.md](docs/configuracion-ad.md)

## Cómo ejecutar la app

1. Encender la VM del AD y verificar el reenvío del puerto 389.
2. Instalar las dependencias y arrancar el servidor (PowerShell):

```
pip install -r requirements.txt
$env:AD_SERVICE_PASSWORD = "clave_de_svc_ticketera"
python manage.py migrate
python manage.py runserver
```

3. Entrar a http://127.0.0.1:8000 con un usuario del AD (por ejemplo `test_operador`).

La contraseña de la cuenta de servicio no se guarda en el código: se pasa por la variable de entorno `AD_SERVICE_PASSWORD`. Opcionalmente se pueden definir `AD_HOST` y `AD_PORT` (por defecto `127.0.0.1` y `389`).

La primera vez que un usuario del AD inicia sesión, la app crea su usuario local y, en cada inicio de sesión, actualiza su rol según sus grupos del AD.

## Tests

```
python manage.py test
```


## Entorno de pruebas (Active Directory)

La app autentica contra un Active Directory (`IFTS.local`) alojado en una VM de VirtualBox. Para probarla se necesita:

- Los grupos `Admin`, `Operador`, `Usuario` y `Consulta`.
- Un usuario de prueba por grupo (`test_admin`, `test_operador`, `test_usuario`, `test_consulta`).
- Una cuenta de servicio de solo lectura (`svc_ticketera`).
- El puerto 389 (LDAP) accesible desde la PC (reenvío de puertos `127.0.0.1:389`).

Guía paso a paso: [docs/configuracion-ad.md](docs/configuracion-ad.md)
