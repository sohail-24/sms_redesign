# 🚀 Deployment Guide

This project is fully containerized and designed for **repeatable, production-style deployments** using Docker and Docker Compose.

The same steps work on:

* Fresh servers
* Cloud VMs (AWS / GCP / Azure)
* Local development machines

---

## 📦 Prerequisites

Ensure the following are installed on the server:

* Docker (>= 24.x)
* Docker Compose (v2)
* Git

Verify:

```bash
docker --version
docker compose version
git --version
```

---

## 📥 Step 1: Clone the Repository

```bash
git clone https://github.com/sohail-24/<your-repo-name>.git
cd <your-repo-name>/sms_backend
```

---

## 🔐 Step 2: Environment Configuration

Create the environment file:

```bash
cp .env.example .env
```

```bash
openssl rand -base64 48
```

Edit `.env` with production values:

```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=change-this-to-a-secure-value

DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

DB_NAME=sms_db
DB_USER=sms_user
DB_PASSWORD=sms_password
DB_HOST=sms_db
DB_PORT=5432

REDIS_URL=redis://sms_redis:6379/0

CELERY_BROKER_URL=redis://sms_redis:6379/0
CELERY_RESULT_BACKEND=redis://sms_redis:6379/0
```

⚠️ **Never commit `.env` to GitHub**

---

## 🛠️ Step 3: Build Docker Images

Always build images after a fresh pull:

```bash
 chmod +x docker/entrypoint.sh
```
```bash
docker-compose build
```

This ensures:

* Dependencies are installed
* Migrations are available
* Code is up to date

---

## ▶️ Step 4: Start the Application Stack

```bash
docker-compose up -d
```

This starts:

* PostgreSQL
* Redis
* Django API
* Celery Worker
* Celery Beat
* Flower
* Nginx

---

## 🧱 Step 5: Apply Database Migrations

Migrations are **committed to the repository**, so this step is safe and idempotent:

```bash
docker-compose exec web python manage.py migrate
```

Expected result:

```text
No migrations to apply
```

---

## 👤 Step 6: Create Superuser (First Time Only)

```bash
docker-compose exec web python manage.py createsuperuser
```

Used to access Django Admin.

---
✅ Step 10: Restart Stack (Final Clean Start)
docker-compose restart
✅ Step 11: Health Checks
curl http://localhost/health/

Expected:

{"status": "ok"}

Check logs:

docker-compose logs -f web
docker-compose logs -f celery_worker
🌐 Access URLs

Admin: http://<EC2_PUBLIC_IP>/admin/

API: http://<EC2_PUBLIC_IP>/

Flower: http://<EC2_PUBLIC_IP>:5555

🧠 Production Rules

.env → server only

No manual DB changes

Always redeploy with:

git pull
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
## 🗂️ Step 7: Collect Static Files (Optional)

Only required if:

* Admin UI looks broken
* Deploying behind Nginx

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

---

## 🌐 Accessing the Services

| Service                 | URL                         |
| ----------------------- | --------------------------- |
| API                     | http://SERVER_IP:8000       |
| Admin Panel             | http://SERVER_IP:8000/admin |
| Flower (Celery Monitor) | http://SERVER_IP:5555       |

---

## 🔁 Redeploy / Update Workflow

For new code updates:

```bash
git pull
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
```

---

## 🧠 Deployment Philosophy

* Migrations are **tracked and versioned**
* No manual database changes
* No environment-specific code
* Same steps work everywhere

This ensures **predictable, production-safe deployments**.
