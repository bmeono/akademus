from psycopg2 import pool as pg_pool
from app.core.config import get_settings
import threading

_pool: pg_pool.ThreadedConnectionPool = None
_pool_lock = threading.Lock()


def init_pool():
    global _pool
    with _pool_lock:
        if _pool is None:
            s = get_settings()
            _pool = pg_pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                host=s.db_host,
                port=s.db_port,
                user=s.db_user,
                password=s.db_password,
                dbname=s.db_name,
                sslmode=s.db_sslmode,
            )


def close_pool():
    global _pool
    with _pool_lock:
        if _pool:
            _pool.closeall()
            _pool = None


class _PooledConn:
    """Wraps a psycopg2 connection; close() returns it to the pool instead of closing it."""

    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        try:
            self._pool.putconn(self._conn)
        except Exception:
            pass


def get_db_connection() -> _PooledConn:
    global _pool
    if _pool is None:
        init_pool()
    
    try:
        conn = _pool.getconn()
        return _PooledConn(conn, _pool)
    except Exception as e:
        # Pool exhausted, try to create a new pool
        if _pool:
            try:
                _pool.closeall()
            except:
                pass
        _pool = None
        init_pool()
        return _PooledConn(_pool.getconn(), _pool)