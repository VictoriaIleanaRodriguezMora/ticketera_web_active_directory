## Entorno de pruebas (Active Directory)

La app autentica contra un Active Directory (`IFTS.local`) alojado en una VM de VirtualBox. Para probarla se necesita:

- Los grupos `Admin`, `Operador`, `Usuario` y `Consulta`.
- Un usuario de prueba por grupo (`test_admin`, `test_operador`, `test_usuario`, `test_consulta`).
- Una cuenta de servicio de solo lectura (`svc_ticketera`).
- El puerto 389 (LDAP) accesible desde la PC (reenvío de puertos `127.0.0.1:389`).

Guía paso a paso: [docs/configuracion-ad.md](https://github.com/VictoriaIleanaRodriguezMora/ticketera_web_active_directory/blob/main/configuracion-ad.md)
