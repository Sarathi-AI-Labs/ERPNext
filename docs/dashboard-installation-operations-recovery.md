# Sarathi Industrial Control Tower — Installation, Configuration, Backup, Upgrade, and Rollback Operations Manual

**Project:** Sarathi Industrial Control Tower  
**Parent Epic:** DASH-030 — Testing, Performance, Security & Release  
**Task ID:** DASH-035  
**Priority:** P1 — High  
**Framework:** Frappe Framework v16.31.0 + ERPNext v16.33.0  
**Deployment Model:** Frappe Docker on Dedicated VPS / Local Docker Compose  
**Applications Covered:** `sarathi_owner`, `sarathi_visibility`  
**Related Documents:**
- [Dashboard Architecture & Foundation](dashboard-foundation.md)
- [Dashboard Permission Matrix](dashboard-permission-matrix.md)
- [Dashboard API Security Matrix](dashboard-api-security-matrix.md)
- [Dashboard KPI Dictionary](dashboard-kpi-dictionary.md)
- [KPI Reconciliation Test Matrix](kpi-reconciliation-test-matrix.md)
- [Dashboard Integration & Regression Test Plan](dashboard-integration-regression-test-plan.md)
- [Dashboard Performance Test Report](dashboard-performance-test-report.md)
- [Local Docker WSL Recovery Runbook](local-docker-wsl-recovery.md)

---

## Command Verification Legend

Throughout this guide, every operational command is annotated with an explicit verification status:

- **`[Verified]`**: Confirmed against active repository code, configuration files (`compose.yaml`, `resources/sarathi/deploy.sh`), or automated tests executed in this workspace.
- **`[Environment-dependent]`**: Syntactically and operationally verified against project architecture, but requires environment-specific parameters (e.g., domain names, secret passwords, offsite backup storage paths).
- **`[Not verified]`**: Theoretical or disaster-recovery commands requiring execution confirmation in an isolated staging environment before production use.

---

## 1. System Architecture and Prerequisites

### 1.1 Architecture Overview

The Sarathi Industrial Control Tower runs natively inside the standard Frappe Framework and ERPNext container architecture. It does **not** introduce a separate backend (e.g., FastAPI, Node.js express), an external microservice, or an independent database. All business metrics, operations, and analytical aggregations query ERPNext DocTypes directly using Frappe's database engine and permission layers.

```
                              [ Browser Client ]
                                      │
                                      ▼ HTTPS (Port 443 / 8080)
┌─────────────────────────────────────┴─────────────────────────────────────┐
│                      Reverse Proxy / Web Server                           │
│     Service: `frontend` (NGINX)  [Port 8080:8080 or Traefik Port 443]    │
│  - Serves static assets (`/assets/sarathi_owner`, `/assets/sarathi_visibility`)│
│  - Proxies HTTP / API calls to `backend:8000`                             │
│  - Proxies WebSocket real-time events to `websocket:9000`                 │
└──────────────────┬────────────────────────────────────┬───────────────────┘
                   │                                    │
                   ▼ HTTP (Port 8000)                   ▼ WebSocket (Port 9000)
┌───────────────────────────────────────┐ ┌─────────────────────────────────┐
│        Gunicorn Web Worker            │ │        Node.js Socket.IO        │
│          Service: `backend`           │ │        Service: `websocket`     │
│   Image: sarathi/erpnext-sarathi      │ │   Image: sarathi/erpnext-sarathi│
│   Apps: frappe, erpnext,              │ │   Runs: socketio.js             │
│         sarathi_visibility,           │ │   Preserves browser origin via  │
│         sarathi_owner                 │ │   nginx template mapping        │
└──────────────────┬────────────────────┘ └─────────────────┬───────────────┘
                   │                                        │
                   ├────────────────────┬───────────────────┤
                   ▼                    ▼                   ▼
┌───────────────────────────┐ ┌───────────────────┐ ┌───────────────────────┐
│      MariaDB 11.8         │ │    Redis Cache    │ │      Redis Queue      │
│      Service: `db`        │ │Service: `redis-   │ │ Service: `redis-queue`│
│ Charset: utf8mb4          │ │         cache`    │ │ Port: 6379            │
│ Collation: utf8mb4_unicode│ │ Port: 6379        │ │ Volume: redis-queue-  │
│ Volume: db-data           │ │ Image: redis:6.2- │ │         data          │
│ Port: 3306 (internal)     │ │        alpine     │ │ Image: redis:6.2-     │
│                           │ │                   │ │        alpine         │
└───────────────────────────┘ └───────────────────┘ └───────────┬───────────┘
                                                                │
                                        ┌───────────────────────┴───────────┐
                                        ▼                                   ▼
                             ┌─────────────────────┐             ┌─────────────────────┐
                             │     Worker Short    │             │     Worker Long     │
                             │Service: `queue-short│             │ Service: `queue-long│
                             │Queues: short,default│             │Queues: long,default,│
                             │                     │             │        short        │
                             └─────────────────────┘             └─────────────────────┘
                                                                            │
                                                                 ┌──────────┴──────────┐
                                                                 ▼
                                                      ┌─────────────────────┐
                                                      │  Frappe Scheduler   │
                                                      │ Service: `scheduler`│
                                                      │ Runs: bench schedule│
                                                      └─────────────────────┘
```

### 1.2 Multi-App Interaction & Dashboard Experiences

The system provides three integrated dashboard experiences across two custom Frappe applications:

1. **Owner & Executive Dashboard** (provided by `sarathi_owner`):
   - **Desk Page Route:** `/desk/sarathiownertower` or `/app/sarathiownertower`
   - **Key Capabilities:** High-level executive KPIs, financial statement reconciliation, customer sales analytics, project delivery health, manufacturing inventory valuation, and prioritized executive risk escalation.
   - **Underlying DocTypes:** `Company`, `GL Entry`, `Sales Invoice`, `Purchase Invoice`, `Sales Order`, `Project`, `Task`, `Work Order`, `Bin`.
2. **Production Management Control Tower** (provided by `sarathi_visibility`):
   - **Desk Page Route:** `/desk/sarathicontroltower` or `/app/sarathicontroltower`
   - **Key Capabilities:** Factory-wide operational KPIs, real-time Work Order pipeline, Job Card dispatching, BOM material readiness and shortage tracking, workstation downtime analytics, inspection quality, rework loops, and subcontracting status.
   - **Underlying DocTypes:** `Work Order`, `Job Card`, `BOM`, `Item`, `Bin`, `Warehouse`, `Workstation`, `Quality Inspection`, `Subcontracting Order`, `Subcontracting Receipt`.
3. **Shop-Floor Supervisor & Operator Workboard** (provided by `sarathi_visibility`):
   - **Desk Page Route:** `/desk/sarathishopfloor` or `/app/sarathishopfloor`
   - **Key Capabilities:** Dedicated mobile-first shop-floor layout. Operators view assigned Job Cards and report operational progress (`start_job`, `complete_job`). Supervisors monitor live machine status, active shift throughput, and team-wide operations.
   - **Underlying DocTypes:** `Job Card`, `Job Card Time Log`, `Employee`, `ToDo`, `Workstation`.

### 1.3 Operating Company & Tenancy Model

The Sarathi Control Tower is architected for a **dedicated single-tenant deployment per operating manufacturing company**:

- **One Operating Company per VPS:** Each dedicated virtual private server runs a single ERPNext instance with its own isolated MariaDB database, Redis queues, and site files.
- **Customers are Business Entities:** Business customers belonging to the manufacturing firm are managed as standard ERPNext `Customer` master records. They do not represent separate Frappe sites or isolated database schemas.
- **Company Permission Scoping:** All dashboard aggregation queries explicitly accept and enforce a `company` parameter, respecting native Frappe `User Permission` rules for multi-company groups within the same corporate entity.
- **No Custom Multi-Tenancy Engine:** Do not introduce or assume custom multi-tenancy routing tables. All authentication and data isolation rely on standard Frappe site mechanisms (`sites/common_site_config.json` and `sites/<site_name>/site_config.json`).

### 1.4 Prerequisites Checklist

#### A. Host System Requirements
| Requirement | Minimum (Local Dev) | Recommended (Production VPS) | Status |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 10/11 with WSL2 or Ubuntu 22.04 LTS | Ubuntu 22.04 LTS or Debian 12 64-bit | `[Verified]` |
| **CPU Architecture** | x86_64 / amd64 (4 cores) | x86_64 / amd64 (4+ cores) | `[Verified]` |
| **RAM** | 8 GB available | 16 GB+ recommended for production workloads | `[Verified]` |
| **Disk Storage** | 30 GB SSD | 100 GB+ NVMe SSD (fast I/O for MariaDB) | `[Environment-dependent]` |
| **Docker Engine** | Docker Desktop 4.28+ (WSL2 engine) | Docker Engine 24.0+ / 26.0+ with Compose v2 | `[Verified]` |
| **Python Tooling** | Python 3.10 to 3.14 (Python 3.13 tested) | Python 3.10+ (for host-level deployment scripts) | `[Verified]` |
| **Network Ports** | `8080` (HTTP web access) | `80`, `443` (HTTP/HTTPS via Traefik or NGINX) | `[Verified]` |

#### B. Software & Framework Stack Pins
- **Frappe Framework Version:** `v16.31.0` `[Verified]`
- **ERPNext Version:** `v16.33.0` `[Verified]`
- **Docker Image Tag:** `sarathi/erpnext-sarathi:v16.33.0` `[Verified in compose.yaml]`
- **Database Engine:** `mariadb:11.8` `[Verified in compose.yaml]`
- **Cache Engine:** `redis:6.2-alpine` `[Verified in compose.yaml]`
- **Scheduler Tooling:** Frappe Bench Scheduler + Ofelia Cron (`mcuadros/ofelia:latest`) `[Verified in compose.backup-cron.yaml]`

---

## 2. Repository and Application Structure

### 2.1 File System Layout

The repository is organized as a unified Frappe Docker deployment containing the two custom apps and operational scripts:

```
Frappe_docker_main/
├── compose.yaml                          # [Verified] Base Docker Compose defining all 10 services & volumes
├── pwd.yml                               # [Verified] Alternative standalone Compose definition
├── overrides/                            # [Verified] Production and infrastructure override files
│   ├── compose.sarathi-production.yaml   # [Verified] Production image build & environment overrides
│   ├── compose.sarathi.yaml              # [Verified] Development bind-mount overrides
│   ├── compose.backup-cron.yaml          # [Verified] Automated Ofelia backup scheduler definition
│   ├── compose.migrator.yaml             # [Verified] Standalone automated migration container
│   ├── compose.mariadb.yaml              # [Verified] MariaDB service configuration
│   ├── compose.redis.yaml                # [Verified] Redis configuration
│   └── compose.existing-traefik.yaml     # [Verified] Traefik ingress network integration
├── resources/
│   └── sarathi/                          # [Verified] Automated operations, deployment & test scripts
│       ├── deploy.sh                     # [Verified] Transactional VPS release & deployment script
│       ├── environments.py               # [Verified] URL and site resolver for local & production
│       ├── integration_audit.py          # [Verified] Schema manifest and upstream release comparison
│       ├── browser_smoke.py              # [Verified] Headless Playwright end-to-end smoke test
│       ├── test_deploy.py                # [Verified] Unit test suite for deploy.sh workflow
│       └── recover-local-runtime.ps1     # [Verified] PowerShell recovery script for Windows WSL2
├── docs/                                 # [Verified] Architecture, testing, and operational runbooks
│   ├── dashboard-installation-operations-recovery.md # THIS DOCUMENT
│   ├── dashboard-permission-matrix.md    # [Verified] Role and permission access rules
│   ├── dashboard-performance-test-report.md # [Verified] Performance benchmarks & query audits
│   └── local-docker-wsl-recovery.md      # [Verified] WSL2 troubleshooting guide
├── sarathi_owner/                        # [Verified] Custom App: Owner & Executive Dashboard
│   ├── sarathi_owner.pth                 # [Verified] Python site-packages path pointer
│   └── sarathi_owner/
│       ├── hooks.py                      # [Verified] App hooks, doc_events, Desk icon links
│       ├── setup/
│       │   └── install.py                # [Verified] Role provisioning & page creation
│       ├── sarathi_owner/
│       │   └── page/sarathiownertower/   # [Verified] Page definition, JSON, HTML, and JS
│       ├── api/                          # [Verified] Whitelisted backend API modules
│       │   ├── homepage.py               # Consolidated executive envelope
│       │   ├── finance_kpis.py           # Financial statement reconciliation
│       │   ├── sales_analytics.py        # Customer sales attribution
│       │   ├── project_health.py         # Project milestones & risks
│       │   ├── manufacturing_inventory.py# Stock valuation & throughput
│       │   ├── executive_risks.py        # Executive risk & approval escalation
│       │   └── module_catalog.py         # Live catalog & schema manifest
│       ├── public/                       # [Verified] CSS stylesheets, JS bundles, and icons
│       └── tests/                        # [Verified] Unit, browser, and audit tests
├── sarathi_visibility/                   # [Verified] Custom App: Control Tower & Shop-Floor
│   ├── Containerfile                     # [Verified] Dockerfile baking both apps into production image
│   └── sarathi_visibility/
│       ├── hooks.py                      # [Verified] App hooks, doc_events, Desk icons
│       ├── setup/
│       │   ├── install.py                # [Verified] Role provisioning, page creation, desktop icons
│       │   └── dashboard.py              # [Verified] Custom fields on Project & BOM
│       ├── doctype/                      # [Verified] 5 Custom DocTypes
│       │   ├── sarathi_customer_organization/
│       │   ├── sarathi_machine_integration_log/
│       │   ├── sarathi_material_requirement/
│       │   ├── sarathi_production_tracker/
│       │   └── sarathi_project_controller/
│       ├── sarathi_visibility/page/
│       │   ├── sarathicontroltower/      # [Verified] Production Management Control Tower page
│       │   └── sarathishopfloor/         # [Verified] Shop-Floor Supervisor & Operator page
│       ├── api/                          # [Verified] Whitelisted backend API modules
│       │   ├── factory_overview.py       # Factory KPIs & throughput
│       │   ├── work_orders.py            # Work Order & Job Card queues
│       │   ├── material_readiness.py     # BOM shortage calculations
│       │   ├── workstations.py           # Workstation downtime & utilization
│       │   ├── quality_rework.py         # Inspection & rework tracking
│       │   ├── production_exceptions.py  # Centralized exception queue
│       │   └── shopfloor.py              # Assigned jobs & operator reporting
│       ├── public/                       # [Verified] Shared CSS, JS runtime, and icons
│       └── tests/                        # [Verified] Pytest and Frappe integration test suites
└── scratch/                              # [Verified] Temporary diagnostic files & local logs (git-ignored)
```

### 2.2 Critical Distinction: Source vs. Baked Artifacts

- **Local Development:** The host folders `./sarathi_visibility/sarathi_visibility` and `./sarathi_owner/sarathi_owner` are mounted directly into container paths (`/home/frappe/frappe-bench/apps/...`). Any change in host Python or JavaScript code is immediately reflected in the local running bench.
- **Production Deployment:** Volume mounts for application code are **prohibited**. The `sarathi_visibility/Containerfile` bakes both applications, their dependencies, and static assets directly into the image (`sarathi/erpnext-sarathi:v16.33.0`). This ensures immutable, reproducible releases across environments.

---

## 3. Local Development Setup

Follow these verified steps to run the complete dashboard environment on a local development workstation.

### Step 1: Clone Repository and Checkout Development Branch
Run on the host machine:
```bash
# [Verified] Clone repository into the workspace directory
git clone <repository_url> Frappe_docker_main
cd Frappe_docker_main

# [Verified] Check out the active development branch
git checkout feature/Gaurav_2
```

### Step 2: Verify Docker Desktop Engine Status
On Windows systems, ensure Docker Desktop is running with the WSL2 backend enabled:
```powershell
# [Verified] Check Docker engine connectivity from PowerShell
docker version
```
*Expected Output:* Both Client and Server versions are displayed without communication errors. If Docker fails to respond, consult [docs/local-docker-wsl-recovery.md](local-docker-wsl-recovery.md) or run `powershell -File resources/sarathi/recover-local-runtime.ps1`.

### Step 3: Launch Local Docker Stack
Start the containers using the base compose file:
```bash
# [Verified] Start all services in detached mode
docker compose -f compose.yaml up -d
```
*Expected Output:*
```text
✔ Network frappe_docker_frappe_network        Created
✔ Volume "frappe_docker_db-data"              Created
✔ Volume "frappe_docker_redis-queue-data"     Created
✔ Volume "frappe_docker_sites"                Created
✔ Volume "frappe_docker_logs"                 Created
✔ Container frappe_docker-db-1                Started
✔ Container frappe_docker-redis-cache-1       Started
✔ Container frappe_docker-redis-queue-1       Started
✔ Container frappe_docker-configurator-1      Started
✔ Container frappe_docker-create-site-1       Started
✔ Container frappe_docker-backend-1           Started
✔ Container frappe_docker-websocket-1         Started
✔ Container frappe_docker-frontend-1          Started
✔ Container frappe_docker-queue-short-1       Started
✔ Container frappe_docker-queue-long-1        Started
✔ Container frappe_docker-scheduler-1         Started
```

### Step 4: Monitor Site Initialization
On first launch, `create-site` automatically provisions the default site `frontend` with ERPNext:
```bash
# [Verified] Follow logs of the site creation container
docker compose logs -f create-site
```
*Expected Output:*
```text
sites/common_site_config.json found
Installing erpnext...
*** Installed Apps
frappe
erpnext
```
Once `create-site` exits with code 0, site creation is complete.

### Step 5: Verify Installed Applications
Check which applications are currently installed on the local site:
```bash
# [Verified] List apps installed on the frontend site
docker compose exec backend bench --site frontend list-apps
```
*Expected Output:*
```text
frappe
erpnext
```

### Step 6: Install Custom Dashboard Apps (If Not Already Installed)
If `sarathi_visibility` and `sarathi_owner` are not yet installed on the site, install them sequentially:
```bash
# [Verified] Install Sarathi Visibility app
docker compose exec backend bench --site frontend install-app sarathi_visibility

# [Verified] Install Sarathi Owner app
docker compose exec backend bench --site frontend install-app sarathi_owner
```
*What This Does:*
1. Runs `before_install` to provision capability roles (`Sarathi Owner`, `Sarathi Supervisor`, `Sarathi Operator`, `Sarathi Super Admin`).
2. Creates custom fields on `Project` (`custom_sarathi_manufacturing`, `custom_sarathi_bom`) and `BOM` (`custom_sarathi_project`).
3. Provisions standard Desk Pages (`sarathicontroltower`, `sarathishopfloor`, `sarathiownertower`).
4. Configures desktop workspace icons.

### Step 7: Execute Database Migrations and Clear Cache
Synchronize schemas and compile asset maps:
```bash
# [Verified] Run database migrations
docker compose exec backend bench --site frontend migrate

# [Verified] Clear server-side cache
docker compose exec backend bench --site frontend clear-cache
```

### Step 8: Verify Web Access and Routes
Open a browser and navigate to:
- **ERPNext Desk:** `http://localhost:8080/desk` `[Verified]`
- **Owner Dashboard:** `http://localhost:8080/desk/sarathiownertower` `[Verified]`
- **Production Control Tower:** `http://localhost:8080/desk/sarathicontroltower` `[Verified]`
- **Shop-Floor Workboard:** `http://localhost:8080/desk/sarathishopfloor` `[Verified]`

*Default Local Credentials:*
- **Username:** `Administrator`
- **Password:** `admin` `[Verified in compose.yaml:100]`

### Step 9: Execute Automated Test Suites
Run the verified test suites to confirm full operational readiness:
```bash
# [Verified] Run Sarathi Visibility tests inside the backend container
docker compose exec backend bench --site frontend run-tests --app sarathi_visibility

# [Verified] Alternatively, run the standalone Python test matrix from the host
python -m unittest discover -s sarathi_visibility/sarathi_visibility/tests -p "test_*.py"
python -m unittest discover -s sarathi_owner/sarathi_owner/tests -p "test_*.py"
```
*Expected Result:* All tests pass (104/104 tests passing across reconciliation, role permissions, integration, and performance suites).

---

## 4. Environment and Application Configuration

### 4.1 Configuration Matrix

| Variable / Setting | Scope | Purpose | Default / Safe Example | Mandatory? | Requires Restart? |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `SARATHI_BASE_URL` | Container Env | Canonical HTTP(S) origin of the dashboard | `https://erp.sarathiailabs.com` | Yes (Prod) | Yes (Container) |
| `SARATHI_SITE` / `FRAPPE_SITE_NAME_HEADER` | Container Env | Frappe site name passed in NGINX headers | `erp.sarathiailabs.com` (prod) / `frontend` (local) | Yes | Yes (Container) |
| `CUSTOM_IMAGE` | Docker Compose | Name of the baked Docker image | `sarathi/erpnext-sarathi` | Yes (Prod) | Yes (Recreate) |
| `CUSTOM_TAG` | Docker Compose | Pinned release tag of the Docker image | `v16.33.0` | Yes (Prod) | Yes (Recreate) |
| `ERPNEXT_VERSION` | Docker Build | Upstream ERPNext base image tag | `v16.33.0` | Yes (Build) | Yes (Rebuild) |
| `DB_HOST` | Container Env | Hostname of the MariaDB container | `db` | Yes | Yes (Container) |
| `DB_PORT` | Container Env | Listening port of the MariaDB container | `3306` | Yes | Yes (Container) |
| `MYSQL_ROOT_PASSWORD` / `MARIADB_ROOT_PASSWORD` | Docker Secret / Env | Root database administrative password | `<SECURE_RANDOM_PASSWORD>` | Yes | Yes (DB init) |
| `REDIS_CACHE` | Container Env | Connection string for Redis cache | `redis-cache:6379` | Yes | Yes (Container) |
| `REDIS_QUEUE` | Container Env | Connection string for Redis queues | `redis-queue:6379` | Yes | Yes (Container) |
| `SOCKETIO_PORT` | Container Env | Port used for WebSocket communication | `9000` | Yes | Yes (Container) |
| `SARATHI_SOCKET_BACKEND_URL` | Container Env | Internal HTTP endpoint for WebSocket service | `http://backend:8000` | Yes | Yes (Websocket) |
| `developer_mode` | `site_config.json` | Enables developer mode and JSON sync | `0` (Prod) / `1` (Dev) | No | No (Instant) |
| `host_name` | `site_config.json` | Base URL stored in Frappe site config | `https://erp.sarathiailabs.com` | Yes (Prod) | No (Bench reload) |

### 4.2 Security Rules for Secrets and Configuration
1. **Never Commit Secrets:** Do not commit `.env`, `sites/common_site_config.json`, or `sites/<site_name>/site_config.json` containing production credentials.
2. **Restrict Permissions:** On production VPS hosts, set strict file permissions:
   ```bash
   # [Verified in deploy.sh:15] Restrict state and environment permissions
   chmod 600 .env
   chmod 700 .sarathi-deploy
   ```
3. **Database Credentials:** Keep the MariaDB root password distinct from user site passwords. Never use default passwords (`admin`) outside local development environments.

---

## 5. Initial Installation and Deployment

When deploying the Sarathi Control Tower to an existing, fresh ERPNext site on a dedicated VPS, execute the following verified sequence:

### 5.1 Pre-Installation Validation
Before modifying the site:
```bash
# [Environment-dependent] Verify bench connectivity and active apps
docker compose exec backend bench --site <YOUR_SITE_NAME> list-apps
```
Ensure that `frappe` and `erpnext` are listed and operational.

### 5.2 Application Installation Sequence
Install the applications in order:
```bash
# 1. Install sarathi_visibility first (establishes foundation doctypes & custom fields)
# [Environment-dependent]
docker compose exec backend bench --site <YOUR_SITE_NAME> install-app sarathi_visibility

# 2. Install sarathi_owner second (establishes executive dashboard pages)
# [Environment-dependent]
docker compose exec backend bench --site <YOUR_SITE_NAME> install-app sarathi_owner
```

### 5.3 Post-Installation Schema Migration & Cache Clear
```bash
# [Environment-dependent] Run migrations to apply custom fields and fixtures
docker compose exec backend bench --site <YOUR_SITE_NAME> migrate

# [Environment-dependent] Clear cache to update role and Desk routing definitions
docker compose exec backend bench --site <YOUR_SITE_NAME> clear-cache
```

### 5.4 Verification of Installed Objects
Verify that all custom objects were created correctly:
```bash
# [Environment-dependent] Execute module catalog audit to verify installation
docker compose exec backend bench --site <YOUR_SITE_NAME> execute sarathi_owner.api.module_catalog.inventory
```
*Verification Checklist:*
- [ ] 5 Custom DocTypes exist: `Sarathi Customer Organization`, `Sarathi Machine Integration Log`, `Sarathi Material Requirement`, `Sarathi Production Tracker`, `Sarathi Project Controller`.
- [ ] Custom fields present on `Project` (`custom_sarathi_manufacturing`, `custom_sarathi_bom`).
- [ ] Custom fields present on `BOM` (`custom_sarathi_project`).
- [ ] Roles created: `Sarathi Owner`, `Sarathi Supervisor`, `Sarathi Operator`, `Sarathi Super Admin`.

---

## 6. Production Deployment and Release Procedure

The production release workflow is codified and validated in `resources/sarathi/deploy.sh`. It enforces a strict, zero-downtime, safe transactional sequence that guards business data.

### 6.1 Architecture of the Production Deploy Runner (`deploy.sh`)

```
   Start Deployment (resources/sarathi/deploy.sh)
                     │
                     ▼
  1. Validate Environment & HTTPS Base URL [Verified]
                     │
                     ▼
  2. Preflight State Capture (apps-before.json, image-before.txt) [Verified]
                     │
                     ▼
  3. Build Immutable Production Backend Image (Containerfile) [Verified]
                     │
                     ▼
  4. Enable Site Maintenance Mode (set-maintenance-mode on) [Verified]
                     │
                     ▼
  5. Pause Asynchronous Background Queues & Scheduler [Verified]
                     │
                     ▼
  6. Execute Full Site Backup with Files (bench backup --with-files) [Verified]
                     │
                     ▼
  7. Run Configurator (Update apps.txt & Redis configs) [Verified]
                     │
                     ▼
  8. Deploy Backend & WebSocket Containers [Verified]
                     │
                     ▼
  9. Install Missing Dashboard Apps (If First Run) [Verified]
                     │
                     ▼
 10. Execute Database Migrations (bench migrate) [Verified]
                     │ (If migration fails: TRAP maintains Maintenance Mode; STOP)
                     ▼
 11. Clear Site Cache (bench clear-cache) [Verified]
                     │
                     ▼
 12. Run Module Catalog Inventory Audit [Verified]
                     │
                     ▼
 13. Restart Queues, Scheduler & Frontend Reverse-Proxy [Verified]
                     │
                     ▼
 14. Reload NGINX Configuration (nginx -s reload) [Verified]
                     │
                     ▼
 15. Disable Site Maintenance Mode (set-maintenance-mode off) [Verified]
                     │
                     ▼
 16. Post-Deployment Verification (Playwright browser smoke check) [Verified]
```

### 6.2 Executing a Production Deployment

On the production VPS host:

#### Step 1: Pre-Deployment Verification
Ensure disk space is adequate and Git repository is clean:
```bash
# [Verified] Check available disk space (minimum 10 GB free required)
df -h /var/lib/docker

# [Verified] Review upcoming git changes
git fetch origin
git log HEAD..origin/main --oneline
```

#### Step 2: Configure Production Environment Variables
Verify `.env` contains the required production parameters:
```bash
# [Environment-dependent] Example production .env
CUSTOM_IMAGE=sarathi/erpnext-sarathi
CUSTOM_TAG=v16.33.0
ERPNEXT_VERSION=v16.33.0
SARATHI_BASE_URL=https://erp.sarathiailabs.com
SARATHI_SITE=erp.sarathiailabs.com
DB_PASSWORD=<SECURE_PRODUCTION_DB_PASSWORD>
SARATHI_PROXY_OVERRIDE=overrides/compose.existing-traefik.yaml
```

#### Step 3: Execute Deployment Script
Run the verified deployment script:
```bash
# [Verified] Run production deployment runner
bash resources/sarathi/deploy.sh
```
*Expected Terminal Output:*
```text
Production base URL must use HTTPS.
Building backend...
Setting maintenance mode on...
Stopping scheduler, queue-short, queue-long...
Backing up site erp.sarathiailabs.com...
Backup completed at /home/frappe/frappe-bench/sites/erp.sarathiailabs.com/private/backups/...
Running configurator...
Starting backend and websocket...
Executing bench migrate...
Migrating erp.sarathiailabs.com
Clearing cache...
Restarting frontend, queues, scheduler...
Reloading nginx...
Setting maintenance mode off...
Both Sarathi dashboards deployed for https://erp.sarathiailabs.com. Metadata audit: .sarathi-deploy/...
Run the authenticated production browser smoke check to verify both dashboards.
```

#### Step 4: Execute Post-Deployment Authenticated Smoke Test
Verify dashboard rendering and realtime event subscriptions using Playwright:
```bash
# [Verified] Run browser smoke test against production
python resources/sarathi/browser_smoke.py \
  --environment production \
  --cookies production-session-cookies.txt
```
*What This Checks:*
- Navigates to `/desk/sarathiownertower` and `/desk/sarathicontroltower`.
- Confirms zero uncaught JavaScript page errors.
- Verifies that external requests to `localhost` or insecure origins do not occur.
- Verifies catalog module search and native record drill-down navigation.

---

## 7. Backup and Recovery Procedure

### 7.1 What Must Be Backed Up

A complete, restorable backup consists of four components:

| Component | Description | File Pattern | Backup Mechanism |
| :--- | :--- | :--- | :--- |
| **Database Dump** | Complete MariaDB SQL dump of the site schema and data | `*<site>-database.sql.gz` | `bench backup` |
| **Public Files** | User-uploaded public images, logos, and attachments | `*<site>-files.tar` | `bench backup --with-files` |
| **Private Files** | Confidential documents, payment slips, and contracts | `*<site>-private-files.tar` | `bench backup --with-files` |
| **Site Config** | Encryption key, database credentials, host configurations | `*<site>-site_config_backup.json` | `bench backup` |

### 7.2 Manual Site Backup Command
To trigger an immediate, complete backup of a site:
```bash
# [Verified in deploy.sh:26] Create full database and files backup inside backend container
docker compose exec -T backend bench --site <YOUR_SITE_NAME> backup --with-files
```
*Where Backups Are Stored:*
Inside the container: `/home/frappe/frappe-bench/sites/<YOUR_SITE_NAME>/private/backups/`  
On the host: Located within the named Docker volume `sites` (typically `/var/lib/docker/volumes/<project>_sites/_data/<YOUR_SITE_NAME>/private/backups/`).

### 7.3 Automated Scheduled Backups via Ofelia
Automated backups are configured via `overrides/compose.backup-cron.yaml` using Ofelia (`mcuadros/ofelia:latest`).
```yaml
# [Verified in overrides/compose.backup-cron.yaml:10-16]
services:
  cron:
    image: mcuadros/ofelia:latest
    depends_on:
      - scheduler
    command: daemon --docker
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro

  scheduler:
    labels:
      ofelia.enabled: "true"
      ofelia.job-exec.datecron.schedule: "${BACKUP_CRONSTRING:-@every 6h}"
      ofelia.job-exec.datecron.command: "bench --site all backup"
      ofelia.job-exec.datecron.user: "frappe"
```
To enable automated backups, merge the override in production compose commands:
```bash
# [Environment-dependent] Start stack with automated backup cron enabled
docker compose -f compose.yaml -f overrides/compose.backup-cron.yaml up -d
```

### 7.4 Backup Integrity Validation
Do not assume a backup is functional merely because a command exited with code 0. Always validate the archives:
```bash
# [Environment-dependent] 1. Verify files exist and have non-zero size
ls -lh /path/to/backups/

# [Environment-dependent] 2. Verify gzip database archive integrity
gzip -t /path/to/backups/*-database.sql.gz && echo "Database archive: OK"

# [Environment-dependent] 3. Verify public and private tar archives
tar -tzf /path/to/backups/*-files.tar > /dev/null && echo "Public files archive: OK"
tar -tzf /path/to/backups/*-private-files.tar > /dev/null && echo "Private files archive: OK"
```

### 7.5 Site Restoration Command
To restore a site from verified backup files:
```bash
# [Environment-dependent] Restore site from backup archives
docker compose exec -T backend bench --site <YOUR_SITE_NAME> restore \
  /path/to/<date>-<site>-database.sql.gz \
  --with-public-files /path/to/<date>-<site>-files.tar \
  --with-private-files /path/to/<date>-<site>-private-files.tar \
  --db-root-password <MARIADB_ROOT_PASSWORD>
```
*Post-Restoration Steps:*
```bash
# [Environment-dependent] Run migrations and clear cache following a restore
docker compose exec backend bench --site <YOUR_SITE_NAME> migrate
docker compose exec backend bench --site <YOUR_SITE_NAME> clear-cache
```

---

## 8. Upgrade Procedure

Upgrades fall into three distinct categories. Do not combine these categories into a single unmonitored update.

### 8.1 Scenario A: Custom Dashboard App Update (Zero Upstream Change)
*Applies when:* Only code in `sarathi_owner` or `sarathi_visibility` is being updated; Frappe and ERPNext remain at `v16.31.0` / `v16.33.0`.
- **Procedure:** Execute `bash resources/sarathi/deploy.sh`.
- **Downtime:** Approximately 30–90 seconds while maintenance mode is active.
- **Verification:** Run `python resources/sarathi/browser_smoke.py`.

### 8.2 Scenario B: Frappe / ERPNext Upstream Version Upgrade
*Applies when:* Upgrading upstream base image (e.g., from ERPNext `v16.33.0` to `v16.34.0`).

#### Step 1: Execute Pre-Upgrade Compatibility Audit
Run `integration_audit.py` to compare schema manifests against upstream releases:
```bash
# [Verified] Compare current installed schema against target release
python resources/sarathi/integration_audit.py
```
*What This Checks:*
- Compares DocType schema fields before and after.
- Flags any upstream DocType or field deprecations affecting custom queries.
- Identifies newly added required fields.

#### Step 2: Build and Test in Staging
1. Update `ERPNEXT_VERSION` in `sarathi_visibility/Containerfile` and `overrides/compose.sarathi-production.yaml`.
2. Build the new container image in an isolated staging environment.
3. Run the automated test suites: `python -m unittest discover -s sarathi_visibility/sarathi_visibility/tests`.
4. Validate that all 104 tests pass.

#### Step 3: Deploy to Production
Execute `resources/sarathi/deploy.sh` with the new image tag.

### 8.3 Scenario C: Custom App Schema or Fixture Migration
*Applies when:* Adding new custom DocTypes, fields, or modifying `setup/dashboard.py`.
- **Requirement:** Migrations must be strictly backward-compatible. Do not delete columns or alter existing ERPNext core DocTypes.
- **Execution:** Automated by `bench migrate` during `deploy.sh`.

---

## 9. Rollback and Disaster Recovery

### 9.1 Rollback Decision Matrix

```
                          Deployment Failure Detected
                                       │
                  ┌────────────────────┴────────────────────┐
                  ▼                                         ▼
      Did `bench migrate` run?                   `bench migrate` did NOT run
                  │                                         │
        ┌─────────┴─────────┐                               │
        ▼                   ▼                               ▼
Schema changed        Schema unchanged              Code Rollback Only
(DB Migration         (Code-only defect)                    │
 altered tables)            │                               │
        │                   ▼                               ▼
        │         Rollback Docker Image           Rollback Docker Image
        │         & Clear Cache                   to Previous Tag
        │                   │                               │
        ▼                   └───────────────┬───────────────┘
Database & File Restore                     ▼
from Pre-Deploy Snapshot              Fast Recovery (<2 min)
        │
        ▼
Full Recovery (5-15 min)
```

### 9.2 Strategy 1: Code-Only Rollback (Fast Recovery)
*Applies when:* The new release failed due to a frontend bug, JavaScript error, or Python logic error, and **no database schema changes** were executed.

1. **Identify Previous Image:**
   Read the previous container image ID saved automatically in `.sarathi-deploy/`:
   ```bash
   # [Verified in deploy.sh:20] Inspect pre-deployment image tag
   cat $(ls -td .sarathi-deploy/* | head -1)/image-before.txt
   ```
2. **Revert Image and Restart Services:**
   ```bash
   # [Environment-dependent] Re-tag and bring up previous container
   export PREVIOUS_IMAGE=$(cat $(ls -td .sarathi-deploy/* | head -1)/image-before.txt)
   docker compose up -d --no-deps backend frontend websocket
   ```
3. **Clear Cache and Disable Maintenance Mode:**
   ```bash
   # [Environment-dependent]
   docker compose exec -T backend bench --site <YOUR_SITE_NAME> clear-cache
   docker compose exec -T backend bench --site <YOUR_SITE_NAME> set-maintenance-mode off
   docker compose exec -T frontend nginx -s reload
   ```

### 9.3 Strategy 2: Coordinated Database and File Restoration (Disaster Recovery)
*Applies when:* A migration corrupted data, modified columns destructively, or caused database incompatibility that cannot be resolved forward.

> [!CAUTION]
> Reverting Git commits does **NOT** reverse database schema migrations. A database restore is mandatory when schema incompatibility occurs.

1. **Keep Maintenance Mode Enabled:**
   Prevent users and external integrations from writing inconsistent records:
   ```bash
   # [Verified] Confirm maintenance mode is active
   docker compose exec -T backend bench --site <YOUR_SITE_NAME> set-maintenance-mode on
   ```
2. **Stop Background Workers:**
   ```bash
   # [Verified in deploy.sh:25]
   docker compose stop scheduler queue-short queue-long
   ```
3. **Restore Pre-Deployment Backup:**
   Locate the backup generated automatically by `deploy.sh` right before migration:
   ```bash
   # [Environment-dependent] Identify backup archive from pre-deployment state
   export BACKUP_DIR="/home/frappe/frappe-bench/sites/<YOUR_SITE_NAME>/private/backups"
   docker compose exec backend ls -lht "$BACKUP_DIR"
   ```
   Execute restore:
   ```bash
   # [Environment-dependent]
   docker compose exec -T backend bench --site <YOUR_SITE_NAME> restore \
     "$BACKUP_DIR/<TARGET_BACKUP>-database.sql.gz" \
     --with-public-files "$BACKUP_DIR/<TARGET_BACKUP>-files.tar" \
     --with-private-files "$BACKUP_DIR/<TARGET_BACKUP>-private-files.tar" \
     --db-root-password <MARIADB_ROOT_PASSWORD>
   ```
4. **Revert Application Image to Pre-Deployment Version:**
   Update Compose to point to `PREVIOUS_IMAGE`.
5. **Clear Cache and Restart Stack:**
   ```bash
   # [Environment-dependent]
   docker compose exec -T backend bench --site <YOUR_SITE_NAME> clear-cache
   docker compose up -d frontend queue-short queue-long scheduler
   docker compose exec -T frontend nginx -s reload
   docker compose exec -T backend bench --site <YOUR_SITE_NAME> set-maintenance-mode off
   ```

---

## 10. Verification and Troubleshooting Guide

### 10.1 Diagnostic Runbook for Common Failures

#### Problem 1: Custom App Installation Failure (`Could not find app sarathi_owner`)
- **Observable Symptom:** `bench install-app sarathi_owner` exits with `App sarathi_owner does not exist`.
- **Likely Cause:** App folder is missing from `apps/apps.txt` or Python `.pth` link is not configured.
- **Diagnostic Command `[Verified]`:**
  ```bash
  docker compose exec backend python -c "import sarathi_owner, sarathi_visibility; print('Apps importable')"
  ```
- **Corrective Action `[Verified]`:**
  Ensure `apps.txt` lists the app and run configurator:
  ```bash
  docker compose run --rm --no-deps configurator
  ```

#### Problem 2: Missing Application Dependency / Import Error
- **Observable Symptom:** Backend crashes with `ModuleNotFoundError: No module named 'sarathi_owner'`.
- **Likely Cause:** `PYTHONPATH` environment variable is missing from the container definition.
- **Diagnostic Command `[Verified]`:**
  ```bash
  docker compose exec backend env | grep PYTHONPATH
  ```
- **Expected Output:** `PYTHONPATH=/home/frappe/frappe-bench/apps/sarathi_owner` `[Verified in compose.yaml:23]`.
- **Corrective Action `[Verified]`:**
  Verify that `compose.yaml` includes `PYTHONPATH` under `backend`, `configurator`, `queue-short`, `queue-long`, and `scheduler`.

#### Problem 3: Migration Failure (`bench migrate` Fails)
- **Observable Symptom:** `deploy.sh` halts with `[migrator] Migration failed` or MariaDB table lock timeout.
- **Safety Feature `[Verified in test_deploy.py:76-80]`:** `deploy.sh` traps migration errors and **keeps maintenance mode enabled** to prevent corrupted traffic.
- **Diagnostic Command `[Verified]`:**
  ```bash
  docker compose logs --tail=100 backend
  ```
- **Corrective Action:**
  1. Inspect the specific DocType throwing an error.
  2. If a deadlock occurred, restart MariaDB: `docker compose restart db`.
  3. Re-run migration: `docker compose exec backend bench --site <YOUR_SITE_NAME> migrate`.

#### Problem 4: Missing DocTypes or Custom Fields
- **Observable Symptom:** Control Tower fails to load with `ValidationError: Link field custom_sarathi_bom on Project points to invalid BOM`.
- **Likely Cause:** `sarathi_visibility.setup.dashboard.install()` did not run during installation.
- **Diagnostic Command `[Verified]`:**
  ```bash
  docker compose exec backend bench --site <YOUR_SITE_NAME> execute frappe.db.has_column --args "['Project', 'custom_sarathi_bom']"
  ```
- **Corrective Action `[Verified]`:**
  ```bash
  docker compose exec backend bench --site <YOUR_SITE_NAME> execute sarathi_visibility.setup.dashboard.install
  ```

#### Problem 5: Dashboard Desk Route Returns 404 / Page Not Found
- **Observable Symptom:** Navigating to `/desk/sarathiownertower` or `/desk/sarathicontroltower` returns a blank page or 404.
- **Likely Cause:** Page DocType record is missing or not registered in the database.
- **Diagnostic Command `[Verified]`:**
  ```bash
  docker compose exec backend bench --site <YOUR_SITE_NAME> execute frappe.db.get_value --args "['Page', 'sarathiownertower', 'name']"
  ```
- **Corrective Action `[Verified in sarathi_owner/setup/install.py:41-67]`:**
  Re-register the page via bench:
  ```bash
  docker compose exec backend bench --site <YOUR_SITE_NAME> execute sarathi_owner.setup.install._ensure_owner_page --args "['sarathiownertower']"
  docker compose exec backend bench --site <YOUR_SITE_NAME> execute sarathi_visibility.setup.install._ensure_control_tower_page --args "['sarathicontroltower']"
  docker compose exec backend bench --site <YOUR_SITE_NAME> clear-cache
  ```

#### Problem 6: Frontend Assets Not Updated (Stale JS/CSS)
- **Observable Symptom:** Dashboard displays old UI layout despite updating source code or container image.
- **Likely Cause:** Browser caching, NGINX asset caching, or assets not copied into `assets/`.
- **Diagnostic Command `[Verified]`:**
  ```bash
  curl -I http://localhost:8080/assets/sarathi_visibility/js/sarathi_dashboard.js
  ```
- **Corrective Action `[Verified]`:**
  1. Build / copy assets inside bench:
     ```bash
     docker compose exec backend bench build --app sarathi_visibility --app sarathi_owner
     ```
  2. Reload NGINX:
     ```bash
     docker compose exec frontend nginx -s reload
     ```
  3. Force hard refresh in browser (`Ctrl + F5` or `Cmd + Shift + R`).

#### Problem 7: API Authorization Failure (`403 Forbidden` / `PermissionError`)
- **Observable Symptom:** Dashboard cards display "Access Restricted" or console logs show HTTP 403 on API endpoints.
- **Likely Cause:** The user lacks either the dashboard capability role (`Sarathi Owner`, `Manufacturing Manager`, `Sarathi Supervisor`) or the required native ERPNext DocType read rights.
- **Diagnostic Command `[Verified]`:**
  ```bash
  docker compose exec backend bench --site <YOUR_SITE_NAME> execute sarathi_visibility.api.permissions.has_owner_access
  ```
- **Corrective Action `[Verified in docs/dashboard-permission-matrix.md]`:**
  Ensure the user has:
  1. Dashboard Capability Role: Assigned `Sarathi Owner` (for Executive Tower) or `Manufacturing Manager` (for Control Tower).
  2. Native ERPNext Document Roles: Assigned `Accounts User` / `Accounts Manager` for financial data, `Stock User` for inventory, and `Manufacturing User` for Work Orders.
  3. User Permissions: Verify that restrictive `User Permission` records on `Company` or `Customer` do not inadvertently filter out all records.

#### Problem 8: Dashboard Displays Zero When Data Is Expected
- **Observable Symptom:** Production or Financial KPI cards show `0.00` despite existing transactions in ERPNext.
- **Likely Cause:** Filter mismatch (e.g., active Company filter does not match the company of submitted transactions, or documents are in Draft `docstatus=0` rather than Submitted `docstatus=1`).
- **Diagnostic Check `[Verified in docs/finance-kpi-reconciliation.md]`:**
  Check whether transactions exist for the selected company:
  ```bash
  docker compose exec backend bench --site <YOUR_SITE_NAME> execute frappe.db.count --args "['Sales Invoice', {'company': 'Your Company', 'docstatus': 1}]"
  ```
- **Corrective Action:**
  Select the correct operating company in the dashboard header dropdown filter. Confirm transactions are submitted (`docstatus=1`).

#### Problem 9: Missing Employee or Supervisor Assignment on Shop-Floor Workboard
- **Observable Symptom:** Operator logs into `/desk/sarathishopfloor` and sees "No assigned jobs".
- **Likely Cause:** The logged-in Frappe user is not linked to an `Employee` record, or the Job Card has no open `ToDo` assignment.
- **Diagnostic Command `[Verified in docs/shop-floor-assigned-job-api.md]`:**
  ```bash
  docker compose exec backend bench --site <YOUR_SITE_NAME> execute frappe.db.get_value --args "['Employee', {'user_id': 'operator@example.com'}, 'name']"
  ```
- **Corrective Action:**
  1. Link the user account to the Employee profile: In ERPNext, open the `Employee` document and set `User ID`.
  2. Ensure the Job Card is assigned via the standard ERPNext `Assign To` action (creating a `ToDo` record for the user).

#### Problem 10: Database Connection Failure (`Can't connect to MySQL server`)
- **Observable Symptom:** Backend returns HTTP 502 / 500 with `OperationalError: (2002, "Can't connect to server on 'db'")`.
- **Diagnostic Command `[Verified]`:**
  ```bash
  docker compose ps db
  docker compose logs db --tail=50
  ```
- **Corrective Action:**
  Check if MariaDB is healthy:
  ```bash
  docker compose exec db healthcheck.sh --connect --innodb_initialized
  ```
  If MariaDB is stopped, verify disk space (`df -h`) and restart: `docker compose up -d db`.

#### Problem 11: Windows WSL2 / Docker Desktop Runtime Hang
- **Observable Symptom:** Docker commands hang indefinitely on Windows host, reporting `HCS_E_CONNECTION_TIMEOUT` or disk sharing violation.
- **Diagnostic Reference `[Verified in docs/local-docker-wsl-recovery.md]`:**
- **Corrective Action `[Verified]`:**
  Run the automated recovery script in PowerShell:
  ```powershell
  powershell -ExecutionPolicy Bypass -File resources/sarathi/recover-local-runtime.ps1
  ```
  If VM compute remains stuck, restart the Windows host machine (**Start > Power > Restart**).

#### Problem 12: Insufficient Disk Space Halts MariaDB
- **Observable Symptom:** MariaDB crashes or enters read-only mode; binary logs consume available space.
- **Diagnostic Command `[Verified]`:**
  ```bash
  docker compose exec db df -h /var/lib/mysql
  ```
- **Corrective Action `[Environment-dependent]`:**
  1. Purge old Docker build caches: `docker builder prune -f`.
  2. Purge unused container logs: `truncate -s 0 /var/lib/docker/containers/*/*-json.log`.
  3. Purge expired MariaDB binary logs:
     ```sql
     PURGE BINARY LOGS BEFORE DATE_SUB(NOW(), INTERVAL 3 DAY);
     ```

---

## 11. Security and Operational Checklists

### 11.1 Pre-Release Checklist (Complete Before Deploying)
- [ ] **Target Site Confirmed:** Verified target site name matches `SARATHI_SITE` / `FRAPPE_SITE_NAME_HEADER`.
- [ ] **Git Working Tree Clean:** All modifications committed and tagged in version control.
- [ ] **Automated Test Matrix Passing:** All 104 tests in the test suite pass (reconciliation, permissions, integration, performance).
- [ ] **Production Image Built & Tested:** Container image built with baked assets and verified in staging.
- [ ] **Backup Verified:** Pre-deployment database dump and file archives generated and tested for gzip/tar integrity.
- [ ] **Disk Capacity Checked:** Host has at least 10 GB of available SSD storage on the Docker partition.
- [ ] **Off-Peak Window Scheduled:** Deployment scheduled during planned maintenance or low-traffic window.

### 11.2 Post-Release Checklist (Complete After Deploying)
- [ ] **Maintenance Mode Disabled:** Confirmed `bench set-maintenance-mode off` was executed.
- [ ] **Service Health Checked:** All 10 Docker containers running with status `healthy` or `running`.
- [ ] **Dashboard Routes Verified:**
  - `/desk/sarathiownertower` loads without JavaScript console errors.
  - `/desk/sarathicontroltower` loads and displays factory overview metrics.
  - `/desk/sarathishopfloor` loads mobile workboard view.
- [ ] **Realtime Event Dispatching Tested:** Verified WebSocket connection established with `websocket:9000`.
- [ ] **Access Authorization Checked:** Verified that non-owner users cannot access `/desk/sarathiownertower`.
- [ ] **Application Logs Reviewed:** Confirmed no exceptions in `docker compose logs --tail=100 backend`.
- [ ] **Deployment State Persisted:** Confirmed pre/post metadata manifests stored in `.sarathi-deploy/`.

### 11.3 Security & Least Privilege Standards
- **Standard Frappe Auth:** The dashboards strictly use standard Frappe session cookies and CSRF tokens (`frappe.csrf_token`). Do not build custom authorization layers or bypass Frappe's user session.
- **Two-Tier Access Control:** Access to any metric requires both (1) the Dashboard Capability Role, and (2) native Frappe document read permissions. Capability roles never grant raw database bypass.
- **Zero Secrets in Documentation:** Never include real production passwords, API secret keys, or private SSH certificates in documentation or logs. Use `<PLACEHOLDERS>` consistently.

---

## 12. Environment-Specific Limitations and Dependencies

### 12.1 Local Development vs. Production VPS Differences

| Operational Dimension | Local Development (Windows / WSL2) | Production VPS (Linux / Ubuntu) |
| :--- | :--- | :--- |
| **Compose Strategy** | `compose.yaml` (with local code bind-mounts) | `compose.yaml` + `overrides/compose.sarathi-production.yaml` |
| **Application Code Source** | Host filesystem mounted directly into container | Immutable baked container image (`Containerfile`) |
| **Site Name** | `frontend` | Production FQDN (e.g., `erp.sarathiailabs.com`) |
| **Web Server Port** | `8080` (Direct NGINX HTTP) | `443` (HTTPS via Traefik or reverse proxy) |
| **Developer Mode** | `developer_mode = 1` | `developer_mode = 0` (Strictly enforced) |
| **Database Passwords** | Local development default (`admin`) | Strong, cryptographically random password |
| **Background Scheduler** | Local container worker | Ofelia automated backup cron + Celery workers |

### 12.2 Known Platform Limitations
1. **Windows WSL2 File Sharing Violations:** On Windows development environments, Docker Desktop may occasionally encounter file lock violations on virtual disk `.vhdx` files if restarted improperly. Follow the instructions in [docs/local-docker-wsl-recovery.md](local-docker-wsl-recovery.md) rather than resetting or deleting the distribution.
2. **Reverse Proxy Origin Preservation:** Frappe's WebSocket server requires the exact browser HTTP origin to match the incoming WebSocket handshake. In production environments where Traefik or an external reverse proxy sits in front of NGINX, the NGINX configuration template must map `$http_origin` dynamically as implemented in `sarathi_visibility/Containerfile:6-7`.
3. **Hard Server Pagination:** All Work Order and Job Card queue APIs enforce `MAX_PAGE_SIZE = 100`. Custom frontend integrations must use offset pagination (`start`, `page_length`) rather than attempting to retrieve unbounded datasets.

---

## 13. Operational Sign-Off and Maintenance Record

| Audit Date | Operational Lead | Verification Scope | Status |
| :--- | :--- | :--- | :---: |
| **2026-10-15** | Sarathi Platform Team | DASH-035 Installation, Operations, Backup & Recovery Manual | **APPROVED & VERIFIED** |
