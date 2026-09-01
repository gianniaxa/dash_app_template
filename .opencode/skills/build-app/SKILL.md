---
name: build-app
description: Use when the user wants to build or implement the app, says "build starten", "app bauen", or asks to implement features from SPEC.md. Reads SPEC.md, determines the tech stack, and implements the app by creating pages, components, data files, and wiring everything together.
---

# Build App Skill

You are a senior software engineer. Your job is to implement an application based on the specification in `SPEC.md` and the patterns established in this project.

## Before you start

1. Read `SPEC.md` fully.
2. Read `AGENTS.md` fully — it contains project conventions you must follow.
3. Read the existing code in `src/` to understand the project structure.
4. Check the tech stack specified in `SPEC.md` — Dash, Flask, FastAPI, or other. Load the relevant skill(s) for that stack if available.
5. Check the database backend and access pattern specified in `SPEC.md` — load the `db-access` skill, and `mssql-openshift` or `gcp-patterns` as appropriate.
6. If `SPEC.md` is empty or has unanswered sections marked `...` or `<!-- TODO -->`, stop and tell the user to complete the spec first (use the `spec-interview` skill).

## Build process

Work through the spec section by section in this order:

### 1. Plan first

Before writing any code, output a concise build plan:
- List every file you will create or modify
- Note any new packages needed
- Flag anything in the spec that is ambiguous or conflicting

Get confirmation if the plan involves major structural changes.

### 2. Data layer

- If CSV-based: create data files in `src/data/`
- If database: set up engine/session in `src/db_utility.py` following the `db-access` skill
  - Raw SQL: create `src/db_queries.py` with named-parameter queries
  - ORM: create `src/models.py` with SQLAlchemy model classes
  - Startup migrations: `sql_startup.py` using `create_all` or raw DDL
- Document required env vars in the secrets example file
- Never hardcode connection strings or credentials

### 3. Database security

- **Never** construct SQL with f-strings or string concatenation — always use named parameters (`:param` with `sqlalchemy.text`, or ORM query methods)
- Connection strings go in env vars only — never in code or config files committed to git
- For MSSQL: follow the `mssql-openshift` skill (`OPENSSL_CONF`, NTLM engine reset pattern)
- For Cloud SQL (GCP): use `axach_gcp_helpers.GCP.get_cloudsql_engine()` — credentials stored in Secret Manager, not env vars
- Use `engine.begin()` (not `engine.connect()`) for writes — guarantees rollback on error
- Set `pool_pre_ping=True` to detect stale connections before use
- ORM sessions: always use context managers (`with get_session() as session`) — never leave sessions open

### 4. Authentication & security

Implement based on what is specified in `SPEC.md`:

**No auth**: ensure no sensitive data is exposed on any route without at least noting the risk.

**Username/password**:
- Hash passwords with `bcrypt` or `argon2` — never store plaintext or MD5/SHA1
- Use a session secret from env var (`FLASK_SECRET_KEY` / `SECRET_KEY`) — never hardcoded
- Implement login_required decorator or equivalent to protect all non-public routes
- Set session cookie flags: `HttpOnly=True`, `Secure=True` (in production), `SameSite=Lax`

**SSO / SAML**:
- AXA internal SSO uses SAML via `login.axa-ch.intraxa`
- Requires AXA CA certificate — see `openshift-patterns` skill for cert mounting
- Set `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` env vars to point to the mounted cert

**Role-based access**:
- Define roles as constants or an enum — never as raw strings scattered through the code
- Check roles in a single decorator/middleware, not inline in every route handler
- Store the user's role in the session after login — re-validate on sensitive operations

**General security rules**:
- Validate and sanitise all user inputs before using them in queries, file paths, or shell commands
- Never expose stack traces or internal error details to the end user — log them server-side
- Secrets (API keys, passwords, tokens) only via env vars or Secret Manager — never in code or SPEC.md

### 5. Components / UI

- For each UI pattern needed (form, table, chart, modal), check if a component already exists
- Reuse existing components where possible
- Create new component files following project conventions
- No callbacks inside component files (Dash) — callbacks at module level only

### 6. Pages / Routes

- One file per route/page
- Follow the routing convention of the chosen framework (e.g. `dash.register_page` for Dash)
- Load data via shared utility functions — never inline DB calls in route handlers
- Apply auth checks at the route level — not inside the data functions

### 7. Navigation

- Register every new page/route in the app's navigation
- Keep nav items in logical order
- Hide nav items the current user's role cannot access

### 8. Dependencies

- Add any new packages to `pyproject.toml` (or `requirements.txt` if that's the project convention)
- Dev-only packages go in the appropriate dev group

### 9. Tests

- Write at least one unit test per new utility function
- Write integration tests for DB-backed logic
- Test auth: verify protected routes return 401/redirect when unauthenticated
- Test role checks: verify lower-privilege roles cannot access higher-privilege routes
- Follow the patterns already present in `tests/`

### 10. README

- Update `README.md` to reflect all changes: pages, components, packages, env vars, structure

## What not to do

- Do not delete or overwrite existing files unless the spec explicitly replaces them
- Do not hardcode credentials, secrets, or connection strings anywhere in code
- Do not invent features not in the spec — implement exactly what is specified
- Do not construct SQL or DB URLs with f-strings
- Do not store passwords in plaintext or with weak hashing
- Do not expose internal error details to the browser

## When done

Summarize what was built:
- List all new files created
- List all modified files
- List all env vars the operator must set before running (with descriptions)
- Note any open items or follow-up steps (e.g. "DB credentials still need to be filled in the secrets file", "AXA CA cert must be mounted as a secret in OpenShift")
