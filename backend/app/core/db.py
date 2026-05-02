from psycopg2 import pool as pg_pool
from psycopg2 import OperationalError
from app.core.config import get_settings
import threading

_pool: pg_pool.ThreadedConnectionPool = None
_pool_lock = threading.Lock()


def _build_pool() -> pg_pool.ThreadedConnectionPool:
    s = get_settings()
    return pg_pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=s.db_host,
        port=s.db_port,
        user=s.db_user,
        password=s.db_password,
        dbname=s.db_name,
        sslmode=s.db_sslmode,
        # ✅ Keepalives: evitan que Neon cierre la conexión SSL por inactividad
        keepalives=1,
        keepalives_idle=30,      # segundos sin actividad antes del primer probe
        keepalives_interval=10,  # segundos entre probes
        keepalives_count=5,      # intentos antes de declarar muerta la conexión
        connect_timeout=10,
    )


def init_pool():
    global _pool
    with _pool_lock:
        if _pool is None:
            _pool = _build_pool()


def close_pool():
    global _pool
    with _pool_lock:
        if _pool:
            _pool.closeall()
            _pool = None


def _reset_pool():
    """Cierra el pool actual y crea uno nuevo."""
    global _pool
    with _pool_lock:
        if _pool:
            try:
                _pool.closeall()
            except Exception:
                pass
        _pool = _build_pool()


def _is_conn_alive(conn) -> bool:
    """Verifica si la conexión SSL sigue activa con un ping liviano."""
    try:
        if conn.closed:
            return False
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:
        return False


class _PooledConn:
    """Wraps a psycopg2 connection; close() devuelve al pool en vez de cerrar."""
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        try:
            # Si la conexión quedó rota, descartarla del pool
            if self._conn.closed:
                self._pool.putconn(self._conn, close=True)
            else:
                self._pool.putconn(self._conn)
        except Exception:
            pass


def get_db_connection() -> _PooledConn:
    global _pool
    if _pool is None:
        init_pool()

    max_intentos = 3
    for intento in range(max_intentos):
        try:
            conn = _pool.getconn()

            # ✅ Validar que la conexión SSL sigue viva
            if not _is_conn_alive(conn):
                # Descartar esta conexión muerta y pedir otra
                try:
                    _pool.putconn(conn, close=True)
                except Exception:
                    pass
                if intento == max_intentos - 1:
                    # Último intento: resetear todo el pool
                    _reset_pool()
                continue

            return _PooledConn(conn, _pool)

        except OperationalError:
            # Pool o conexión irrecuperable → resetear
            _reset_pool()
        except Exception as e:
            if intento == max_intentos - 1:
                raise Exception(f"No se pudo obtener conexión a BD después de {max_intentos} intentos: {e}")
            _reset_pool()

    raise Exception("No se pudo establecer conexión a la base de datos")
