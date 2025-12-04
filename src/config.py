"""Centralized configuration for distributed database system."""

from typing import Literal

# DBMS Configuration
DBMS_CONNECTIONS = {
    "DBMS1": "postgresql://ddbs:ddbs@localhost:5434/ddbs1",
    "DBMS2": "postgresql://ddbs:ddbs@localhost:5433/ddbs2",
    "DBMS-STANDBY": "postgresql://ddbs:ddbs@localhost:5435/ddbs1",  # Shared standby
}

DBMS_STANDBY_MAP = {
    "DBMS1": "DBMS-STANDBY",
    "DBMS2": "DBMS-STANDBY",  # Same standby for both
}

# Data Center Mapping
DBMS_TO_DATACENTER = {
    "DBMS1": "DC1",  # Beijing
    "DBMS2": "DC2",  # Hong Kong
    "DBMS-STANDBY": "STANDBY",  # Shared
}

# Redis Configuration
REDIS_CONNECTIONS = {
    "DC1": {"host": "localhost", "port": 6379},
    "DC2": {"host": "localhost", "port": 6381},
    "STANDBY": {"host": "localhost", "port": 6380},  # Shared standby
}

# Redis Standby Mapping
REDIS_STANDBY_MAP = {
    "DC1": "STANDBY",
    "DC2": "STANDBY",  # Same standby for both
}

# Cache Configuration
CACHE_TTL = 60
CACHE_KEY_PREFIX = "query"

# HDFS Configuration
HDFS_CONFIG = {
    "namenode": "namenode",
    "port": 9000,
    "web_port": 9870,
    "base_path": "/articles",
    "replication": 2,
}


def get_redis_for_datacenter(datacenter: Literal["DC1", "DC2", "STANDBY"]) -> dict:
    """Get Redis connection info for a datacenter."""
    return REDIS_CONNECTIONS[datacenter]


def get_datacenter_for_dbms(dbms: str) -> str:
    """Get datacenter for a given DBMS."""
    return DBMS_TO_DATACENTER.get(dbms, "DC1")


def get_standby_redis_for_datacenter(datacenter: Literal["DC1", "DC2"]) -> dict:
    """Get standby Redis connection for a datacenter."""
    standby = REDIS_STANDBY_MAP[datacenter]
    return REDIS_CONNECTIONS[standby]
