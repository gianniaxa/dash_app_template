---
name: openshift-patterns
description: Use when working on OpenShift (OpenPaaS) projects, Helm charts for OpenShift, ImageStreams, PersistentVolumeClaims, Universal Agent, CronJobs on Kubernetes/OpenShift, Dockerfiles for RHEL/OpenShift, or CI/CD pipelines that build and deploy to OpenShift via Artifactory.
---

# OpenShift Patterns (AXA CH OpenPaaS)

## Platform

- **Platform**: Red Hat OpenShift on Azure (OpenPaaS)
- **API server pattern**: `https://api.{cluster}.switzerlandnorth.azure.openpaas.axa-cloud.com:6443`
- **Internal image registry**: `image-registry.openshift-image-registry.svc:5000`
- **Namespace pattern**: `{app-name}-{app-id}-{stage}-axa-ch`
  - Example: `arbeiten-im-ausland-app-4255-dev-axa-ch`
- **Stages**: `dev`, `preprod`, `prod`

---

## Dockerfile

Base image comes from the **internal Red Hat registry** (not Docker Hub):

```dockerfile
FROM registry.access.redhat.com/hi/python:3.12-builder
```

### OpenShift UID/GID compatibility

OpenShift runs containers with an arbitrary UID in group 0. Always fix permissions:

```dockerfile
RUN chown -R 1001:0 /app && chmod -R g+w /app
USER 1001
```

Build as `USER root` for installation steps, then drop back to `USER 1001`.

### Full minimal Python Dockerfile

```dockerfile
FROM registry.access.redhat.com/hi/python:3.12-builder

USER root
WORKDIR /app

# Upgrade pip first (clears RHACS security gates)
RUN python3 -m pip install --no-cache-dir --upgrade "pip>=26.1"

COPY ./src-app /app
COPY ./src /app/src

# OpenSSL legacy provider (needed for MSSQL NTLM auth — see mssql-openshift skill)
COPY openssl-legacy.cnf /openssl-legacy.cnf
ENV OPENSSL_CONF=/openssl-legacy.cnf
ENV PYTHONPATH=/app/src:/app

RUN python3 -m pip install --root-user-action=ignore --no-cache-dir --only-binary :all: -r requirements.txt

# OpenShift UID compatibility
RUN chown -R 1001:0 /app && chmod -R g+w /app

EXPOSE 8080
USER 1001

CMD exec gunicorn --bind :8080 --workers 3 --threads 1 --log-level $LOG_LEVEL --timeout 0 app:application
```

**Notes:**
- `--only-binary :all:` avoids compiling C extensions at runtime — required because the build image may not have full dev headers
- AXA CA cert for SAML is **not** baked in; it is mounted as a secret at runtime (see below)

---

## Package registry (Artifactory)

Images are **not** pushed to GCP Artifact Registry. They go to AXA's internal Artifactory:

```
virtual-axa-ch-{team}-docker.docker.artifactory.europe.axa-cloud.com/{service-name}:{tag}
```

The pull registry URL and push registry URL are separate (`PULL_DOCKER_REPO_URL` vs `DOCKER_REPO_URL`).

Authentication is via `ARTIFACTORY_USERNAME` / `ARTIFACTORY_PASSWORD` GitHub secrets.

---

## CI/CD (GitHub Actions)

Reusable workflows from `axa-ch-actions`:

1. **Build & push** to Artifactory (`workflow-build-container-image`)
2. **Import into OpenShift ImageStream** (`action-import-artifactory-image`) — always imports into the **dev** namespace first; preprod and prod pull from the dev ImageStream via RBAC
3. **Patch values files** with the new image SHA (`patch-infra-repo-as-app`) — updates `helm-charts/values-{stage}.yaml` in-repo; ArgoCD picks up the change

Image tags in `values-{stage}.yaml` are **SHA digests** (`sha256:...`), not mutable tags.

```yaml
# .github/workflows/release.yaml skeleton
jobs:
  buildAndPushAppImage:
    uses: axa-ch-actions/workflow-build-container-image/.github/workflows/build-container-image.yaml@v1
    secrets:
      artifactoryCredentials: |
        ${{ vars.DOCKER_REPO_URL }};${{ vars.ARTIFACTORY_USERNAME }};${{ secrets.ARTIFACTORY_PASSWORD }}
        ${{ vars.PULL_DOCKER_REPO_URL }};${{ vars.ARTIFACTORY_USERNAME }};${{ secrets.ARTIFACTORY_PASSWORD }}
    with:
      imageName: "${{ vars.DOCKER_REPO_URL }}/${{ vars.SERVICE_NAME }}-app:${{ github.sha }}"
      dockerfileLocation: Dockerfile-app
      pushImage: true

  importAppImage:
    needs: buildAndPushAppImage
    steps:
      - uses: axa-ch-actions/action-import-artifactory-image@v1
        with:
          namespace: ${{ vars.DEV_NAMESPACE_NAME }}
          imageStreamName: ${{ vars.SERVICE_NAME }}-app
          tag: ${{ github.sha }}
          artifactoryRepository: ${{ vars.DOCKER_REPO_NAME }}
          importImage: ${{ vars.SERVICE_NAME }}-app
          importHash: ${{ needs.buildAndPushAppImage.outputs.imageHash }}
          apiserver: https://api.${{ vars.CLUSTER }}.switzerlandnorth.azure.openpaas.axa-cloud.com:6443
          ocToken: ${{ secrets.PIPELINE_SA_TOKEN }}

  deployDev:
    needs: [importAppImage, buildAndPushAppImage]
    steps:
      - uses: axa-ch-actions/patch-infra-repo-as-app@v4
        with:
          imageTag: ${{ needs.buildAndPushAppImage.outputs.imageHash }}
          valuesFile: "helm-charts/values-dev.yaml"
          imageTagPath: .deployment.app.image.tag
```

Deploy order: `dev` → `preprod` → `prod` (each stage `needs` the previous).

---

## Helm chart structure

```
helm-charts/
  Chart.yaml
  values.yaml          # defaults + documentation
  values-dev.yaml      # stage-specific overrides + sealed image tags
  values-preprod.yaml
  values-prod.yaml
  templates/
    d-application.yaml           # Deployment
    svc-application.yaml         # Service
    rt-application.yaml          # Route
    is-application.yaml          # ImageStream (created in dev namespace only)
    is-cli.yaml                  # ImageStream for CLI/CronJob image
    is-universal-agent.yaml      # ImageStream for Universal Agent
    image-stream-access-rbac.yaml # RoleBinding so preprod/prod can pull from dev
    config-application.yaml      # ConfigMap (non-secret env vars)
    config-universal-agent.yaml  # ConfigMap for Universal Agent
    pvc-application.yaml         # PersistentVolumeClaim
    cronjob-application.yaml     # CronJobs (looped from values)
    sa-application.yaml          # ServiceAccount
    pdb-application.yaml         # PodDisruptionBudget
    sealed-secret-*.yaml         # Sealed secrets (checked into git)
```

### ImageStream pattern

ImageStreams are **only created in the dev namespace**. Preprod and prod pull from dev via a `RoleBinding`:

```yaml
# image-stream-access-rbac.yaml
{{- if eq .Values.stage "dev" }}
kind: RoleBinding
subjects:
  - kind: ServiceAccount
    name: {{ .Values.applicationName }}
    namespace: {{ .Values.namespaces.preprod }}
  - kind: ServiceAccount
    name: {{ .Values.applicationName }}
    namespace: {{ .Values.namespaces.prod }}
roleRef:
  kind: ClusterRole
  name: 'system:image-puller'
{{- end }}
```

Image reference in Deployment always points to dev namespace:
```yaml
image: '{{ .Values.openshift.image.url }}/{{ .Values.namespaces.dev }}/{{ .Values.applicationName }}-app@{{ .Values.deployment.app.image.tag }}'
```

---

## PersistentVolumeClaim (PVC)

For file uploads, exports, or shared data between the app and the Universal Agent:

```yaml
# values.yaml
persistence:
  enabled: true
  size: 1Gi
  mountPath: /data
  storageClass: "managed-premium-zrs"  # Azure ZRS, recommended for multi-AZ
  volumeMode: Filesystem
```

```yaml
# pvc-application.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ .Values.applicationName }}-storage
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {{ .Values.persistence.size }}
  storageClassName: {{ .Values.persistence.storageClass }}
  volumeMode: {{ .Values.persistence.volumeMode | default "Filesystem" }}
```

Mount in Deployment (both app container and Universal Agent container share the same PVC):
```yaml
volumeMounts:
  - name: data-storage
    mountPath: {{ .Values.persistence.mountPath }}
volumes:
  - name: data-storage
    persistentVolumeClaim:
      claimName: {{ .Values.applicationName }}-storage
```

---

## Universal Agent (Stonebranch)

Used for **scheduled file transfers** and integration with the Stonebranch workload automation platform.

The Universal Agent runs as a **sidecar container** in the same pod as the app, sharing the PVC.

```yaml
# values.yaml
universalAgent:
  enabled: true
  version: "8.0.2.0"
  imageStream:
    name: universal-agent
  source:
    repository: "virtual-axa-ch-axa-ch-common-libs-docker.docker.artifactory.europe.axa-cloud.com/stonebranch/universal-agent"
  omsServers: "7878@sbomsdev1.axa-ch.intraxa,7878@sbomsdev2.axa-ch.intraxa"
  clusterStage: DEV-DEV   # stage-specific, e.g. PROD-PROD in prod

# values-dev.yaml
universalAgent:
  clusterStage: DEV-DEV
  omsServers: "7878@sbomsdev1.axa-ch.intraxa,7878@sbomsdev2.axa-ch.intraxa"
```

ConfigMap for the Universal Agent:
```yaml
data:
  UAGAGENTCLUSTERS: CL_POD_{{ .Values.applicationName }}_{{ .Values.universalAgent.clusterStage }}_{{ .Values.application.appId }}
  UAGENABLESSL: 'yes'
  UAGOMSSERVERS: {{ .Values.universalAgent.omsServers | quote }}
  UAGTRANSIENT: 'yes'
  USER_NAME: 'ubroker'
```

The Universal Agent ImageStream is imported from Artifactory into the dev namespace once, then reused across stages.

---

## CronJobs

CronJobs are defined in `values.yaml` as a map and rendered in a single template via `range`.

Two image patterns:
1. **CLI image** — a lightweight image built for scheduled tasks, references `is-cli` ImageStream
2. **Custom image** (e.g. email cronjob) — separate Dockerfile, separate ImageStream, referenced via `useEmailCronjobImage: true`

```yaml
# values.yaml
cronjobs:
  importData:
    enabled: true
    schedule:
      dev: "0 7 29 2 *"       # Feb 29 = effectively disabled in dev
      preprod: "0 7 29 2 *"
      prod: "15 7 * * 1-5"    # Business days at 07:15
    concurrencyPolicy: Forbid
    successfulJobsHistoryLimit: 2
    failedJobsHistoryLimit: 2
    image: image-registry.openshift-image-registry.svc:5000/{dev-namespace}/cli:latest
    command:
      - /bin/sh
      - -c
      - |
        curl -f -X POST http://{service}:8080/trigger/import \
          -H "X-Trigger-Token: ${TRIGGER_SECRET}" \
          --max-time 600 || exit 1

  sendMailJob:
    enabled: true
    useEmailCronjobImage: true   # uses the email-cronjob ImageStream
    schedule:
      prod: "0 8 * * 1-5"
    imageTag: ""  # set by CI/CD
    command:
      - python3
      - email_reminder.py
      - reminders
```

**Disabling CronJobs at runtime** without redeploying: use an optional secret `CRONJOBS_ENABLED=false`.

**Stage-specific schedules**: the template reads `index $job.schedule $.Values.stage`. Use `"0 7 29 2 *"` (Feb 29) as a safe "disabled" schedule for non-prod stages.

CronJob template loops:
```yaml
{{- range $name, $job := .Values.cronjobs }}
{{- if $job.enabled }}
---
apiVersion: batch/v1
kind: CronJob
...
  schedule: {{ index $job.schedule $.Values.stage | quote }}
{{- end }}
{{- end }}
```

---

## Secrets management

Secrets are stored as **Sealed Secrets** (encrypted, safe to commit to git).

Sensitive values that change per-environment (DB connection strings, API keys) live in `values-{stage}.yaml` as encrypted `AgA...` blobs.

Secrets that must be created **manually** (e.g. CA certificates, pipeline tokens) are created once via `oc create secret` and are not tracked by Helm.

```bash
# Manual secret creation (run once per namespace)
oc create secret generic my-secret \
  --from-literal=MY_KEY=myvalue \
  -n arbeiten-im-ausland-app-4255-dev-axa-ch
```

---

## AXA CA certificate

The AXA internal CA (`O = GIE AXA, CN = AXA-Issuing-CA-PR1`) is required for SAML and internal HTTPS.

- **Local dev**: volume-mount the `.pem` file via `docker-compose.yml`
- **OpenShift**: create secret manually with `oc`, mount as volume

```bash
oc create secret generic aia-axa-ca-cert \
  --from-file=ca.pem=secrets/ca_certs_axa_me.pem \
  -n arbeiten-im-ausland-app-4255-dev-axa-ch
```

In Deployment, mount it and set env vars for Python's `requests` library:
```yaml
env:
  - name: SSL_CERT_FILE
    value: /etc/pki/ca-trust/source/anchors/axa-ca.pem
  - name: REQUESTS_CA_BUNDLE
    value: /etc/pki/ca-trust/source/anchors/axa-ca.pem
volumeMounts:
  - name: axa-ca-cert
    mountPath: /etc/pki/ca-trust/source/anchors/
    readOnly: true
volumes:
  - name: axa-ca-cert
    secret:
      secretName: aia-axa-ca-cert
      items:
        - key: ca.pem
          path: axa-ca.pem
```

The cert PEM is stored at:
```
G:\PUBLIC\SWPD_Source\google-cloud-sdk\certs\ca_certs_axa_me.pem
```

---

## Deployment strategy

Use `Recreate` (not `RollingUpdate`) when a PVC is involved.

**Multi-attach is disabled on this platform.** PVCs use `ReadWriteOnce` access mode, which means
only **one pod can mount the volume at a time**. With `RollingUpdate`, the new pod starts before
the old one is terminated — both try to mount the PVC simultaneously, causing the new pod to get
stuck in `ContainerCreating` with a `Multi-Attach error`. Always use `Recreate` to avoid this:

```yaml
strategy:
  type: Recreate
```

This also applies to CronJobs that mount the PVC — set `concurrencyPolicy: Forbid` to prevent two
job instances from running at the same time and competing for the volume.

---

## Useful `oc` commands

```bash
# List pods
oc get pods -n arbeiten-im-ausland-app-4255-dev-axa-ch

# Exec into pod
oc exec -it <pod-name> -n <namespace> -- /bin/bash

# Check logs
oc logs <pod-name> -n <namespace>

# Trigger a CronJob manually
oc create job --from=cronjob/<cronjob-name> manual-run -n <namespace>

# Check ImageStreams
oc get is -n <namespace>
```
