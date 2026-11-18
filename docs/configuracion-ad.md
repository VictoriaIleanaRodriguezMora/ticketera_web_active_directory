# Configuración del Active Directory para pruebas

Guía para preparar el AD (`IFTS.local`) contra el que se prueba la ticketera.

## Resumen

Ingresar en la VM con `IFTS\Administrador` y dejar listo lo siguiente:

- 4 grupos de AD: `Admin`, `Operador`, `Usuario`, `Consulta`.
- 1 usuario de prueba por grupo.
- 1 cuenta de servicio (`svc_ticketera`) con permiso de solo lectura, para que la app consulte el AD.
- Puerto 389 (LDAP) accesible desde fuera de la VM. En VirtualBox requiere red en modo puente o reenvío de puertos.

| Usuario | Grupo |
| --- | --- |
| test_admin | Admin |
| test_operador | Operador |
| test_usuario | Usuario |
| test_consulta | Consulta |

## 1. Crear los 4 grupos

1. Abrir **Active Directory Administrative Center**.
2. Seleccionar **IFTS (local) → Users**.
3. En el menú de Users: **New → Group**.
4. Completar:
   - **Group name:** `Admin`
   - **Group scope:** Global
   - **Group type:** Security
5. **OK** y repetir con `Operador`, `Usuario` y `Consulta`.

**Verificación:** escribir el nombre en el cuadro **Filter** (por ejemplo `Admin`) o recorrer la lista de Users; deben aparecer con tipo *Group*. Con doble clic se abre *Properties* y se ven los miembros (*Members*).

## 2. Crear los 4 usuarios

1. En **Active Directory Administrative Center**, seleccionar **IFTS (local) → Users**.
2. **New → User** y completar:
   - **Full name:** `test_admin`
   - **User UPN logon:** `test_admin` (el dominio se completa solo)
   - **User SamAccountName logon:** `test_admin`
   - **Password / Confirm password:** debe cumplir la política de complejidad (mayúscula, minúscula, número y símbolo, mínimo 7 caracteres).
3. Destildar **User must change password at next logon**; si no, el login desde la app falla. Para eso, en **Other password options** tildar **Password never expires**.
4. En **Member Of** de la misma ventana: **Add…** → escribir el grupo (`Admin`) → seleccionar `Admin (IFTS.local/Users)` → **OK** dos veces.
5. **OK** y repetir con `test_operador`, `test_usuario` y `test_consulta`.

**Si se olvidó asignar el grupo al crear el usuario:**

1. Seleccionar el usuario en la lista.
2. En el panel derecho: **Add to group…**
3. Escribir el nombre del grupo → **Check Names** → **OK**.

Para confirmar, abrir el grupo (doble clic) → **Members**: debe figurar el usuario.

## 3. Crear la cuenta de servicio

1. **Users → New → User**, igual que un usuario común.
2. Completar **Full name**, **UPN** y **SamAccountName** con `svc_ticketera`.
3. Definir la contraseña (misma política de complejidad).
4. Destildar **User must change password at next log on** y tildar **Password never expires**. Opcionalmente, tildar también **User cannot change password**.
5. **OK**.

## 4. Verificar el puerto 389 (LDAP)

Son dos comprobaciones: una dentro de la VM y otra desde la PC que la aloja.

### Dentro de la VM

En **Inicio**, abrir CMD o PowerShell y ejecutar:

```
ipconfig
netstat -an | findstr :389
```

- `ipconfig`: anotar la IPv4.
- `netstat`: debe aparecer una línea `0.0.0.0:389 ... LISTENING`, lo que confirma que el AD está escuchando.

### Desde la PC (host)

1. En **Oracle VirtualBox**, seleccionar la VM (en nuestro caso, **PP3**).
2. **Configuración** (engranaje naranja) → **Red**.
3. Pestaña **Adaptador 1** → botón **Reenvío de puertos**.
4. Con el ícono **+** agregar una regla y editar los campos (doble clic):

   | Campo | Valor |
   | --- | --- |
   | Nombre | LDAP |
   | Protocolo | TCP |
   | IP anfitrión | 127.0.0.1 |
   | Puerto anfitrión | 389 |
   | IP invitado | 10.0.2.15 (la IPv4 que muestra `ipconfig`) |
   | Puerto invitado | 389 |

5. **Aceptar** en las dos ventanas.
6. Desde PowerShell en la PC:

   ```powershell
   Test-NetConnection -ComputerName 127.0.0.1 -Port 389
   ```

**Resultado esperado:** `TcpTestSucceeded : True`.

Si da `False`, las causas más comunes son:

- **Reenvío de puertos mal configurado:** revisar que la regla exista, con IP anfitrión `127.0.0.1`, puertos 389/389 e IP invitado igual a la IPv4 de `ipconfig` en la VM (normalmente `10.0.2.15`).
- **Firewall de Windows en la VM:** revisar que la regla de LDAP esté habilitada (normalmente la crea el AD solo).
