---
name: mssql-openshift
description: Use when connecting to Microsoft SQL Server (MSSQL) from Python, dealing with NTLM authentication, pyodbc or SQLAlchemy with mssql, OpenSSL legacy provider errors, OPENSSL_CONF, or connection string issues on Linux/OpenShift/Docker containers.
---

# MSSQL Connection on Linux / OpenShift (Python)

## The core problem

AXA's MSSQL servers use **NTLM authentication**. On modern Linux with OpenSSL 3.x, the legacy
cryptographic providers required by NTLM are disabled by default. This causes connection failures.

**Fix**: enable the OpenSSL legacy provider via a custom config file.

---

## openssl-legacy.cnf

Create this file at the project root and copy it into the Docker image:

```ini
# openssl-legacy.cnf
# Extend the default openssl config
.include = /etc/ssl/openssl.cnf

openssl_conf = openssl_init

[openssl_init]
providers = provider_sect

[provider_sect]
default = default_sect
legacy = legacy_sect

[default_sect]
activate = 1

[legacy_sect]
activate = 1
```

---

## Dockerfile integration

```dockerfile
COPY openssl-legacy.cnf /openssl-legacy.cnf
ENV OPENSSL_CONF=/openssl-legacy.cnf
```

This must be set **before** any pip install step that involves `pyodbc` or connection setup.

---

## Docker Compose (local dev)

```yaml
environment:
  OPENSSL_CONF: /openssl-legacy.cnf
```

Or bake it into the image as above — no separate env var needed if the Dockerfile already sets it.

---

## Connection string format

The connection string is passed via the `CONNECTION_STRING` environment variable (from a Kubernetes secret / Sealed Secret):

```
mssql+pyodbc://{user}:{password}@{host}/{database}?driver=ODBC+Driver+17+for+SQL+Server&authentication=ActiveDirectoryPassword&TrustServerCertificate=yes
```

Or for NTLM (Windows auth over Kerberos/NTLM):
```
mssql+pyodbc://{user}:{password}@{host}/{database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
```

---

## SQLAlchemy engine setup

NTLM state can become **corrupted** in long-running processes. The engine must be periodically
recycled (every ~60 minutes) and reset on auth failures.

```python
import os
import time
from sqlalchemy import create_engine, event

_engine = None
_engine_created_time = None
_reset_interval_seconds = 3600  # Reset every hour to prevent NTLM state corruption


def _create_engine():
    connection_string = os.environ["CONNECTION_STRING"]
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,
        pool_recycle=3600,   # Recycle connections after 1 hour
        pool_size=5,
        max_overflow=0,
        pool_timeout=30,
    )
    return engine


def get_engine():
    global _engine, _engine_created_time
    if _engine is None:
        _engine = _create_engine()
        _engine_created_time = time.time()
    return _engine


def reset_engine(reason="periodic"):
    """Force engine recreation to clear corrupted NTLM state."""
    global _engine, _engine_created_time
    try:
        if _engine is not None:
            _engine.dispose()
    except Exception:
        pass
    finally:
        _engine = None
        _engine_created_time = None


def should_reset_engine():
    """Return True if engine is older than reset interval."""
    if _engine is None or _engine_created_time is None:
        return False
    return (time.time() - _engine_created_time) > _reset_interval_seconds
```

Call `reset_engine("ntlm_failure")` in exception handlers when you see NTLM/auth errors.
Call `reset_engine("periodic")` on a background check when `should_reset_engine()` returns `True`.

---

## Required system packages (in Dockerfile)

The RHEL-based image (`registry.access.redhat.com/hi/python:3.12-builder`) needs the ODBC driver.
Install via pip wheels if pre-built, or ensure the base image includes `unixODBC` and
`msodbcsql17`/`msodbcsql18`.

Typical `requirements.txt` entries:
```
pyodbc
SQLAlchemy
```

---

## Kubernetes secret

The connection string is stored as a **Sealed Secret** and injected as an env var:

```yaml
# In Deployment spec
env:
  - name: CONNECTION_STRING
    valueFrom:
      secretKeyRef:
        name: aia-connection-string
        key: CONNECTION_STRING
```

```yaml
# In CronJob spec (same pattern)
env:
  - name: CONNECTION_STRING
    valueFrom:
      secretKeyRef:
        name: aia-connection-string
        key: CONNECTION_STRING
```

---

## Startup SQL migration script

Run schema migrations/startup scripts before starting the app server:

```dockerfile
CMD python3 sql_startup.py && exec gunicorn --bind :8080 ...
```

`sql_startup.py` uses `get_engine()` to apply idempotent DDL (CREATE TABLE IF NOT EXISTS, ALTER TABLE, etc.).

---

## Debugging NTLM / OpenSSL issues

```bash
# Verify legacy provider is active inside the container
openssl list -providers

# Expected output includes:
#   legacy
#     name: OpenSSL Legacy Provider

# Test DB connectivity manually
python3 -c "
import os; os.environ['OPENSSL_CONF'] = '/openssl-legacy.cnf'
import pyodbc
conn = pyodbc.connect(os.environ['CONNECTION_STRING'])
print('OK')
"
```

If you see `SSL: WRONG_VERSION_NUMBER` or `DH_KEY_TOO_SMALL`, the legacy provider is not loaded —
check that `OPENSSL_CONF` is set before any Python import that loads OpenSSL.

---

## Common errors and fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `SSL: WRONG_VERSION_NUMBER` | Legacy OpenSSL provider not loaded | Set `OPENSSL_CONF=/openssl-legacy.cnf` before process start |
| `Login failed for user` after hours of uptime | NTLM state corruption | Call `reset_engine("ntlm_failure")` and retry |
| `[08S01] Communication link failure` | Stale connection pool | `pool_pre_ping=True` + `pool_recycle=3600` |
| `No module named pyodbc` | Missing ODBC driver in image | Ensure `unixODBC` + `msodbcsql17` installed in base image |
