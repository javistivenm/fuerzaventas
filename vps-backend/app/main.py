from datetime import datetime, timezone
from secrets import compare_digest

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    poc_access_code: str
    bridge_url: str
    bridge_api_key: str
    bridge_timeout_seconds: float = 10


settings = Settings()
app = FastAPI(title="Valery POC VPS API", docs_url=None, redoc_url=None)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "service": "vps-backend"}


@app.get("/api/poc/status")
async def poc_status(x_poc_code: str = Header(alias="X-Poc-Code")) -> dict:
    if not compare_digest(x_poc_code, settings.poc_access_code):
        raise HTTPException(status_code=401, detail="Código de acceso incorrecto.")

    bridge_status = {"ok": False, "message": "No fue posible llegar a Windows."}
    firebird_status = {"ok": False, "message": "No comprobado.", "server_time": None}

    try:
        async with httpx.AsyncClient(timeout=settings.bridge_timeout_seconds) as client:
            response = await client.get(
                f"{settings.bridge_url.rstrip('/')}/v1/firebird/ping",
                headers={"X-Bridge-Key": settings.bridge_api_key},
            )
            response.raise_for_status()
            body = response.json()

        bridge_status = {
            "ok": True,
            "message": f"Respondió en {body.get('duration_ms', 0)} ms.",
        }
        firebird_status = {
            "ok": bool(body.get("ok")),
            "message": body.get("message", "Consulta completada."),
            "server_time": body.get("server_time"),
            "server_version": body.get("server_version"),
        }
    except httpx.HTTPStatusError as exc:
        bridge_status = {
            "ok": True,
            "message": f"Windows respondió HTTP {exc.response.status_code}.",
        }
        firebird_status["message"] = "El puente no pudo completar la consulta."
    except httpx.RequestError as exc:
        bridge_status["message"] = f"Error de red: {type(exc).__name__}."

    return {
        "ok": bridge_status["ok"] and firebird_status["ok"],
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "vps": {"ok": True, "message": "Backend público operativo."},
        "bridge": bridge_status,
        "firebird": firebird_status,
    }

