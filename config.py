"""
Database configuration for the IRS project.
Update credentials to match your MySQL environment.
"""

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "irs_db",
}

POOL_CONFIG = {
    "pool_name": "irs_pool",
    "pool_size": 5,
}
