---
name: db-access
description: Use when accessing a database from Python — whether raw SQL queries or SQLAlchemy ORM — with MSSQL or PostgreSQL/Cloud SQL. Covers engine setup, raw query patterns, ORM model definitions, sessions, and when to choose one approach over the other.
---

# Database Access Patterns

Two supported approaches: **raw SQL** (via SQLAlchemy Core / `pd.read_sql`) or **SQLAlchemy ORM**.
Both work with MSSQL and PostgreSQL/Cloud SQL. The choice is made during spec and recorded in `SPEC.md`.

---

## When to choose which

| | Raw SQL | ORM |
|---|---|---|
| Primarily read data for display | ✅ simpler | overkill |
| Complex joins / aggregations | ✅ easier to write and reason about | verbose |
| Write-heavy app (create/update/delete) | possible but tedious | ✅ cleaner |
| Relationships between entities | manual | ✅ handled automatically |
| Schema migrations needed | manual DDL | ✅ Alembic integration |
| Team familiar with SQL | ✅ | requires ORM knowledge |

A hybrid is also fine: ORM for writes/relationships, raw SQL for complex read queries.

---

## Engine setup

### MSSQL (OpenShift / local)

See `mssql-openshift` skill for `OPENSSL_CONF` and NTLM details.

```python
# src/db_utility.py
import os
from sqlalchemy import create_engine

def _create_engine():
    return create_engine(
        os.environ["CONNECTION_STRING"],
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=0,
        pool_timeout=30,
    )
```

Connection string format (from env / Kubernetes secret):
```
mssql+pyodbc://{user}:{password}@{host}/{database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
```

### PostgreSQL / Cloud SQL (GCP)

```python
from axach_gcp_helpers import GCP

gcp = GCP("axach-myproject-dev")
engine = gcp.get_cloudsql_engine()  # SQLAlchemy engine, ready to use
```

See `gcp-patterns` skill for `gcp_project_configs` secret and SSL cert setup.

---

## Option A — Raw SQL

Best for data-heavy read apps, dashboards, and complex queries.

### Read into DataFrame (for Dash tables / charts)

```python
import pandas as pd
from db_utility import get_engine

def get_orders(status: str) -> pd.DataFrame:
    query = """
        SELECT o.id, o.created_at, u.name AS user_name, o.total
        FROM orders o
        JOIN users u ON u.id = o.user_id
        WHERE o.status = :status
        ORDER BY o.created_at DESC
    """
    with get_engine().connect() as conn:
        return pd.read_sql(query, conn, params={"status": status})
```

Always use **named parameters** (`:param`) — never f-strings with user input (SQL injection risk).

### Execute writes (INSERT / UPDATE / DELETE)

```python
from sqlalchemy import text
from db_utility import get_engine

def update_status(order_id: int, new_status: str) -> None:
    with get_engine().begin() as conn:          # begin() = auto-commit on success
        conn.execute(
            text("UPDATE orders SET status = :status WHERE id = :id"),
            {"status": new_status, "id": order_id}
        )
```

`engine.begin()` commits on exit, rolls back on exception.

### Startup / schema creation

```python
from sqlalchemy import text
from db_utility import get_engine

def run_startup_sql():
    with get_engine().begin() as conn:
        conn.execute(text("""
            IF NOT EXISTS (
                SELECT 1 FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = 'orders'
            )
            CREATE TABLE orders (
                id INT IDENTITY PRIMARY KEY,
                status NVARCHAR(50) NOT NULL,
                created_at DATETIME2 DEFAULT GETDATE()
            )
        """))
```

---

## Option B — SQLAlchemy ORM

Best for write-heavy apps with multiple related entities.

### Model definitions

```python
# src/models.py
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(50), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="orders")
```

### Session factory

```python
# src/db_utility.py  (add to existing engine setup)
from sqlalchemy.orm import sessionmaker, Session as SASession
from models import Base

SessionFactory = sessionmaker(bind=get_engine())

def get_session() -> SASession:
    return SessionFactory()
```

### CRUD patterns

```python
from db_utility import get_session
from models import Order, User

# Read
def get_open_orders() -> list[Order]:
    with get_session() as session:
        return session.query(Order).filter_by(status="open").all()

# Create
def create_order(user_id: int) -> Order:
    with get_session() as session:
        order = Order(user_id=user_id, status="open")
        session.add(order)
        session.commit()
        session.refresh(order)
        return order

# Update
def close_order(order_id: int) -> None:
    with get_session() as session:
        order = session.get(Order, order_id)
        if order:
            order.status = "closed"
            session.commit()

# Delete
def delete_order(order_id: int) -> None:
    with get_session() as session:
        order = session.get(Order, order_id)
        if order:
            session.delete(order)
            session.commit()
```

### Read into DataFrame (ORM → Dash)

```python
import pandas as pd
from sqlalchemy import select
from db_utility import get_session
from models import Order, User

def get_orders_df() -> pd.DataFrame:
    with get_session() as session:
        stmt = select(Order.id, Order.status, Order.created_at, User.name)\
            .join(User)
        result = session.execute(stmt)
        return pd.DataFrame(result.fetchall(), columns=result.keys())
```

### Schema creation (ORM-managed)

```python
# sql_startup.py
from models import Base
from db_utility import get_engine

def run_startup():
    Base.metadata.create_all(get_engine())   # creates all tables if not exist
```

For more complex migrations (ALTER TABLE, data migrations), use **Alembic**:
```bash
alembic init alembic
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## Hybrid pattern

ORM for entity management, raw SQL for heavy read queries:

```python
# Write via ORM
with get_session() as session:
    session.add(Order(user_id=1, status="open"))
    session.commit()

# Read via raw SQL for Dash table
df = pd.read_sql("SELECT ... complex aggregation ...", get_engine())
```

---

## Project file layout

```
src/
  db_utility.py      # engine + session factory (always present)
  models.py          # ORM models (only if ORM approach chosen)
  sql_startup.py     # startup schema init
  db_queries.py      # raw SQL read functions (raw SQL approach)
  # or
  db_service.py      # CRUD service functions (ORM approach)
```

---

## SPEC.md database section

When writing a SPEC.md, include under the **Database** section:

```markdown
## Database

- **Backend**: MSSQL / PostgreSQL (Cloud SQL)
- **Access pattern**: Raw SQL / ORM / Hybrid
- **ORM**: SQLAlchemy 2.x (if ORM chosen)
- **Migrations**: create_all on startup / Alembic (if ORM chosen)
- **Main entities**: (list tables/models)
- **Connection**: CONNECTION_STRING env var (MSSQL) / axach_gcp_helpers (Cloud SQL)
```
