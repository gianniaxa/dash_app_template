---
name: gcp-patterns
description: Use when working with GCP projects, GCP data, BigQuery, Cloud Storage, Cloud SQL, Secret Manager, Vertex AI, Cloud Run, Cloud Build, Artifact Registry, axach_gcp_helpers, or Docker images pushed to or pulled from GCP. Contains conventions for registry URLs, authentication, cloudbuild.yaml, Dockerfile patterns, and the axach_gcp_helpers library used in this organisation.
---

# GCP Patterns

## Artifact Registry

Registry base URL pattern:
```
europe-west6-docker.pkg.dev/axach-inetbuildingzonereg-ibz/
```

Image naming:
```
europe-west6-docker.pkg.dev/axach-inetbuildingzonereg-ibz/{project}-repo/{image-name}:{version}
```

Docker Hub images are **not** pulled directly — use the organisation's remote cache repository:
```
europe-west6-docker.pkg.dev/axach-inetbuildingzonereg-ibz/docker-hub-remote-repo/
```

Example Dockerfile base image:
```dockerfile
ARG REGISTRY_BASE=europe-west6-docker.pkg.dev/axach-inetbuildingzonereg-ibz/docker-hub-remote-repo/
FROM ${REGISTRY_BASE}python:3.12-slim
```

## Authentication (Cloud Build)

Cloud Build cannot use `docker login` interactively. Instead:

1. Generate an OAuth2 token via the `gcloud` builder and write it to `/workspace/token.txt`
2. Pass it as a `--build-arg TOKEN=...` to `docker build`
3. Use it inside the Dockerfile as needed (e.g. for `uv` / pip against a private index)

```yaml
# cloudbuild.yaml
steps:
  - name: gcr.io/cloud-builders/gcloud
    entrypoint: 'bash'
    args: ['-c', 'gcloud auth print-access-token > /workspace/token.txt']
  - name: 'docker'
    entrypoint: 'sh'
    env:
      - "DOCKER_API_VERSION=1.41"
    args:
      - '-c'
      - >-
        docker build
        --build-arg="TOKEN=$(cat /workspace/token.txt)"
        -f Dockerfile
        -t europe-west6-docker.pkg.dev/axach-inetbuildingzonereg-ibz/$_TARGETPROJECT-repo/$_IMAGEPATH:$_VERSION
        -t europe-west6-docker.pkg.dev/axach-inetbuildingzonereg-ibz/$_TARGETPROJECT-repo/$_IMAGEPATH:$TAG_NAME
        .
substitutions:
  _TARGETPROJECT: youmustsetthetarget
  _IMAGEPATH: your-image-name
  _VERSION: 0.1.0
images:
  - 'europe-west6-docker.pkg.dev/axach-inetbuildingzonereg-ibz/$_TARGETPROJECT-repo/$_IMAGEPATH:$_VERSION'
  - 'europe-west6-docker.pkg.dev/axach-inetbuildingzonereg-ibz/$_TARGETPROJECT-repo/$_IMAGEPATH:$TAG_NAME'
options:
  logging: CLOUD_LOGGING_ONLY
serviceAccount: "projects/axach-inetbuildingzone-ibz/serviceAccounts/si-$_TARGETPROJECT@axach-inetbuildingzone-ibz.iam.gserviceaccount.com"
```

## Dockerfile — private Python index via uv

The TOKEN build arg is used to authenticate `uv sync` against a private Artifactory/PyPI index:

```dockerfile
ARG TOKEN

RUN UV_INDEX_USERNAME=oauth2accesstoken \
    UV_INDEX_PASSWORD=${TOKEN} \
    uv sync --no-cache --no-install-project
```

Full minimal example:
```dockerfile
ARG REGISTRY_BASE=europe-west6-docker.pkg.dev/axach-inetbuildingzonereg-ibz/docker-hub-remote-repo/
FROM ${REGISTRY_BASE}python:3.12-slim

ARG TOKEN

ENV PYTHONUNBUFFERED=True
ENV APP_HOME=/app
WORKDIR $APP_HOME

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY pyproject.toml $APP_HOME/pyproject.toml
COPY main.py $APP_HOME/main.py
COPY src/ $APP_HOME/src/

RUN UV_INDEX_USERNAME=oauth2accesstoken \
    UV_INDEX_PASSWORD=${TOKEN} \
    uv sync --no-cache --no-install-project

ENV PYTHONPATH="${PYTHONPATH}:/app/src"
ENV PATH="/app/.venv/bin:${PATH}"

ENTRYPOINT ["python", "main.py"]
```

## Service account naming convention

```
si-{project}@axach-inetbuildingzone-ibz.iam.gserviceaccount.com
```

The Cloud Build service account project is always `axach-inetbuildingzone-ibz` (the build project), even when the target image goes into a different project repo.

## docker-compose.yml (local dev)

For local builds that mirror the Cloud Build flow, pass the token via an env var:

```yaml
services:
  my-service:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        TOKEN: ${TOKEN}
    image: my-service:latest
```

Generate the token locally with:
```bash
TOKEN=$(gcloud auth print-access-token)
```

---

## axach_gcp_helpers

Internal AXA CH library that wraps common GCP interactions. Local clone at `~/projects/axach_gcp_helpers`.

### Installation

In `pyproject.toml` / `requirements.txt` (private PyPI index, authenticated via TOKEN):
```
--extra-index-url https://oauth2accesstoken:${TOKEN}@europe-west6-python.pkg.dev/axach-inetbuildingzonereg-ibz/axach-claimsanalytics-pyrepo/simple
axach_gcp_helpers~=0.6
```

Local install from git:
```bash
pip install git+https://github.axa.com/axach-ccda/axach_gcp_helpers.git
```

With Kafka extras:
```bash
pip install git+https://github.axa.com/axach-ccda/axach_gcp_helpers.git#egg=axach_gcp_helpers[kafka]
```

### Project naming convention

All GCP project names follow the pattern:
```
axach-{team}-{workload}-{stage}
```
- Must start with `axach-`
- Must end with one of: `dev`, `ppd`, `prd`, `exp`

Example: `axach-as-regress-uvg-dev`

### Basic usage

```python
from axach_gcp_helpers import GCP

gcp = GCP("axach-as-regress-uvg-dev")

gcp.get_gcp_project()   # -> "axach-as-regress-uvg-dev"
gcp.get_stage()         # -> "dev"
gcp.get_environ()       # -> "local" | "gcp" | "openpaas"
```

### Secret Manager

```python
# Read secret as string
secret_value = gcp.read_from_secretmanager("my-secret-name")

# Download secret as temp file (returns path)
path = gcp.download_from_secretmanager("my-secret-name")

# Split PEM certificate into key/cert/ca temp files
cert_dict = gcp.download_split_certificates("kafka-cert-secret")
# cert_dict = {"key": "/tmp/...", "cert": "/tmp/...", "ca": "/tmp/..."}
```

Project configs are stored in Secret Manager under the name `gcp_project_configs` as a YAML file.
Access with `gcp.get_gcp_configs()`. Generate a blank template with:
```python
from axach_gcp_helpers import generate_blank_gcp_configs
generate_blank_gcp_configs()
```

### Cloud Storage (GCS)

Bucket names are auto-resolved: short names like `"working"` are expanded to
`{project_base}-working-{stage}` automatically.

```python
# Get a bucket object
bucket = gcp.get_bucket("working")

# Get a blob
blob = gcp.get_blob("working", "path/to/file.txt")
blob.download_as_string()

# Download blob to local file
gcp.get_file_from_bucket("working", "path/to/file.txt", "/local/path/file.txt")
```

### BigQuery

```python
bq = gcp.get_bq_client()                        # google.cloud.bigquery.Client
rows = gcp.execute_bq_query("SELECT ...")        # returns RowIterator, raises on errors
```

### Cloud SQL (PostgreSQL)

Requires `gcp_project_configs` secret with `cloud_sql_instance` and `cloud_sql_tunnel` sections.
Uses SSL certificates from Secret Manager. Locally, connects via gateway proxy.

```python
engine = gcp.get_cloudsql_engine()   # SQLAlchemy engine (postgresql+psycopg2)
```

### Logging

```python
logger = gcp.get_logger()
logger.info("message")
logger.debug("debug message")
logger.setLevel("INFO")   # suppress debug
```
On GCP: routes to Cloud Logging. Locally: logs to stdout at DEBUG level.

### PubSub

```python
gcp.send_pubsub(
    target_project="axach-streamingestion-dev",
    target_pubsub="ps-my-topic",
    d_data={"key": "value"}
)
```

### GCP Workflows

```python
result = gcp.execute_workflow(
    workflow_name="my-workflow",
    parameters={"param": "value"},
    location="europe-west6",        # default
    max_backoff_delay=600            # seconds, default
)
```
Polls until finished. Raises `TimeoutError` if `max_backoff_delay` is exceeded, `RuntimeError` if workflow fails.

### Cloud Run

```python
url = gcp.get_cloudrun_endpoint("my-cloudrun-service")
```

### Vertex AI

```python
from axach_gcp_helpers.vertex_ai import VertexAIEndpointClient

client = VertexAIEndpointClient(
    project="axach-as-regress-uvg-dev",
    endpoint_id="1234567890",
    location="europe-west6"   # default
)
predictions = client.get_predictions([{"feature1": 1.0, "feature2": 2.0}])
```

### Kafka (optional extra)

```python
from axach_gcp_helpers.kafka_utils import KafkaConsumer

cert_dict = gcp.download_split_certificates("kafka-cert-secret")
consumer = KafkaConsumer(cert_dict=cert_dict, group_id="my-group", stage="dev", logger=logger)
consumer.subscribe(["my-topic"])
msg = consumer.get_messages_and_info(10, 1)
```

### Utility functions

```python
from axach_gcp_helpers.utils import get_access_token, split_project_name, keep_configuration_for_stage

# Get OAuth2 access token programmatically
token = get_access_token()

# Split project name into base and stage
base, stage = split_project_name("axach-as-regress-uvg-dev")
# -> ("axach-as-regress-uvg", "dev")

# Filter a nested config dict to a single stage
config = {"threshold": {"dev": 0.5, "ppd": 0.7, "prd": 0.9}}
keep_configuration_for_stage(config, "ppd")
# -> {"threshold": 0.7}
```

### Stage / gateway mapping

| Stage | Gateway |
|-------|---------|
| dev   | `gatewaycon-gcp.dev.axa-ch.intraxa` |
| ppd   | `gatewaycon-gcp.acc.axa-ch.intraxa` |
| prd   | `gatewaycon-gcp.axa-ch.intraxa` |
| exp   | `gatewayconexp-gcp.axa-ch.intraxa` |

Locally, `http_proxy` and `https_proxy` are automatically set to the `exp` gateway.
