# Valery Firebird POC

## Architecture

- The request path is `frontend` (Vue PWA) -> `vps-backend` (public FastAPI) -> Tailscale -> `windows-bridge` (private FastAPI) -> Firebird 2.5. The PoC intentionally executes only `SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE`.
- `frontend/nginx.conf` proxies `/api/` to the Docker service name `backend:8000`; keep backend routes under `/api/` for the deployed frontend to reach them. Vite development instead proxies `/api` to `http://localhost:8000`.
- `docker-compose.yml` requires the external Dokploy network `dokploy-network`. Publish only the `frontend` service on port 80; do not publish the backend or Windows bridge.

## Local Commands

- Frontend commands run from `frontend/`: `pnpm dev` and `pnpm build`. The lockfile is `pnpm-lock.yaml`, although the production Dockerfile currently installs with `npm install`.
- Run the VPS API from `vps-backend/` after installing `requirements.txt`: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers`. It reads `POC_ACCESS_CODE`, `BRIDGE_URL`, `BRIDGE_API_KEY`, and optional `BRIDGE_TIMEOUT_SECONDS` from the environment.
- Set up the Windows bridge from Windows PowerShell with `Set-ExecutionPolicy -Scope Process Bypass; .\scripts\install.ps1`; start it with `.\run.ps1`. Both scripts require `py -3-32`: the Firebird 2.5 client DLL is expected to be 32-bit.

## Security And Operations

- The Windows bridge loads its own `windows-bridge/.env` (not process-only configuration), including `FIREBIRD_CLIENT_LIBRARY`; never commit it. The install script creates it from `.env.example`.
- Every bridge endpoint requires `X-Bridge-Key`; the public status route requires `X-Poc-Code`. Both FastAPI apps deliberately disable `/docs` and `/redoc`.
- `tailscale/policy.hujson` is a template with placeholder IPs. Preserve the rule that only the VPS reaches Windows port 8787, keep Firebird port 3050 unexposed, and retain the VPS public-firewall block outside Tailscale.
- Follow `docs/DEPLOYMENT.md`'s order: verify the keyed VPS-to-Windows bridge request before deploying Dokploy. Its negative checks are the available end-to-end security verification; this repository has no configured automated test, lint, or typecheck command.
