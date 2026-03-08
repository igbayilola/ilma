#!/usr/bin/env bash
# ILMA Database Backup Script
# Usage: ./backup.sh [daily|weekly]
# Crontab example:
#   0 2 * * * /opt/ilma/deploy/backup.sh daily
#   0 3 * * 0 /opt/ilma/deploy/backup.sh weekly

set -euo pipefail

BACKUP_TYPE="${1:-daily}"
BACKUP_DIR="/var/backups/ilma"
DATE=$(date +%Y%m%d_%H%M%S)
DB_CONTAINER="ilma-db"
DB_NAME="ilma_db"
DB_USER="ilma_user"
RETENTION_DAILY=7
RETENTION_WEEKLY=30

mkdir -p "$BACKUP_DIR/$BACKUP_TYPE"

FILENAME="$BACKUP_DIR/$BACKUP_TYPE/ilma_${BACKUP_TYPE}_${DATE}.sql.gz"

echo "[$(date)] Starting $BACKUP_TYPE backup..."

docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$FILENAME"

echo "[$(date)] Backup created: $FILENAME ($(du -h "$FILENAME" | cut -f1))"

# Cleanup old backups
if [ "$BACKUP_TYPE" = "daily" ]; then
    find "$BACKUP_DIR/daily" -name "*.sql.gz" -mtime +$RETENTION_DAILY -delete
    echo "[$(date)] Cleaned up daily backups older than $RETENTION_DAILY days"
elif [ "$BACKUP_TYPE" = "weekly" ]; then
    find "$BACKUP_DIR/weekly" -name "*.sql.gz" -mtime +$RETENTION_WEEKLY -delete
    echo "[$(date)] Cleaned up weekly backups older than $RETENTION_WEEKLY days"
fi

echo "[$(date)] Backup complete."
