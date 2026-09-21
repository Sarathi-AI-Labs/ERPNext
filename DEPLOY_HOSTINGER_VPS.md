# Production Deployment Guide: ERPNext + Sarathi Visibility on Hostinger VPS

This guide walks you through the step-by-step production deployment of this repository on a **Hostinger KVM VPS** using Docker, Docker Compose v2, MariaDB 11.8, Redis, and Traefik v3 with automatic Let's Encrypt SSL.

---

## 1. Architecture Overview

In production on your Hostinger VPS, services run across isolated Docker containers managed by Docker Compose:

```text
                                 Public Internet
                                        │
                         HTTP (:80) / HTTPS (:443)
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │          Traefik v3.7 Proxy               │
                  │    (Auto Let's Encrypt SSL / ACME)        │
                  └─────────────────────┬─────────────────────┘
                                        │ (Port 8080 internal)
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │            Frontend (NGINX)               │
                  │        (Serves HTML / Static Assets)      │
                  └───────────────┬───────────────────────────┘
                                  │
               ┌──────────────────┴──────────────────┐
               │ /api, /desk                         │ /socket.io
               ▼                                     ▼
┌─────────────────────────────┐       ┌─────────────────────────────┐
│      Backend (Gunicorn)     │◄──────┤     Websocket (Node.js)     │
│   (Frappe / ERPNext v16)    │       │ (SARATHI_SOCKET_BACKEND_URL)│
└──────────────┬──────────────┘       └──────────────┬──────────────┘
               │                                     │
               ├──────────────────┬──────────────────┤
               ▼                  ▼                  ▼
┌────────────────────────┐ ┌───────────────┐ ┌───────────────┐
│     MariaDB 11.8       │ │  Redis Cache  │ │  Redis Queue  │
│  (Persistent Volume)   │ │  (In-Memory)  │ │ (RQ Workers)  │
└────────────────────────┘ └───────────────┘ └───────┬───────┘
                                                     │
                                 ┌───────────────────┴───────────────────┐
                                 ▼                                       ▼
                    ┌─────────────────────────┐             ┌─────────────────────────┐
                    │  Worker: queue-short    │             │   Worker: queue-long    │
                    └─────────────────────────┘             └─────────────────────────┘
                                                            ┌─────────────────────────┐
                                                            │     Bench Scheduler     │
                                                            └─────────────────────────┘
```

---

## 2. Hostinger VPS Sizing & System Preparation

### Recommended VPS Plan
- **Minimum:** Hostinger KVM 1 (4 GB RAM, 1 vCPU, 50 GB NVMe) — *Requires configuring Swap!*
- **Recommended for Production:** Hostinger KVM 2 (8 GB RAM, 2 vCPUs, 100 GB NVMe)

### Step 2.1: Connect via SSH
```bash
ssh root@YOUR_VPS_IP
```

### Step 2.2: Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw jq
```

### Step 2.3: Configure Swap Space (Crucial for 4GB RAM)
Frappe bench operations, database indexing, and asset building are memory-intensive. Setting up a 4GB or 8GB swap space prevents out-of-memory (OOM) crashes:
```bash
# Verify if swap exists
free -h

# If no swap or swap < 4GB, create an 8GB swapfile
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Persist across reboots
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Optimize swappiness for database performance
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

### Step 2.4: Configure Hostinger Firewall (UFW)
Open only required public ports:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH (or your custom SSH port)
sudo ufw allow 80/tcp      # HTTP (Let's Encrypt validation & redirect)
sudo ufw allow 443/tcp     # HTTPS (Web traffic)
sudo ufw --force enable
sudo ufw status
```
*Note: Databases (3306), Redis (6379), Backend (8000), and Websocket (9000) remain safely isolated inside Docker's internal network.*

---

## 3. Install Docker Engine and Docker Compose v2

Use Docker's official automated installation:
```bash
curl -fsSL https://get.docker.com | sh

# Verify installation
docker --version
docker compose version
```

---

## 4. DNS Configuration

Before setting up SSL, point your domain to your Hostinger VPS:
1. Log into your domain registrar / DNS provider (Cloudflare, Hostinger DNS, GoDaddy, etc.).
2. Create an **A Record**:
   - **Name / Host:** `erp` (or `@` for root domain)
   - **Type:** `A`
   - **Value / IP:** `YOUR_VPS_IP`
   - **TTL:** Auto or 300 seconds
3. *(Important Cloudflare note)*: If you use Cloudflare, set the proxy status to **DNS Only (Grey Cloud)** during first initialization so Let's Encrypt HTTP-01 challenges complete without friction.

Verify DNS propagation:
```bash
ping erp.yourdomain.com
```

---

## 5. Clone and Configure the Repository

### Step 5.1: Clone the Codebase
```bash
cd /opt
# Or clone your private repository
git clone https://github.com/Sarathi-AI-Labs/Frappe_docker_main.git frappe_docker
cd frappe_docker
```

### Step 5.2: Create the Production Environment File (`.env`)
Copy the provided template:
```bash
cp hostinger.env.example .env
nano .env
```

Set the following production parameters in `.env`:
```env
# 1. Custom Image & Pull Policy
ERPNEXT_VERSION=v16.33.0
CUSTOM_IMAGE=sarathi/erpnext-sarathi
CUSTOM_TAG=v16.33.0
PULL_POLICY=never
RESTART_POLICY=unless-stopped

# 2. Database Password (Generate a strong password!)
DB_PASSWORD=YourUltraSecureDbPassword123!

# 3. Domain and Let's Encrypt SSL
LETSENCRYPT_EMAIL=admin@yourdomain.com
SITES_RULE=Host(`erp.yourdomain.com`)

# 4. Gunicorn Tuning (Adjust for VPS RAM)
GUNICORN_WORKERS=2
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120
CLIENT_MAX_BODY_SIZE=50m
```

---

## 6. Build the Custom Sarathi Docker Image

Build the custom ERPNext image containing the `sarathi_visibility` application:
```bash
docker build -f sarathi_visibility/Containerfile \
  --build-arg ERPNEXT_VERSION=v16.33.0 \
  -t sarathi/erpnext-sarathi:v16.33.0 .
```

Verify that the image was created:
```bash
docker images | grep sarathi
```

---

## 7. Start the Production Stack

Launch the stack using the core compose file along with the MariaDB, Redis, HTTPS (Traefik), and Sarathi overrides:

```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  up -d
```

### Check Container Status
```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  ps
```
Ensure all containers are running (`db` must show `healthy`, `configurator` will show `exited (0)` which is expected).

---

## 8. Create Site and Install the Sarathi App

Once the stack is running, initialize your production site. **The site name should match your domain name**:

### Step 8.1: Create the Site
```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  exec backend bench new-site erp.yourdomain.com \
    --mariadb-user-host-login-scope='%' \
    --admin-password='YourAdminPasswordHere' \
    --db-root-password='YourUltraSecureDbPassword123!' \
    --install-app erpnext \
    --set-default
```

### Step 8.2: Install `sarathi_visibility`
```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  exec backend bench --site erp.yourdomain.com install-app sarathi_visibility
```

### Step 8.3: Clear Cache and Run Migrations
```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  exec backend bench --site erp.yourdomain.com migrate

docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  exec backend bench --site erp.yourdomain.com clear-cache
```

---

## 9. Accessing the Application

1. Open your browser and navigate to:
   ```text
   https://erp.yourdomain.com
   ```
2. Log in with:
   - **Username:** `Administrator`
   - **Password:** The admin password set during `bench new-site`
3. Access the Sarathi Control Tower dashboard at:
   ```text
   https://erp.yourdomain.com/desk/sarathicontroltower
   ```

---

## 10. Routine Operations & Maintenance

### Creating Backups
```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  exec backend bench --site erp.yourdomain.com backup --with-files
```
Backups are saved inside the `sites` volume under `sites/erp.yourdomain.com/private/backups/`.

### Updating Code / Rebuilding the Custom App
When code inside `sarathi_visibility` changes:
```bash
# 1. Rebuild image
docker build -f sarathi_visibility/Containerfile --build-arg ERPNEXT_VERSION=v16.33.0 -t sarathi/erpnext-sarathi:v16.33.0 .

# 2. Recreate containers
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  up -d --force-recreate backend frontend websocket queue-short queue-long scheduler

# 3. Run migrations and clear cache
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  exec backend bench --site erp.yourdomain.com migrate

docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.sarathi.yaml \
  exec backend bench --site erp.yourdomain.com clear-cache
```

### Aliasing the Command for Convenience
To avoid typing the long `-f` list repeatedly, create an alias on the VPS in `~/.bashrc`:
```bash
alias dcompose="docker compose --env-file /opt/frappe_docker/.env -f /opt/frappe_docker/compose.yaml -f /opt/frappe_docker/overrides/compose.mariadb.yaml -f /opt/frappe_docker/overrides/compose.redis.yaml -f /opt/frappe_docker/overrides/compose.https.yaml -f /opt/frappe_docker/overrides/compose.sarathi.yaml"
```
Then run:
```bash
dcompose ps
dcompose logs -f backend
```
