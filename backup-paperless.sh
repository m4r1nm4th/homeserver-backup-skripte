#!/bin/bash

set -euo pipefail
# === CONFIGURATION ===
export RESTIC_REPOSITORY="/mnt/backup/restic"
export RESTIC_PASSWORD_FILE=/.restic-password

# Paperless
paperless_temp=/tmp/paperless
mkdir -p $paperless_temp
paperless_backup_dir="/mnt/backup/restic/paperless"
mkdir -p $paperless_backup_dir
docker exec paperless-stack-db-1 pg_dump --clean --if-exists --username=paperless paperless > $paperless_temp/paperless-db.sql
# Paperless export
docker exec -t paperless-stack-webserver-1 document_exporter ../export
rsync -aavx /home/marin/shared/media/paperless/export/* "$paperless_backup_dir"
rsync -aavx $paperless_temp/* $paperless_backup_dir
# clean
rm -rf $paperless_temp

# Restic backup
restic backup $paperless_backup_dir --tag paperless
restic forget --path=$paperless_backup_dir --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
