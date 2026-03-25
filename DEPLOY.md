# ILMA — Guide de Déploiement VPS AlmaLinux 10 (de A à Z)

> Ce guide couvre le déploiement complet d'ILMA sur un VPS AlmaLinux 10.
> Durée estimée : 30-45 minutes.

---

## Prérequis

- Un VPS AlmaLinux 10 (minimum 2 vCPU, 2 Go RAM, 20 Go SSD)
- Un nom de domaine pointant vers l'IP du VPS (ex: `ilma.app`)
- Un accès SSH root ou sudo
- Le dépôt Git hébergé quelque part (GitHub, GitLab, etc.)

---

## Étape 1 — Préparer le serveur

### 1.1 Se connecter et mettre à jour

```bash
ssh root@VOTRE_IP

dnf update -y
```

### 1.2 Créer un utilisateur dédié (ne pas tout faire en root)

```bash
useradd -m -s /bin/bash ilma
passwd ilma
usermod -aG wheel ilma
su - ilma
```

### 1.3 Installer Docker

```bash
# Ajouter le dépôt Docker officiel
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo

# Installer Docker Engine + Compose
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Démarrer et activer Docker
sudo systemctl enable --now docker

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Se reconnecter pour que le groupe prenne effet
exit
su - ilma

# Vérifier
docker --version
docker compose version
```

### 1.4 Installer les outils utiles

```bash
sudo dnf install -y git curl nano
```

### 1.5 Configurer le pare-feu (firewalld)

AlmaLinux utilise `firewalld` (pas `ufw`) :

```bash
# Vérifier que firewalld tourne
sudo systemctl enable --now firewalld

# Ouvrir les ports nécessaires
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh

# Appliquer
sudo firewall-cmd --reload

# Vérifier
sudo firewall-cmd --list-all
```

### 1.6 Configurer SELinux pour Docker

AlmaLinux a SELinux activé par défaut. Docker fonctionne avec, mais si vous rencontrez des problèmes de permissions :

```bash
# Vérifier le statut SELinux
getenforce

# Si besoin, autoriser les containers à accéder au réseau
sudo setsebool -P container_manage_cgroup on
```

> **Note :** Ne désactivez pas SELinux. Il est une couche de sécurité importante.
> Si un problème survient, consultez les logs : `sudo ausearch -m avc -ts recent`

---

## Étape 2 — Cloner le projet

```bash
cd /home/ilma
git clone https://github.com/VOTRE_REPO/ilma.git
cd ilma
```

---

## Étape 3 — Configurer les variables d'environnement

### 3.1 Créer le fichier `.env` de production pour le backend

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Contenu à adapter :

```env
# PostgreSQL
POSTGRES_USER=ilma_user
POSTGRES_PASSWORD=UN_MOT_DE_PASSE_FORT_ICI
POSTGRES_DB=ilma_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# API
API_V1_STR=/api/v1
PROJECT_NAME=ILMA Backend

# JWT — IMPORTANT : générer une clé secrète unique
SECRET_KEY=VOTRE_CLE_SECRETE_64_CHARS
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# CORS — mettre votre domaine
BACKEND_CORS_ORIGINS='["https://ilma.app","https://www.ilma.app"]'

# SMS (laisser mock pour commencer, passer à twilio plus tard)
SMS_PROVIDER=mock
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=

# Push
PUSH_PROVIDER=mock

# Notifications
NOTIFICATIONS_ENABLED=true
NOTIFICATION_MAX_PER_DAY=2

# Paiement (sandbox pour commencer)
KKIAPAY_PUBLIC_KEY=
KKIAPAY_PRIVATE_KEY=
KKIAPAY_SECRET=
FEDAPAY_API_KEY=
FEDAPAY_ENVIRONMENT=sandbox

# S3 / Minio (interne au réseau Docker)
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=VOTRE_MINIO_ACCESS_KEY
S3_SECRET_KEY=VOTRE_MINIO_SECRET_KEY
S3_BUCKET=ilma-packs
S3_REGION=us-east-1
```

Pour générer la `SECRET_KEY` :

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 3.2 Créer le fichier `.env` frontend (optionnel)

```bash
cat > frontend/.env.production << 'EOF'
VITE_API_URL=/api/v1
VITE_SENTRY_DSN=
EOF
```

---

## Étape 4 — Docker Compose de production

Créer `docker-compose.prod.yml` à la racine :

```bash
cat > docker-compose.prod.yml << 'COMPOSE'
version: "3.9"

services:
  # ── Frontend (Nginx + SPA + reverse proxy API) ──
  frontend:
    build: ./frontend
    container_name: ilma-frontend
    ports:
      - "3080:80"
    depends_on:
      - api
    restart: always

  # ── Backend API ──
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ilma-api
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
    env_file:
      - ./backend/.env
    environment:
      - POSTGRES_HOST=db
      - REDIS_HOST=redis
      - S3_ENDPOINT=http://minio:9000
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    restart: always

  # ── PostgreSQL ──
  db:
    image: postgres:15-alpine
    container_name: ilma-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-ilma_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-ilma_password}
      POSTGRES_DB: ${POSTGRES_DB:-ilma_db}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ilma_user -d ilma_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  # ── Redis ──
  redis:
    image: redis:7-alpine
    container_name: ilma-redis
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  # ── Minio (S3-compatible object storage) ──
  minio:
    image: minio/minio:latest
    container_name: ilma-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${S3_ACCESS_KEY:-ilma_minio}
      MINIO_ROOT_PASSWORD: ${S3_SECRET_KEY:-ilma_minio_secret}
    volumes:
      - miniodata:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  # ── Minio init (create bucket on first start) ──
  minio-init:
    image: minio/mc:latest
    container_name: ilma-minio-init
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: >
      /bin/sh -c "
      mc alias set ilma http://minio:9000 $${MINIO_ROOT_USER:-ilma_minio} $${MINIO_ROOT_PASSWORD:-ilma_minio_secret};
      mc mb --ignore-existing ilma/ilma-packs;
      mc anonymous set download ilma/ilma-packs;
      exit 0;
      "
    restart: "no"

volumes:
  pgdata:
  redisdata:
  miniodata:
COMPOSE
```

Différences clés avec le docker-compose de dev :
- `--workers 4` au lieu de `--reload`
- `restart: always` sur tous les services
- Port frontend `3080:80` (Caddy gère le 80/443)
- Pas de ports exposés pour PostgreSQL, Redis ni Minio
- Volume Redis pour la persistance
- Mémoire Redis limitée à 128 Mo

---

## Étape 5 — Build et lancement

### 5.1 Construire les images

```bash
cd /home/ilma/ilma
docker compose -f docker-compose.prod.yml build
```

### 5.2 Démarrer les services

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 5.3 Vérifier que tout est up

```bash
docker compose -f docker-compose.prod.yml ps
```

Tous les services doivent être `Up (healthy)`.

### 5.4 Exécuter les migrations Alembic

```bash
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### 5.5 Vérifier l'accès

```bash
# API health check
curl http://localhost:3080/api/v1/health

# Frontend
curl -s http://localhost:3080 | head -5
```

---

## Étape 6 — HTTPS avec Caddy

Caddy est le choix le plus simple : HTTPS automatique via Let's Encrypt, zero config TLS.

### 6.1 Installer Caddy

```bash
# Installer le dépôt COPR pour Caddy
sudo dnf install -y 'dnf-command(copr)'
sudo dnf copr enable -y @caddy/caddy
sudo dnf install -y caddy
```

### 6.2 Configurer le reverse proxy

```bash
sudo tee /etc/caddy/Caddyfile << 'EOF'
ilma.app {
    reverse_proxy localhost:3080
    encode gzip

    header {
        # Sécurité
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"

        # Supprimer le header serveur
        -Server
    }

    # Logs d'accès
    log {
        output file /var/log/caddy/ilma-access.log {
            roll_size 10mb
            roll_keep 5
        }
    }
}
EOF
```

### 6.3 Démarrer Caddy

```bash
sudo systemctl enable --now caddy

# Vérifier le statut
sudo systemctl status caddy

# Vérifier les logs si besoin
sudo journalctl -u caddy -f
```

Caddy obtient et renouvelle automatiquement le certificat Let's Encrypt.

### 6.4 Vérifier HTTPS

```bash
curl -I https://ilma.app
```

Vous devriez voir `HTTP/2 200` avec le header `Strict-Transport-Security`.

---

## Étape 7 — Créer le premier compte admin

```bash
docker compose -f docker-compose.prod.yml exec api python3 -c "
import asyncio
from app.db.session import async_session
from app.models.user import User, UserRole
from app.core.security import get_password_hash

async def create_admin():
    async with async_session() as db:
        admin = User(
            email='admin@ilma.app',
            full_name='Administrateur ILMA',
            hashed_password=get_password_hash('Xr;aTRKMx_1CI1Wd@HF1c!9'),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        print(f'Admin créé: {admin.email} (id={admin.id})')

asyncio.run(create_admin())
"
```

**Changez le mot de passe immédiatement après la première connexion.**

---

## Étape 8 — Sauvegardes automatiques

### 8.1 Script de backup PostgreSQL

```bash
sudo mkdir -p /opt/ilma/backups

sudo tee /opt/ilma/backup.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/opt/ilma/backups"
DATE=$(date +%Y-%m-%d_%H%M)
KEEP_DAYS=14

# Dump PostgreSQL
docker exec ilma-db pg_dump -U ilma_user ilma_db | gzip > "$BACKUP_DIR/ilma_db_$DATE.sql.gz"

# Supprimer les backups de plus de $KEEP_DAYS jours
find "$BACKUP_DIR" -name "ilma_db_*.sql.gz" -mtime +$KEEP_DAYS -delete

echo "[$(date)] Backup OK: ilma_db_$DATE.sql.gz ($(du -h "$BACKUP_DIR/ilma_db_$DATE.sql.gz" | cut -f1))"
SCRIPT

sudo chmod +x /opt/ilma/backup.sh
```

### 8.2 Planifier le backup quotidien (3h du matin)

```bash
# Utiliser un timer systemd (plus fiable que cron sur RHEL/Alma)
sudo tee /etc/systemd/system/ilma-backup.service << 'EOF'
[Unit]
Description=ILMA PostgreSQL Backup
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
ExecStart=/opt/ilma/backup.sh
User=ilma
EOF

sudo tee /etc/systemd/system/ilma-backup.timer << 'EOF'
[Unit]
Description=ILMA daily backup at 3:00 AM

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now ilma-backup.timer

# Vérifier
sudo systemctl list-timers | grep ilma
```

### 8.3 Restaurer un backup

```bash
gunzip < /opt/ilma/backups/ilma_db_2026-03-19_0300.sql.gz | \
  docker exec -i ilma-db psql -U ilma_user ilma_db
```

---

## Étape 9 — Monitoring (Sentry + UptimeRobot)

### 9.1 Sentry (error tracking)

1. Créer un compte gratuit sur [sentry.io](https://sentry.io)
2. Créer un projet **Python** (backend) et un projet **React** (frontend)
3. Ajouter les DSN :

**Backend** — dans `backend/.env` :
```env
SENTRY_DSN=https://xxx@sentry.io/yyy
```

**Frontend** — dans `frontend/.env.production` :
```env
VITE_SENTRY_DSN=https://xxx@sentry.io/zzz
```

4. Rebuild et redéployer :
```bash
docker compose -f docker-compose.prod.yml up -d --build frontend
```

### 9.2 UptimeRobot (monitoring uptime)

1. Créer un compte gratuit sur [uptimerobot.com](https://uptimerobot.com)
2. Ajouter un moniteur HTTP :
   - URL : `https://ilma.app/api/v1/health`
   - Intervalle : 5 minutes
   - Alertes : email (ou Telegram/Slack)

---

## Étape 10 — Mises à jour (déploiement continu)

### 10.1 Mise à jour manuelle

```bash
cd /home/ilma/ilma

# Récupérer les changements
git pull origin main

# Rebuild et redéployer
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Exécuter les nouvelles migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Vérifier
docker compose -f docker-compose.prod.yml ps
curl https://ilma.app/api/v1/health
```

### 10.2 Script de déploiement automatisé

```bash
sudo tee /opt/ilma/deploy.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail

cd /home/ilma/ilma

echo "=== [1/5] Pulling latest code ==="
git pull origin main

echo "=== [2/5] Backup database ==="
/opt/ilma/backup.sh

echo "=== [3/5] Building images ==="
docker compose -f docker-compose.prod.yml build

echo "=== [4/5] Starting services ==="
docker compose -f docker-compose.prod.yml up -d

echo "=== [5/5] Running migrations ==="
docker compose -f docker-compose.prod.yml exec -T api alembic upgrade head

echo "=== Deploy complete at $(date) ==="
curl -sf https://ilma.app/api/v1/health | python3 -m json.tool
SCRIPT

sudo chmod +x /opt/ilma/deploy.sh
```

Usage : `/opt/ilma/deploy.sh`

### 10.3 Déploiement via GitHub Actions (CI/CD)

Ajouter ces secrets dans GitHub :
- `VPS_HOST` : IP du VPS
- `VPS_USER` : `ilma`
- `VPS_SSH_KEY` : clé privée SSH

Puis ajouter un job dans `.github/workflows/ci.yml` :

```yaml
deploy-production:
  needs: [build, docker-build]
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to VPS
      uses: appleboy/ssh-action@v1
      with:
        host: ${{ secrets.VPS_HOST }}
        username: ${{ secrets.VPS_USER }}
        key: ${{ secrets.VPS_SSH_KEY }}
        script: /opt/ilma/deploy.sh
```

---

## Étape 11 — Sécurisation du serveur

### 11.1 Copier votre clé SSH (depuis votre machine locale)

**Faire ceci AVANT de désactiver le login par mot de passe :**

```bash
# Depuis votre machine locale
ssh-copy-id ilma@VOTRE_IP
```

### 11.2 SSH hardening

```bash
sudo nano /etc/ssh/sshd_config
```

Modifier :
```
PermitRootLogin no
PasswordAuthentication no
MaxAuthTries 3
```

```bash
sudo systemctl restart sshd
```

### 11.3 Fail2ban (protection brute-force)

```bash
sudo dnf install -y epel-release
sudo dnf install -y fail2ban

# Créer la config locale
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
backend = systemd
EOF

sudo systemctl enable --now fail2ban

# Vérifier
sudo fail2ban-client status sshd
```

### 11.4 Mises à jour automatiques de sécurité

```bash
sudo dnf install -y dnf-automatic

# Configurer pour appliquer uniquement les patchs de sécurité
sudo sed -i 's/apply_updates = no/apply_updates = yes/' /etc/dnf/automatic.conf
sudo sed -i 's/upgrade_type = default/upgrade_type = security/' /etc/dnf/automatic.conf

sudo systemctl enable --now dnf-automatic.timer

# Vérifier
sudo systemctl status dnf-automatic.timer
```

---

## Étape 12 — Logs et debug

### Voir les logs en temps réel

```bash
# Tous les services
docker compose -f docker-compose.prod.yml logs -f

# Un service spécifique
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f db
```

### Logs Caddy

```bash
sudo journalctl -u caddy -f
sudo tail -f /var/log/caddy/ilma-access.log
```

### Accéder au shell d'un container

```bash
# Backend Python
docker compose -f docker-compose.prod.yml exec api bash

# PostgreSQL
docker compose -f docker-compose.prod.yml exec db psql -U ilma_user ilma_db

# Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli
```

### Vérifier l'espace disque

```bash
df -h
docker system df
```

### Nettoyer les images Docker inutilisées

```bash
docker system prune -af --volumes
```

### Vérifier SELinux si un problème survient

```bash
# Voir les derniers refus SELinux
sudo ausearch -m avc -ts recent

# Générer une règle pour autoriser une action bloquée
sudo ausearch -m avc -ts recent | audit2allow -M ilma-fix
sudo semodule -i ilma-fix.pp
```

---

## Récapitulatif de l'architecture

```
Internet
   │
   ▼
┌──────────────────────────────────────────────┐
│  Caddy (port 443, HTTPS auto Let's Encrypt)  │
│  ┌─ ilma.app → reverse proxy → :3080        │
└──┬───────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────┐
│  Docker Compose                               │
│                                               │
│  ┌─────────────┐     ┌─────────────────────┐ │
│  │  frontend    │────▶│  api (FastAPI x4)    │ │
│  │  Nginx :3080 │     │  :8000              │ │
│  │  (SPA + proxy│     │                     │ │
│  │   /api → api)│     │  ┌───┐  ┌───────┐  │ │
│  └─────────────┘     │  │ PG │  │ Redis  │  │ │
│                       │  │5432│  │ 6379   │  │ │
│                       │  └───┘  └───────┘  │ │
│                       │                     │ │
│                       │  ┌───────────────┐  │ │
│                       │  │ Minio (S3)    │  │ │
│                       │  │ 9000          │  │ │
│                       │  └───────────────┘  │ │
│                       └─────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## Checklist post-déploiement

- [ ] `https://ilma.app` charge le SPA
- [ ] `https://ilma.app/api/v1/health` retourne `{"success": true}`
- [ ] Inscription fonctionne (créer un compte test)
- [ ] Login fonctionne
- [ ] Le service worker s'installe (DevTools > Application)
- [ ] Le manifest PWA est détecté (invite d'installation sur mobile)
- [ ] Le compte admin peut accéder à `/admin`
- [ ] Les backups quotidiens s'exécutent (`sudo systemctl status ilma-backup.timer`)
- [ ] Sentry capte les erreurs (provoquer une erreur test)
- [ ] UptimeRobot envoie des alertes
- [ ] Le certificat HTTPS est valide (vérifier dans le navigateur)
- [ ] SSH par mot de passe est désactivé
- [ ] Seuls les ports 22, 80, 443 sont ouverts (`sudo firewall-cmd --list-all`)
- [ ] SELinux est en mode `Enforcing` (`getenforce`)
- [ ] Fail2ban protège SSH (`sudo fail2ban-client status sshd`)
- [ ] Mises à jour auto de sécurité activées (`sudo systemctl status dnf-automatic.timer`)
