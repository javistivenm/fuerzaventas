import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from secrets import compare_digest
from time import perf_counter

from fastapi import FastAPI, Header, HTTPException

from .firebird import ping_database
from .settings import settings


log_path = Path(settings.bridge_log_file)
log_path.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("valery-bridge")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    log_path,
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

app = FastAPI(title="Valery Windows Bridge", docs_url=None, redoc_url=None)


def require_bridge_key(value: str) -> None:
    if not compare_digest(value, settings.bridge_api_key):
        logger.warning("rejected_request reason=invalid_key")
        raise HTTPException(status_code=401, detail="No autorizado.")


@app.get("/health")
async def health(x_bridge_key: str = Header(alias="X-Bridge-Key")) -> dict:
    require_bridge_key(x_bridge_key)
    return {"ok": True, "service": "windows-bridge"}


@app.get("/v1/firebird/ping")
async def firebird_ping(x_bridge_key: str = Header(alias="X-Bridge-Key")) -> dict:
    require_bridge_key(x_bridge_key)
    started = perf_counter()

    try:
        result = await asyncio.wait_for(asyncio.to_thread(ping_database), timeout=10)
        duration_ms = round((perf_counter() - started) * 1000)
        logger.info("firebird_ping ok=true duration_ms=%s", duration_ms)
        return {
            "ok": True,
            "message": "Firebird respondió correctamente.",
            "duration_ms": duration_ms,
            **result,
        }
    except TimeoutError:
        logger.exception("firebird_ping ok=false reason=timeout")
        raise HTTPException(status_code=504, detail="Firebird excedió el tiempo límite.")
    except Exception as exc:
        logger.exception("firebird_ping ok=false error_type=%s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="No fue posible consultar Firebird.")

