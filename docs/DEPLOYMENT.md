# Despliegue de la prueba

## 1. Recoger el estado actual

No cambie todavía las reglas de Tailscale. Ejecute y guarde la salida:

### Windows

```powershell
tailscale status
tailscale ip -4
Get-NetTCPConnection -LocalPort 3050 -ErrorAction SilentlyContinue
Get-Item "C:\Program Files (x86)\Firebird\Firebird_2_5\bin\fbclient.dll"
```

### VPS Ubuntu 24.04

```bash
sudo tailscale status
sudo tailscale ip -4
sudo tailscale ping windows-firebird
```

La política de `tailscale/policy.hujson` es una plantilla. Compare primero su
política actual para no perder la regla que bloquea el acceso público al VPS.
Las reglas de Tailscale controlan tráfico de la tailnet; el bloqueo de la IP
pública debe seguir existiendo también en UFW, nftables o el firewall del VPS.

## 2. Puente Windows

La ruta `Program Files (x86)` indica que el cliente Firebird probablemente es
de 32 bits. Instale Python de 32 bits y confirme que el selector funciona:

```powershell
py -3-32 -c "import struct; print(struct.calcsize('P') * 8)"
```

Desde `windows-bridge`:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install.ps1
notepad .env
.\run.ps1
```

Edite como mínimo:

- `BRIDGE_HOST`: IP Tailscale de Windows.
- `BRIDGE_API_KEY`: secreto aleatorio.
- `FIREBIRD_DATABASE`: alias o ruta real de la base Valery.
- `FIREBIRD_USER` y `FIREBIRD_PASSWORD`.
- `FIREBIRD_CHARSET`.

No use `SYSDBA` en la aplicación. Cree un usuario exclusivo con permiso mínimo.

Prueba local:

```powershell
$Headers = @{ "X-Bridge-Key" = "EL_SECRETO" }
Invoke-RestMethod `
  -Uri "http://IP_TAILSCALE_WINDOWS:8787/v1/firebird/ping" `
  -Headers $Headers
```

## 3. Firewall de Windows

Después de conocer ambas IP Tailscale, ejecute como administrador:

```powershell
New-NetFirewallRule `
  -DisplayName "Valery POC Bridge from VPS" `
  -Direction Inbound `
  -Action Allow `
  -Protocol TCP `
  -LocalAddress "IP_TAILSCALE_WINDOWS" `
  -LocalPort 8787 `
  -RemoteAddress "IP_TAILSCALE_VPS"
```

No cree ninguna regla entrante para el puerto 3050.

## 4. Prueba desde el VPS

```bash
curl --fail-with-body \
  -H 'X-Bridge-Key: EL_SECRETO' \
  http://IP_TAILSCALE_WINDOWS:8787/v1/firebird/ping
```

No continúe con Dokploy hasta que esta llamada funcione.

## 5. Dokploy

1. Suba este repositorio a un repositorio Git privado.
2. Cree un proyecto y un ambiente `poc`.
3. Cree un servicio Docker Compose.
4. Use `docker-compose.yml`.
5. Cree estas variables protegidas:

```dotenv
POC_ACCESS_CODE=CODIGO_PARA_EL_CELULAR
BRIDGE_URL=http://IP_TAILSCALE_WINDOWS:8787
BRIDGE_API_KEY=EL_SECRETO_DEL_PUENTE
BRIDGE_TIMEOUT_SECONDS=10
```

6. En Domains, publique el servicio `frontend` por el puerto `80`.
7. Asigne `subdominio.axlabz.xyz` y active HTTPS.
8. No publique el servicio `backend`.

## 6. Android

Abra `https://subdominio.axlabz.xyz`, introduzca `POC_ACCESS_CODE` y pulse
**Probar conexión**. El código se conserva solo durante la sesión de la pestaña.

## 7. Pruebas negativas

- La IP pública de Windows no debe responder en 8787 ni 3050.
- Una solicitud al puente sin `X-Bridge-Key` debe devolver 401.
- Un equipo distinto del VPS no debe alcanzar Windows:8787.
- El dominio público no debe exponer `/docs` en ninguna API.

## Siguiente paso

Una vez aprobada la PoC, instale el puente como servicio con WinSW o NSSM,
active reinicio automático y reemplace la consulta de sistema por una consulta
de negocio parametrizada y de solo lectura.

