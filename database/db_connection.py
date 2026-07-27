"""
Database connection module.

Provides a singleton MySQLConnectionPool so every repository
reuses the same pool instead of opening a new connection each call.
"""

import logging
import mysql.connector.pooling
from config import DB_CONFIG, POOL_CONFIG

logger = logging.getLogger(__name__)

_pool: mysql.connector.pooling.MySQLConnectionPool | None = None


def get_pool() -> mysql.connector.pooling.MySQLConnectionPool:
    """
    Return the singleton connection pool, creating it on first call.

    Returns:
        MySQLConnectionPool: The shared connection pool.

    Raises:
        mysql.connector.Error: If the pool cannot be created.
    """
    global _pool
    if _pool is None:
        try:
            _pool = mysql.connector.pooling.MySQLConnectionPool(
                **POOL_CONFIG,
                **DB_CONFIG,
            )
            logger.info("Connection pool '%s' created.", POOL_CONFIG["pool_name"])
        except mysql.connector.Error as e:
            logger.error("Failed to create connection pool: %s", e)
            raise
    return _pool


def get_connection() -> mysql.connector.pooling.PooledMySQLConnection:
    """
    Borrow a connection from the pool.

    Returns:
        PooledMySQLConnection: A pooled MySQL connection.

    Raises:
        mysql.connector.Error: If a connection cannot be obtained.
    """
    try:
        return get_pool().get_connection()
    except mysql.connector.Error as e:
        logger.error("Failed to get connection from pool: %s", e)
        raise
