from datetime import date, datetime, time
from threading import Lock

import fdb

from .settings import settings


_api_lock = Lock()
_api_loaded = False


def _serialize(value: datetime | date | time | object) -> str:
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _connect() -> fdb.Connection:
    global _api_loaded

    if not _api_loaded:
        with _api_lock:
            if not _api_loaded:
                fdb.load_api(settings.firebird_client_library)
                _api_loaded = True

    return fdb.connect(
        host=settings.firebird_host,
        port=settings.firebird_port,
        database=settings.firebird_database,
        user=settings.firebird_user,
        password=settings.firebird_password,
        charset=settings.firebird_charset,
    )


def ping_database() -> dict:
    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE")
        row = cursor.fetchone()
        return {
            "server_time": _serialize(row[0]),
            "server_version": connection.server_version,
        }
    finally:
        connection.close()


def find_client(code: str) -> dict[str, str] | None:
    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT CODIGO, NOMBRE, DIRECCION, TELEFONOS "
            "FROM CLIENTES WHERE TRIM(CODIGO) = ?",
            (code,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        return {
            "code": row[0].strip(),
            "name": (row[1] or "").strip(),
            "address": (row[2] or "").strip(),
            "phones": (row[3] or "").strip(),
        }
    finally:
        connection.close()
