"""
Database connection utility.

Provides a single entry point for obtaining a SQLAlchemy engine.
Supports PostgreSQL and MSSQL. The database type and credentials
are read from environment variables, which are loaded from
secrets/.env.secrets when running locally.

Usage:
------
from utils.db import get_engine

engine = get_engine()

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))

# Or with pandas:
df = pd.read_sql("SELECT * FROM users", engine)
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL

# Load secrets from secrets/.env.secrets when running locally.
# In production (Docker / container), environment variables are
# injected directly and this file will simply not be found.
_secrets_path = Path(__file__).parent.parent.parent / "secrets" / ".env.secrets"
if _secrets_path.exists():
    load_dotenv(_secrets_path)


def get_engine() -> Engine:
    """
    Create and return a SQLAlchemy engine based on environment variables.

    Required environment variables
    --------------------------------
    DB_TYPE       : "postgresql" or "mssql"
    DB_HOST       : hostname or IP of the database server
    DB_PORT       : port number (default: 5432 for postgres, 1433 for mssql)
    DB_NAME       : database name
    DB_USER       : username
    DB_PASSWORD   : password

    Optional
    --------
    DB_SCHEMA     : default schema (used as search_path for postgres)

    Raises
    ------
    ValueError if DB_TYPE is not supported.
    """
    db_type = os.environ["DB_TYPE"].lower()
    host = os.environ["DB_HOST"]
    port = os.environ.get("DB_PORT")
    name = os.environ["DB_NAME"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]

    if db_type == "postgresql":
        port = port or "5432"
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=user,
            password=password,
            host=host,
            port=int(port),
            database=name,
        )
        connect_args = {}
        schema = os.environ.get("DB_SCHEMA")
        if schema:
            connect_args["options"] = f"-csearch_path={schema}"
        return create_engine(url, connect_args=connect_args)

    elif db_type == "mssql":
        port = port or "1433"
        url = URL.create(
            drivername="mssql+pyodbc",
            username=user,
            password=password,
            host=host,
            port=int(port),
            database=name,
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "TrustServerCertificate": "yes",
            },
        )
        return create_engine(url, fast_executemany=True)

    else:
        raise ValueError(
            f"Unsupported DB_TYPE '{db_type}'. Use 'postgresql' or 'mssql'."
        )
