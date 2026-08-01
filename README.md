# Valery Firebird 2.5 — prueba de concepto

Prueba el recorrido completo:

`Android -> HTTPS/Dokploy -> FastAPI VPS -> Tailscale -> Windows -> Firebird 2.5`

La única consulta ejecutada es:

```sql
SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE
```

## Componentes

- `frontend/`: mini PWA Vue 3.
- `vps-backend/`: backend público que llama al puente.
- `windows-bridge/`: API privada que consulta Firebird.
- `docs/DEPLOYMENT.md`: instalación y prueba paso a paso.
- `tailscale/policy.hujson`: plantilla restrictiva de Tailscale.

No se incluyen credenciales reales. Copie los archivos `.env.example` y complete
los secretos directamente en Windows y Dokploy.

