from datetime import date, datetime, time
from threading import Lock

import fdb

from .settings import settings


_api_lock = Lock()
_api_loaded = False


def _serialize(value: datetime | date | time | object) -> str:
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def ping_database() -> dict:
    global _api_loaded

    if not _api_loaded:
        with _api_lock:
            if not _api_loaded:
                fdb.load_api(settings.firebird_client_library)
                _api_loaded = True

    connection = fdb.connect(
        host=settings.firebird_host,
        port=settings.firebird_port,
        database=settings.firebird_database,
        user=settings.firebird_user,
        password=settings.firebird_password,
        charset=settings.firebird_charset,
    )

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

